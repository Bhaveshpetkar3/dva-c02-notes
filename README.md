# AWS DVA-C02 Notes

My Notion study notes, exported to Markdown and published with MkDocs Material.

## Refreshing from Notion

1. Put `NOTION_TOKEN=...` in `.env` (never committed).
2. `python scripts/export_notion.py 24dc6f8b930c8002bcc1f3d521656c5b`
3. Commit and push; GitHub Actions rebuilds the site.

Preview locally with `pip install -r requirements.txt` then `mkdocs serve`.
