"""MkDocs hook: fill the home page's stats grid and module table at build time.

docs/index.md holds two placeholders, <!-- home:stats --> and <!-- home:modules -->.
Every section page listed in mkdocs.yml's nav (except Home) counts as a module;
lectures are `## Lecture N:` headings and diagrams are ```mermaid fences.
"""

import os
import re

LECTURE = re.compile(r"^## Lecture\b", re.M)
DIAGRAM = re.compile(r"^\s*```mermaid", re.M)


def _modules(config):
    for entry in config["nav"] or []:
        if isinstance(entry, dict):
            (title, path), = entry.items()
            if isinstance(path, str) and path != "index.md":
                yield title, path


def on_page_markdown(markdown, page, config, files):
    if page.file.src_uri != "index.md":
        return markdown

    rows, lectures, diagrams = [], 0, 0
    for i, (title, path) in enumerate(_modules(config), 1):
        with open(os.path.join(config["docs_dir"], path), encoding="utf-8") as f:
            text = f.read()
        n_lec, n_dia = len(LECTURE.findall(text)), len(DIAGRAM.findall(text))
        lectures, diagrams = lectures + n_lec, diagrams + n_dia
        rows.append(f"| {i:02d} | [{title}]({path}) | {n_lec or '—'} | {n_dia or '—'} |")

    stats = [
        ("Modules", len(rows), "Course sections covered"),
        ("Lectures", lectures, "Lectures with notes"),
        ("Diagrams", diagrams, "Architecture and flow diagrams"),
        ("Exam", "DVA-C02", "AWS Certified Developer – Associate"),
    ]
    grid = ['<div class="stats-grid">'] + [
        f'<div class="stat-box"><div class="stat-label">{label}</div>'
        f'<div class="stat-value">{value}</div><div class="stat-desc">{desc}</div></div>'
        for label, value, desc in stats
    ] + ["</div>"]
    table = ["| # | Module | Lectures | Diagrams |", "| --- | --- | --- | --- |"] + rows

    return (markdown
            .replace("<!-- home:stats -->", "\n".join(grid))
            .replace("<!-- home:modules -->", "\n".join(table)))
