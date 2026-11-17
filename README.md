# Creator Kit

Branded, phone-first guide pages for creators. Each reel or post gets one page with the tools, links and
commands people can open and copy. Send the page link in your DMs instead of a wall of text.

- `guides/*.json` : one file per guide (title, intro, tools with links and copy-able commands, steps, sources)
- `themes/*.json` : the look (colours, fonts, mascot, handle)
- `build.py`      : turns guides into a static site in `dist/` (Python, no dependencies)
- `.github/workflows/pages.yml` : on every push, builds and publishes to GitHub Pages

Add a guide: copy `guides/agents.json`, change the text, push. The page appears at `/<slug>/`.
Build locally: `python build.py`, then open `dist/index.html`.

Made by The Human Edge (@thehumanedge.ai).
