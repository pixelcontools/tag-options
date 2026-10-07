"""Preview banner PNGs the way a human reviews them: magnified, on light and dark backgrounds.

    python tools/art/preview.py out.png banner1.png [banner2.png ...] [--zoom 3]

Writes one image: each banner on #EBEDEF (top) and near-black (bottom), nearest-neighbour upscaled.
Open it (Read tool / image viewer) and judge legibility of the lettering on both backgrounds.
"""
import sys
from PIL import Image

args = [a for a in sys.argv[1:] if not a.startswith('--')]
zoom = int(sys.argv[sys.argv.index('--zoom') + 1]) if '--zoom' in sys.argv else 3
if '--zoom' in sys.argv:
    args.remove(sys.argv[sys.argv.index('--zoom') + 1])
out, files = args[0], args[1:]
ims = [Image.open(f).convert('RGBA') for f in files]
w = max(i.width for i in ims) + 20
h = sum(i.height + 20 for i in ims) * 2
sheet = Image.new('RGBA', (w, h), (235, 237, 239, 255))
y = 0
for bg in ((235, 237, 239, 255), (11, 11, 15, 255)):
    for im in ims:
        cell = Image.new('RGBA', (w, im.height + 20), bg)
        cell.alpha_composite(im, (10, 10))
        sheet.alpha_composite(cell, (0, y))
        y += im.height + 20
sheet.convert('RGB').resize((sheet.width * zoom, sheet.height * zoom), Image.NEAREST).save(out)
print('wrote', out, sheet.width * zoom, 'x', sheet.height * zoom)
