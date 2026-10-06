# tag-options

Animated guild-tag options for the PIXELCONS guild on [geopixels.net](https://geopixels.net).

- **Live page:** `docs/index.html` (served by GitHub Pages from `/docs`). Pick a tag, optionally include the Roll image, click a tag to copy its HTML.
- **Tag files:** `docs/tags/plain/` (tag only) and `docs/tags/with-roll/` (tag + Roll, 84 px tall; Roll is an embedded PNG, about 21 KB of HTML). `docs/tags/roll.html` is the Roll piece on its own.
- **Rebuild the page:** `python tools/build.py` (reads `docs/tags/`, writes `docs/index.html`).

Tags use only inline SVG animation and the site's built-in `maplibregl-user-location-dot-pulse` keyframes: no `<script>`, no `<style>`.
