"""Check note pages for Markdown that breaks on this site, then validate Mermaid.

Usage: python scripts/check_notes.py [docs/page.md ...]   (default: every section page)

Notion tolerates things Python-Markdown does not, so this catches them before
publishing. Mermaid errors only appear in the browser, so every diagram is
parsed with the site's own mermaid.min.js in headless Edge. Exit code 1 on errors.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
MERMAID_JS = os.path.join(DOCS, "js", "mermaid.min.js")
EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

FENCE = re.compile(r"^(\s*)(`{3,})(.*)$")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+\.)\s")
LECTURE = re.compile(r"^## Lecture (\d+): \S")
INLINE_CODE = re.compile(r"(`+).+?\1")
RAW_TAG = re.compile(r"</?[A-Za-z][\w:-]*(\s[^>]*)?/?>")
ALLOWED_TAGS = {"br", "p", "div", "span", "sub", "sup", "kbd", "mark", "details", "summary"}
FORWARD_LOOKING = re.compile(r"^#+ .*\b(coming next|up next|what's next|next lecture)\b", re.I)


def lint(path):
    errors, warnings, diagrams, lectures = [], [], [], []
    lines = open(path, encoding="utf-8").read().split("\n")
    in_fence, fence_len, fence_start, fence_lang, block = False, 0, 0, "", []
    prev = ""
    for n, line in enumerate(lines, 1):
        m = FENCE.match(line)
        if in_fence:
            if m and len(m.group(2)) >= fence_len and not m.group(3).strip():
                in_fence = False
                if fence_lang == "mermaid":
                    diagrams.append((fence_start, "\n".join(block)))
            else:
                block.append(line)
            prev = line
            continue
        if m:
            in_fence, fence_len, fence_start, block = True, len(m.group(2)), n, []
            fence_lang = m.group(3).strip().lower()
            if not fence_lang:
                warnings.append(f"{n}: code block has no language tag")
            elif fence_lang in ("python", "py", "java"):
                warnings.append(f"{n}: {fence_lang} code block (application code should be javascript)")
            prev = line
            continue

        where = f"{n}:"
        if line.startswith("# ") and n > 1:
            errors.append(f"{where} extra H1; only the page title may be '# ' (lectures are '## Lecture N: ...')")
        if line.startswith("## Lecture"):
            lm = LECTURE.match(line)
            if lm:
                lectures.append((int(lm.group(1)), n))
            else:
                errors.append(f"{where} lecture heading must look like '## Lecture N: <emoji> Title'")
        if FORWARD_LOOKING.match(line):
            errors.append(f"{where} forward-looking section ('what's coming next') is not allowed")

        lm = LIST_ITEM.match(line)
        if lm:
            indent = len(lm.group(1).expandtabs(4))
            if indent % 4:
                errors.append(f"{where} list item indented {indent} spaces; nested lists need multiples of 4")
            if prev.strip() and not LIST_ITEM.match(prev) and not prev.startswith(("#", ">")) \
                    and not prev.startswith(" ") and indent == 0:
                errors.append(f"{where} list starts right after a paragraph; add a blank line before it")

        stripped = INLINE_CODE.sub("", line)
        for tag in RAW_TAG.finditer(stripped):
            name = re.match(r"</?([A-Za-z][\w:-]*)", tag.group(0)).group(1).lower()
            if name not in ALLOWED_TAGS:
                errors.append(f"{where} '{tag.group(0)}' would be swallowed as HTML; wrap it in backticks")
        prev = line

    if in_fence:
        errors.append(f"{fence_start}: code block is never closed")

    seen = {}
    for num, n in lectures:
        if num in seen:
            errors.append(f"{n}: Lecture {num} appears twice (also line {seen[num]})")
        seen[num] = n
    nums = [num for num, _ in lectures]
    if nums != sorted(nums):
        errors.append(f"lectures are out of order: {nums}")

    # Each lecture should close with a single '---' before the next one.
    for i, (num, n) in enumerate(lectures):
        end = lectures[i + 1][1] - 1 if i + 1 < len(lectures) else len(lines)
        tail = [l for l in lines[n:end] if l.strip()]
        if not tail or tail[-1].strip() != "---":
            warnings.append(f"{n}: Lecture {num} does not end with a '---' divider")
    return errors, warnings, diagrams, [num for num, _ in lectures]


def check_mermaid(diagrams):
    """diagrams: list of (label, code). Returns {label: error message} for failures."""
    if not diagrams:
        return {}
    edge = next((p for p in EDGE_PATHS if os.path.exists(p)), None)
    if not edge:
        print("warning: Microsoft Edge not found; Mermaid diagrams were NOT validated")
        return {}
    tmp = tempfile.mkdtemp(prefix="mermaid-check-")
    try:
        shutil.copy(MERMAID_JS, os.path.join(tmp, "mermaid.min.js"))
        payload = json.dumps([code for _, code in diagrams])
        html = f"""<!doctype html><html><body><pre id="out">pending</pre>
<script src="mermaid.min.js"></script>
<script>
mermaid.initialize({{ startOnLoad: false }});
const diagrams = {payload};
(async () => {{
  const results = [];
  for (const d of diagrams) {{
    try {{ await mermaid.parse(d); results.push(null); }}
    catch (e) {{ results.push(String(e && e.message || e).slice(0, 400)); }}
  }}
  document.getElementById("out").textContent = "RESULTS:" + JSON.stringify(results);
}})();
</script></body></html>"""
        page = os.path.join(tmp, "check.html")
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)
        out = subprocess.run(
            [edge, "--headless=new", "--disable-gpu", f"--user-data-dir={os.path.join(tmp, 'profile')}",
             "--virtual-time-budget=30000", "--dump-dom", "file:///" + page.replace("\\", "/")],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180).stdout
        m = re.search(r"RESULTS:(\[.*?\])</pre>", out, re.S)
        if not m:
            print("warning: could not read Mermaid results from Edge; diagrams were NOT validated")
            return {}
        import html as htmllib
        results = json.loads(htmllib.unescape(m.group(1)))
        return {label: err for (label, _), err in zip(diagrams, results) if err}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    paths = sys.argv[1:] or sorted(p for p in glob.glob(os.path.join(DOCS, "*.md"))
                                   if os.path.basename(p) != "index.md")
    total_err, all_diagrams, owners = 0, [], {}
    for path in paths:
        rel = os.path.relpath(path, ROOT)
        errors, warnings, diagrams, lectures = lint(path)
        for num in lectures:
            if num in owners and owners[num] != rel:
                errors.append(f"Lecture {num} is also in {owners[num]}")
            owners[num] = rel
        for e in errors:
            print(f"ERROR   {rel}:{e}")
        for w in warnings:
            print(f"warning {rel}:{w}")
        total_err += len(errors)
        all_diagrams += [(f"{rel}:{line}", code) for line, code in diagrams]

    failures = check_mermaid(all_diagrams)
    for label, err in failures.items():
        print(f"ERROR   {label}: Mermaid syntax error: {err.splitlines()[0] if err else err}")
    total_err += len(failures)

    print(f"checked {len(paths)} page(s), {len(all_diagrams)} diagram(s): "
          f"{'OK' if not total_err else f'{total_err} error(s)'}")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
