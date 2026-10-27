# AWS DVA-C02 Notes

Revision notes for the AWS Certified Developer – Associate exam, published with MkDocs Material.

The notes were exported once from Notion; this repo is now the source of truth. New lectures are written by the `dva-notes` Claude agent (`C:\Users\atlog\Desktop\aws\.claude\agents\dva-notes.md`).

- `docs/<section>.md` — one page per course section; lectures are `## Lecture N: ...` blocks.
- `mkdocs.yml` — site config and sidebar order (`nav:`).
- `hooks/home.py` — fills the home page's stats and module table at build time.
- `scripts/check_notes.py` — Markdown lint + Mermaid validation; run before publishing.

Preview locally with `pip install -r requirements.txt` then `mkdocs serve`.
