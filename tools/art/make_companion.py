"""Turn an image into a "companion image": an <img> with an embedded PNG that sits to the right of any guild tag.

    python tools/art/make_companion.py IMAGE --id devil --name "Devil girl" [--height 84] [--max-chars 60000]
                                       [--trim-bg] [--alpha-cut 64] [--preview out.png]

What it does
  1. crops the transparent margin, scales to --height (default 84, the height of every tag), keeps the aspect ratio
  2. encodes a PNG data URI at 256 colours (near-lossless for pixel/illustration art and usually 3-4x smaller than full
     colour); if the HTML is over --max-chars it steps down 128 -> 64 -> 32 colours at that height, then shrinks the
     height by 8 px and tries again (height is the last thing to give; the floor is 32 px).
     --lossless starts from full colour instead (how Roll was made; use for soft photographic art, costs size)
  3. writes docs/tags/companions/<id>.html and registers it in docs/tags/companions/companions.json
  4. reports what was chosen and how the biggest existing tag + this companion compares with the largest tag known to be
     accepted by geopixels.net (gycra's, 211,642 characters)
After this run `python tools/build.py` so the page and the with-<id>/ folders pick it up.

Why a data-URI PNG: geopixels.net's CSP allows `data:` images (and catbox.moe/imgur.com), nothing else. See the skill.
"""
import argparse, base64, io, json, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP_DIR = os.path.join(ROOT, 'docs', 'tags', 'companions')
PLAIN_DIR = os.path.join(ROOT, 'docs', 'tags', 'plain')
GYCRA = 211_642


def prepare(src, trim_bg, alpha_cut):
    im = Image.open(src).convert('RGBA')
    if trim_bg:                                   # opaque image on a flat background: make that colour transparent
        bg = im.getpixel((0, 0))
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                c = px[x, y]
                if all(abs(c[k] - bg[k]) <= 12 for k in range(3)):
                    px[x, y] = (c[0], c[1], c[2], 0)
    box = im.getchannel('A').getbbox()
    if not box:
        sys.exit('image is fully transparent')
    return im.crop(box)


def encode(im, height, colors, alpha_cut):
    w = max(1, round(im.width * height / im.height))
    r = im.resize((w, height), Image.LANCZOS)
    r.putalpha(r.getchannel('A').point(lambda v: 0 if v < alpha_cut else v))   # drop the near-transparent fringe
    if colors:
        r = r.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    buf = io.BytesIO()
    r.save(buf, 'PNG', optimize=True)
    html = ('<img src="data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode() +
            f'" width="{w}" height="{height}" style="display: block; image-rendering: pixelated" alt="">')
    return html, w, buf.getvalue()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('image')
    ap.add_argument('--id', required=True, help='short id: letters, digits, - or _ (used in file names)')
    ap.add_argument('--name', help='label shown in the gallery dropdown (default: the id)')
    ap.add_argument('--height', type=int, default=84)
    ap.add_argument('--max-chars', type=int, default=60_000, help='budget for the companion HTML alone (default 60000)')
    ap.add_argument('--alpha-cut', type=int, default=64)
    ap.add_argument('--lossless', action='store_true', help='start from full colour instead of 256 colours')
    ap.add_argument('--trim-bg', action='store_true', help='treat the top-left colour as a transparent background')
    ap.add_argument('--preview', help='also write the final bitmap, 4x on light grey, to this PNG')
    a = ap.parse_args()
    if not re.fullmatch(r'[a-z0-9_-]+', a.id):
        sys.exit('--id must be lowercase letters, digits, - or _')

    im = prepare(a.image, a.trim_bg, a.alpha_cut)
    best = None
    height = a.height
    while height >= 32 and best is None:
        for colors in ((None, 256, 128, 64, 32) if a.lossless else (256, 128, 64, 32)):
            html, w, png = encode(im, height, colors, a.alpha_cut)
            if len(html) <= a.max_chars:
                best = (html, w, height, colors, png)
                break
        else:
            height -= 8
    if best is None:
        sys.exit(f'could not fit in {a.max_chars} chars even at 32 px / 32 colours; raise --max-chars or use simpler art')
    html, w, height, colors, png = best

    os.makedirs(COMP_DIR, exist_ok=True)
    with open(os.path.join(COMP_DIR, a.id + '.html'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    idx_path = os.path.join(COMP_DIR, 'companions.json')
    idx = json.load(open(idx_path, encoding='utf-8')) if os.path.exists(idx_path) else []
    idx = [c for c in idx if c['id'] != a.id]
    idx.append({'id': a.id, 'name': a.name or a.id, 'file': a.id + '.html', 'w': w, 'h': height, 'chars': len(html)})
    idx.sort(key=lambda c: (c['id'] != 'roll', c['name'].lower()))             # Roll stays first
    with open(idx_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(idx, f, indent=1, ensure_ascii=False)

    biggest = max((len(open(os.path.join(PLAIN_DIR, p), encoding='utf-8').read()) for p in os.listdir(PLAIN_DIR)), default=0)
    total = biggest + len(html) + 200                                          # + the flex wrapper
    print(f'{a.id}: {w}x{height}px, {"full colour" if colors is None else str(colors) + " colours"}, '
          f'PNG {len(png):,} bytes, HTML {len(html):,} chars (budget {a.max_chars:,})')
    if height != a.height:
        print(f'  note: shrunk from {a.height} to {height} px to fit the budget; it will sit shorter than the tag')
    print(f'  biggest tag today {biggest:,} + this companion = about {total:,} chars = {total / GYCRA:.0%} of the largest known-accepted tag ({GYCRA:,})')
    if total > GYCRA * 0.5:
        print('  WARNING: above half of the largest tag known to be accepted; shrink it (lower --max-chars) or simplify the art')
    if a.preview:
        pv = Image.open(io.BytesIO(png)).convert('RGBA')
        sheet = Image.new('RGBA', (pv.width + 16, pv.height + 16), (235, 237, 239, 255))
        sheet.alpha_composite(pv, (8, 8))
        sheet.convert('RGB').resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(a.preview)
        print('  preview:', a.preview)
    print('next: python tools/build.py')


if __name__ == '__main__':
    main()
