# tag-options

Gallery of guild-tag options for geopixels.net (GitHub Pages from `docs/`).

**To make, change or remove a tag option, read `.github/skills/new-guild-tag/SKILL.md` first.** It has the site's constraints
(CSP allows `data:` images only, no `<style>`/`<script>`, size evidence), the house style, the generator commands and the pitfalls.

Quick rules:
- `docs/index.html` is generated: edit `tools/index.template.html` / `tools/build.py`, then run `python tools/build.py`.
- Options keep their numbers; never renumber.
- Windows PowerShell 5.1: no `&&`; no double quotes inside commit messages.
- Commit regenerated `docs/index.html` together with `docs/tags/` changes; push to `main` (Pages rebuilds in about a minute).
