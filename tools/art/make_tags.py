"""Build tag HTML for the PNG scenes with and without the heart pair (none / pair) and update docs/tags (plain/ + manifest.json).
The with-<companion>/ folders are produced by `python tools/build.py`.

    python make_tags.py <scenes_dir> <repo_root>
"""
import base64, json, os, random, re, sys

P = 'maplibregl-user-location-dot-pulse'
GOLD, BLUE = '#ffca3a', '#1982c4'
YEL, BLU = '\U0001f49b', '\U0001f499'
PAD_Y, PAD_X = 0, 26                    # side padding leaves room for the two hearts beside the banner
BW, BH = 280, 84
LEVELS = {'none': 0, 'pair': 2}

SCENES = [
    # file, number, name, description, lettering band (banner y0, y1)
    ('night.png', 24, 'Pixel Night', 'The skyline after dark: crescent moon, shooting star, glowing wordmark and lit windows.', (27, 52)),
    ('arcade.png', 25, 'Pixel Arcade', 'Retro synthwave: striped sun, neon grid floor, scanlines and a pink-glow wordmark.', (13, 38)),
    ('space.png', 26, 'Pixel Space', 'A starfield with nebula clouds, a ringed gold planet and a blue moon behind the wordmark.', (27, 52)),
    ('citypop.png', 28, 'Pixel City Pop', 'Retro Japan, 80s city pop: a white Countach cruises an elevated road above a pastel Tokyo skyline with street lights and a bus stop, toward a sign with a heart-shaped sobbing face and an arrow. Katakana (ピクセルコンズ) runs down the side.', (12, 37)),
    ('citypop2.png', 29, 'Pixel City Pop: Gold to Blue', 'City Pop again, but the whole scene follows the guild gradient: golden hour on the left cooling to blue on the right, down to the skyline, road tint and lamp glow.', (12, 37)),
    ('sky.png', 27, 'Pixel Sky', 'Bright sky islands with trees, a little red-roofed house and drifting clouds.', (25, 50)),
]


def heart(emo, col, size, dur, delay, pos):
    return (f'<span style="position: absolute; {pos}; font-size: {size}px; line-height: 1; filter: drop-shadow(0 0 {max(3, size // 4)}px {col}); '
            f'animation: {dur}s linear {delay}s infinite {P}">{emo}</span>')


def hearts(count, band, seed):
    """none -> nothing; pair -> one yellow heart left and one blue heart right of the banner, centred vertically.
    They render on top of the banner (z-index 2 vs 1)."""
    if count == 0:
        return ''
    mid = PAD_Y + BH // 2 - 12
    return (heart(YEL, GOLD, 24, 2.0, -2.0, f'left: 2px; top: {mid}px; z-index: 2') +
            heart(BLU, BLUE, 24, 2.0, -1.0, f'right: 2px; top: {mid}px; z-index: 2'))


def sparkle(x, y, dur, dl):
    return (f'<span style="position: absolute; left: {x}px; top: {y}px; width: 1px; height: 1px; background: #fff; '
            f'box-shadow: 0 -1px #fff, 0 1px #fff, -1px 0 #fff, 1px 0 #fff; animation: {dur}s ease-out {dl}s infinite {P}"></span>')


def build(png_bytes, count, band, seed):
    img = ('<img src="data:image/png;base64,' + base64.b64encode(png_bytes).decode() +
           f'" width="{BW}" height="{BH}" style="display: block; position: relative; z-index: 1; image-rendering: pixelated" alt="">')
    if count == 0:
        return ('<span style="position: relative; display: inline-block; width: 280px; height: 84px">' + img +
                sparkle(90, 12, 2.6, -0.4) + sparkle(171, 70, 3.1, -1.7) + sparkle(246, 22, 2.8, -1.1) + '</span>')
    return (f'<span style="position: relative; display: inline-block; padding: {PAD_Y}px {PAD_X}px">' + img +
            sparkle(PAD_X + 90, PAD_Y + 10, 2.6, -0.4) + sparkle(PAD_X + 171, PAD_Y + 70, 3.1, -1.7) + sparkle(PAD_X + 246, PAD_Y + 20, 2.8, -1.1) +
            hearts(count, band, seed) + '</span>')


def main(scenes_dir, root):
    tags = os.path.join(root, 'docs', 'tags')
    man = json.load(open(os.path.join(tags, 'manifest.json'), encoding='utf-8'))
    man = [m for m in man if m['n'] not in {s[1] for s in SCENES}]
    for fname, n, name, desc, band in SCENES:
        png = open(os.path.join(scenes_dir, fname), 'rb').read()
        slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')      # no colons etc. in file names
        for stale in ('few', 'many'):                                    # older heart-count variants
            p = os.path.join(tags, 'plain', f'{n:02d}_{slug}_hearts_{stale}.html')
            if os.path.exists(p):
                os.remove(p)
        files = {}
        for lvl, count in LEVELS.items():
            html = build(png, count, band, n * 31)
            f = f'{n:02d}_{slug}_hearts_{lvl}.html'
            with open(os.path.join(tags, 'plain', f), 'w', encoding='utf-8', newline=chr(10)) as fh:
                fh.write(html)
            files[lvl] = f
            print(f'{name:30} {lvl:5} {len(html):6} chars')
        man.append({'n': n, 'name': name, 'desc': desc, 'levels': files})
    json.dump(man, open(os.path.join(tags, 'manifest.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('next: python tools/build.py   (writes the page and the with-<companion>/ folders)')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
