"""Export a Notion page tree to Markdown for MkDocs.

Usage: python scripts/export_notion.py <root-page-id>
Reads NOTION_TOKEN from the environment or from .env in the project root.
Writes Markdown into docs/, images into docs/assets/, and the nav into mkdocs.yml.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
ASSETS = os.path.join(DOCS, "assets")
API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def load_token():
    token = os.environ.get("NOTION_TOKEN")
    env_path = os.path.join(ROOT, ".env")
    if not token and os.path.exists(env_path):
        with open(env_path, encoding="utf-8-sig") as f:
            for line in f:
                key, _, value = line.strip().partition("=")
                if key.strip() == "NOTION_TOKEN":
                    token = value.strip().strip('"').strip("'")
    if not token:
        sys.exit("NOTION_TOKEN not found in environment or .env")
    return token


TOKEN = load_token()


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(6):
        req = urllib.request.Request(API + path, data=data, method=method, headers={
            "Authorization": f"Bearer {TOKEN}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(float(e.headers.get("Retry-After", 2 ** attempt)))
                continue
            raise RuntimeError(f"{method} {path} -> {e.code}: {e.read().decode(errors='replace')}")
        except urllib.error.URLError:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"{method} {path} failed after retries")


def paginate(method, path, body=None):
    cursor = None
    while True:
        if method == "GET":
            sep = "&" if "?" in path else "?"
            url = path + sep + "page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
            res = api("GET", url)
        else:
            payload = dict(body or {}, page_size=100)
            if cursor:
                payload["start_cursor"] = cursor
            res = api("POST", path, payload)
        yield from res["results"]
        if not res.get("has_more"):
            return
        cursor = res["next_cursor"]


# ---------- fetching ----------

def page_title(page):
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            return "".join(t["plain_text"] for t in prop["title"]).strip()
    return ""


def make_node(node_id, title, kind):
    return {"id": node_id.replace("-", ""), "title": title or "Untitled", "kind": kind,
            "blocks": [], "children": []}


def fetch_children(block_id, node):
    """Fetch the blocks under block_id, recursing into nested blocks and subpages."""
    blocks = []
    for b in paginate("GET", f"/blocks/{block_id}/children"):
        t = b["type"]
        if t == "child_page":
            child = make_node(b["id"], b["child_page"]["title"], "page")
            print(f"  page: {child['title']}")
            child["blocks"] = fetch_children(b["id"], child)
            node["children"].append(child)
            b["_node"] = child
        elif t == "child_database":
            child = fetch_database(b["id"], b["child_database"]["title"])
            if child:
                node["children"].append(child)
                b["_node"] = child
        elif t == "synced_block" and b["synced_block"].get("synced_from"):
            src = b["synced_block"]["synced_from"]["block_id"]
            try:
                b["_children"] = fetch_children(src, node)
            except RuntimeError as e:
                print(f"  warning: synced block {src} not accessible ({e.args[0][:80]})")
                b["_children"] = []
        elif b.get("has_children"):
            b["_children"] = fetch_children(b["id"], node)
        blocks.append(b)
    return blocks


def fetch_database(db_id, title):
    print(f"  database: {title}")
    node = make_node(db_id, title, "database")
    try:
        rows = list(paginate("POST", f"/databases/{db_id}/query"))
    except RuntimeError as e:
        print(f"  warning: database {title!r} not accessible ({e.args[0][:80]})")
        return None
    for row in rows:
        child = make_node(row["id"], page_title(row), "page")
        print(f"    row: {child['title']}")
        child["blocks"] = fetch_children(row["id"], child)
        node["children"].append(child)
    return node


# ---------- paths ----------

def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60].strip("-")


PATHS = {}  # node id -> docs-relative posix path of its markdown file


def assign_paths(node, folder, is_root=False):
    if is_root:
        node["path"] = "index.md"
        child_folder = ""
    else:
        if node["children"]:
            node["path"] = f"{folder}{node['slug']}/index.md"
            child_folder = f"{folder}{node['slug']}/"
        else:
            node["path"] = f"{folder}{node['slug']}.md"
            child_folder = None
    PATHS[node["id"]] = node["path"]
    used = {"index", "assets"}
    for child in node["children"]:
        base = slugify(child["title"]) or child["id"][:8]
        slug, n = base, 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)
        child["slug"] = slug
        assign_paths(child, child_folder)


def rel_link(from_path, to_path):
    return os.path.relpath(to_path, os.path.dirname(from_path) or ".").replace("\\", "/")


# ---------- rendering ----------

def escape(text):
    text = text.replace("\\", "\\\\")
    text = re.sub(r"([*_`\[\]|])", r"\\\1", text)
    return text.replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, marker):
    """Apply an inline marker, keeping surrounding whitespace outside it."""
    m = re.match(r"^(\s*)(.*?)(\s*)$", text, re.S)
    lead, core, trail = m.groups()
    return f"{lead}{marker}{core}{marker}{trail}" if core else text


def rich(rts, cur_path):
    out = []
    for rt in rts:
        ann = rt.get("annotations", {})
        href = rt.get("href")
        if rt["type"] == "mention":
            m = rt["mention"]
            target = (m.get("page") or {}).get("id", "").replace("-", "")
            if target in PATHS:
                href = rel_link(cur_path, PATHS[target])
        pieces = []
        for line in rt["plain_text"].split("\n"):
            if rt["type"] == "equation" or ann.get("code"):
                piece = f"`{line}`" if line.strip() else line
            else:
                piece = escape(line)
                if ann.get("bold"):
                    piece = wrap(piece, "**")
                if ann.get("italic"):
                    piece = wrap(piece, "*")
                if ann.get("strikethrough"):
                    piece = wrap(piece, "~~")
            pieces.append(piece)
        text = "<br>".join(pieces)
        if href and text.strip():
            if href.startswith("/"):
                pid = href.lstrip("/").split("#")[0].split("?")[0][-32:]
                href = rel_link(cur_path, PATHS[pid]) if pid in PATHS else "https://www.notion.so" + href
            text = f"[{text}]({href})"
        out.append(text)
    s = "".join(out)
    # A line starting with these would otherwise become a heading or list.
    return re.sub(r"^(\s*)(#|[-+] |\d+\. )", r"\1\\\2", s)


def plain(rts):
    return "".join(t["plain_text"] for t in rts)


def indent(lines, prefix="    "):
    return [prefix + l if l else "" for l in lines]


LANG_MAP = {"plain text": "text", "shell": "bash", "c#": "csharp", "c++": "cpp",
            "f#": "fsharp", "objective-c": "objectivec", "markdown": "md"}


def download(url, node_id, block_id):
    os.makedirs(ASSETS, exist_ok=True)
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower() or ".png"
    name = f"{node_id[:8]}-{block_id.replace('-', '')[:12]}{ext}"
    dest = os.path.join(ASSETS, name)
    if not os.path.exists(dest):
        # No auth header: these are pre-signed storage URLs.
        req = urllib.request.Request(url, headers={"User-Agent": "notion-export"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
                    f.write(resp.read())
                break
            except Exception as e:
                if attempt == 3:
                    print(f"  warning: could not download {url[:80]} ({e})")
                    return None
                time.sleep(2 ** attempt)
    return f"assets/{name}"


def file_target(block, node, cur_path):
    data = block[block["type"]]
    if data.get("type") == "file":
        local = download(data["file"]["url"], node["id"], block["id"])
        return rel_link(cur_path, local) if local else None
    return data.get(data.get("type"), {}).get("url")


LIST_TYPES = {"bulleted_list_item", "numbered_list_item", "to_do"}


def render_blocks(blocks, node, cur_path):
    lines = []
    prev = None
    for b in blocks:
        out = render_block(b, node, cur_path)
        if not out:
            continue
        tight = prev in LIST_TYPES and b["type"] == prev
        if lines and not tight:
            lines.append("")
        lines.extend(out)
        prev = b["type"]
    return lines


def render_block(b, node, cur_path):
    t = b["type"]
    data = b.get(t, {})
    kids = b.get("_children", [])
    sub = lambda: render_blocks(kids, node, cur_path)
    text = lambda: rich(data.get("rich_text", []), cur_path)

    if t == "paragraph":
        out = [text()] if plain(data["rich_text"]).strip() else []
        return out + ([""] + sub() if kids else [])
    if t in ("heading_1", "heading_2", "heading_3", "heading_4"):
        # Page title is the H1, so shift Notion headings down one level.
        level = int(t[-1]) + 1
        return [f"{'#' * level} {text()}"] + ([""] + sub() if kids else [])
    if t in LIST_TYPES:
        marker = {"bulleted_list_item": "-", "numbered_list_item": "1.",
                  "to_do": "- [x]" if data.get("checked") else "- [ ]"}[t]
        out = [f"{marker} {text()}"]
        if kids:
            out += [""] + indent(sub())
        return out
    if t == "toggle":
        title = plain(data["rich_text"]).replace('"', "'").strip() or "Details"
        return [f'??? note "{title}"', ""] + indent(sub())
    if t == "callout":
        icon = (data.get("icon") or {}).get("emoji", "")
        body = [f"{icon} {text()}".strip()] + ([""] + sub() if kids else [])
        return ['!!! note ""', ""] + indent(body)
    if t == "quote":
        body = [text()] + ([""] + sub() if kids else [])
        return [("> " + l) if l else ">" for l in body]
    if t == "code":
        code = plain(data["rich_text"])
        lang = data.get("language", "text").lower()
        lang = LANG_MAP.get(lang, lang.replace(" ", ""))
        fence = "````" if "```" in code else "```"
        out = [f"{fence}{lang}", *code.split("\n"), fence]
        if data.get("caption"):
            out += ["", f"*{rich(data['caption'], cur_path)}*"]
        return out
    if t == "equation":
        return ["```text", data["expression"], "```"]
    if t == "divider":
        return ["---"]
    if t == "image":
        src = file_target(b, node, cur_path)
        if not src:
            return []
        cap = rich(data.get("caption", []), cur_path)
        alt = plain(data.get("caption", [])).replace("]", "") or "image"
        return [f"![{alt}]({src})"] + (["", f"*{cap}*"] if cap else [])
    if t in ("file", "pdf", "video", "audio"):
        src = file_target(b, node, cur_path)
        if not src:
            return []
        name = plain(data.get("caption", [])) or data.get("name") or f"{t} attachment"
        return [f"📎 [{escape(name)}]({src})"]
    if t in ("bookmark", "embed", "link_preview"):
        url = data.get("url")
        if not url:
            return []
        label = plain(data.get("caption", [])) or url
        return [f"🔗 [{escape(label)}]({url})"]
    if t == "table":
        rows = [r["table_row"]["cells"] for r in kids if r["type"] == "table_row"]
        if not rows:
            return []
        width = max(len(r) for r in rows)
        fmt = lambda cells: "| " + " | ".join(
            rich(c, cur_path) for c in cells + [[]] * (width - len(cells))) + " |"
        if data.get("has_column_header"):
            out = [fmt(rows[0]), "|" + " --- |" * width] + [fmt(r) for r in rows[1:]]
        else:
            out = ["|" + "   |" * width, "|" + " --- |" * width] + [fmt(r) for r in rows]
        return out
    if t in ("column_list", "column", "synced_block", "template"):
        return sub()
    if t in ("child_page", "child_database"):
        child = b.get("_node")
        if not child:
            return []
        icon = "🗂️" if child["kind"] == "database" else "📄"
        return [f"{icon} [{escape(child['title'])}]({rel_link(cur_path, child['path'])})"]
    if t == "link_to_page":
        pid = (data.get("page_id") or data.get("database_id") or "").replace("-", "")
        if pid in PATHS:
            return [f"➡️ [Linked page]({rel_link(cur_path, PATHS[pid])})"]
        return []
    if t in ("table_of_contents", "breadcrumb", "unsupported"):
        return []
    print(f"  note: skipped unsupported block type {t!r}")
    return []


def write_node(node):
    path = node["path"]
    lines = [f"# {escape(node['title'])}", ""]
    if node["kind"] == "database":
        lines += [f"- [{escape(c['title'])}]({rel_link(path, c['path'])})" for c in node["children"]]
    else:
        lines += render_blocks(node["blocks"], node, path)
    full = os.path.join(DOCS, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    for child in node["children"]:
        write_node(child)


def nav_entries(node):
    entries = []
    for child in node["children"]:
        title = json.dumps(child["title"], ensure_ascii=False)
        if child["children"]:
            entries.append({"title": title, "path": child["path"], "items": nav_entries(child)})
        else:
            entries.append({"title": title, "path": child["path"]})
    return entries


def nav_yaml(entries, depth=1):
    pad = "  " * depth
    out = []
    for e in entries:
        if "items" in e:
            out.append(f"{pad}- {e['title']}:")
            out.append(f"{pad}  - {e['path']}")
            out += nav_yaml(e["items"], depth + 1)
        else:
            out.append(f"{pad}- {e['title']}: {e['path']}")
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root_id = re.sub(r"[^0-9a-f]", "", sys.argv[1].lower())[-32:]
    root_page = api("GET", f"/pages/{root_id}")
    root = make_node(root_id, page_title(root_page), "page")
    print(f"root: {root['title']}")
    root["blocks"] = fetch_children(root_id, root)

    assign_paths(root, "", is_root=True)
    write_node(root)

    nav = ["INHERIT: mkdocs.base.yml", "nav:", f"  - Home: index.md"] + nav_yaml(nav_entries(root))
    with open(os.path.join(ROOT, "mkdocs.yml"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(nav) + "\n")
    print(f"done: {len(PATHS)} pages written to docs/")


if __name__ == "__main__":
    main()
