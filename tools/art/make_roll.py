"""Rebuild docs/tags/roll.html (the Roll image, 97x84, as an embedded PNG) from a source image.

    python tools/art/make_roll.py [source.png] [out.html]

Defaults: source D:\\wplace\\geopixels\\roll_gyate.png, out docs/tags/roll.html (relative to the repo root).
Every tag in the gallery appends this fragment inside a 97x84 box, so keep the size.
"""
import base64, io, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = sys.argv[1] if len(sys.argv) > 1 else r'D:\wplace\geopixels\roll_gyate.png'
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'docs', 'tags', 'roll.html')

im = Image.open(src).convert('RGBA')
im = im.crop(im.getchannel('A').getbbox())                       # trim the transparent margin
im = im.resize((97, round(im.height * 97 / im.width)), Image.LANCZOS)
assert im.size == (97, 84), f'expected 97x84, got {im.size}; crop or pick a different source'
im.putalpha(im.getchannel('A').point(lambda v: 0 if v < 64 else v))   # drop near-transparent fringe
buf = io.BytesIO()
im.save(buf, 'PNG', optimize=True)
html = ('<img src="data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode() +
        '" width="97" height="84" style="display: block; image-rendering: pixelated" alt="">')
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)
print(f'wrote {out}: {len(buf.getvalue())} PNG bytes, {len(html)} chars')
