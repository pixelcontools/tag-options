"""Build tag HTML for the PNG scenes at three heart levels (none / few / many) and update docs/tags.

    python make_tags.py <scenes_dir> <repo_root>
"""
import base64, json, os, random, sys

P = 'maplibregl-user-location-dot-pulse'
GOLD, BLUE = '#ffca3a', '#1982c4'
YEL, BLU = '\U0001f49b', '\U0001f499'
PAD_Y, PAD_X = 12, 26                   # wrapper padding that leaves room for hearts outside the banner
BW, BH = 280, 84
LEVELS = {'none': 0, 'few': 6, 'many': 16}

SCENES = [
    # file, number, name, description, lettering band (banner y0, y1)
    ('night.png', 24, 'Pixel Night', 'The skyline after dark: crescent moon, shooting star, glowing wordmark and lit windows.', (27, 52)),
    ('arcade.png', 25, 'Pixel Arcade', 'Retro synthwave: striped sun, neon grid floor, scanlines and a pink-glow wordmark.', (13, 38)),
    ('space.png', 26, 'Pixel Space', 'A starfield with nebula clouds, a ringed gold planet and a blue moon behind the wordmark.', (27, 52)),
    ('citypop.png', 28, 'Pixel City Pop', 'Retro Japan, 80s city pop: a white Countach cruises an elevated road above a pastel Tokyo skyline, toward a sign with a crying face and an arrow. Katakana (ピクセルコンズ) runs down the side.', (12, 37)),
    ('sky.png', 27, 'Pixel Sky', 'Bright sky islands with trees, a little red-roofed house and drifting clouds.', (25, 50)),
]


def heart(emo, col, size, dur, delay, pos):
    return (f'<span style="position: absolute; {pos}; font-size: {size}px; line-height: 1; filter: drop-shadow(0 0 {max(3, size // 4)}px {col}); '
            f'animation: {dur}s linear {delay}s infinite {P}">{emo}</span>')


def hearts(count, band, seed):
    """big pair first, then floating hearts that avoid the lettering band (banner coordinates, offset by the wrapper padding)."""
    if count == 0:
        return ''
    r = random.Random(seed)
    ly0, ly1 = band
    out = [heart(YEL, GOLD, 24, 2.0, -2.0, f'left: 2px; top: {PAD_Y + (ly0 + ly1) // 2 - 12}px'),
           heart(BLU, BLUE, 24, 2.0, -1.0, f'right: 2px; top: {PAD_Y + (ly0 + ly1) // 2 - 16}px')]
    n_float = count - 2
    # x slots spread across the banner; alternate above / below the lettering
    xs = [(i + 0.5) / n_float for i in range(n_float)]
    r.shuffle(xs)
    for i, x in enumerate(xs):
        emo, col = (YEL, GOLD) if i % 2 == 0 else (BLU, BLUE)
        size = r.choice([8, 9, 10, 11, 12, 13])
        above = (i % 2 == 0) and ly0 > 24
        if above:
            lo, hi = 3, max(4, ly0 - 5 - size)
        else:
            lo, hi = ly1 + 5, BH - size - 3
        y = PAD_Y + round(lo + r.random() * max(0, hi - lo))
        out.append(heart(emo, col, size, round(1.7 + r.random() * 1.1, 1), -round(r.random() * 2.4, 1), f'left: {PAD_X + round(x * (BW - 16))}px; top: {y}px'))
    return ''.join(out[:count])


def sparkle(x, y, dur, dl):
    return (f'<span style="position: absolute; left: {x}px; top: {y}px; width: 1px; height: 1px; background: #fff; '
            f'box-shadow: 0 -1px #fff, 0 1px #fff, -1px 0 #fff, 1px 0 #fff; animation: {dur}s ease-out {dl}s infinite {P}"></span>')


def build(png_bytes, count, band, seed):
    img = ('<img src="data:image/png;base64,' + base64.b64encode(png_bytes).decode() +
           f'" width="{BW}" height="{BH}" style="display: block; image-rendering: pixelated" alt="">')
    if count == 0:
        return ('<span style="position: relative; display: inline-block; width: 280px; height: 84px">' + img +
                sparkle(90, 12, 2.6, -0.4) + sparkle(171, 70, 3.1, -1.7) + sparkle(246, 22, 2.8, -1.1) + '</span>')
    return (f'<span style="position: relative; display: inline-block; padding: {PAD_Y}px {PAD_X}px">' + img +
            sparkle(PAD_X + 90, PAD_Y + 10, 2.6, -0.4) + sparkle(PAD_X + 171, PAD_Y + 70, 3.1, -1.7) + sparkle(PAD_X + 246, PAD_Y + 20, 2.8, -1.1) +
            hearts(count, band, seed) + '</span>')


def main(scenes_dir, root):
    tags = os.path.join(root, 'docs', 'tags')
    roll = open(os.path.join(tags, 'roll.html'), encoding='utf-8').read()
    wrap = lambda h: ('<div style="display: inline-flex; align-items: center">' + h +
                      '<span style="position: relative; display: inline-block; width: 97px; height: 84px">' + roll + '</span></div>')
    man = json.load(open(os.path.join(tags, 'manifest.json'), encoding='utf-8'))
    man = [m for m in man if m['n'] not in {s[1] for s in SCENES}]
    for fname, n, name, desc, band in SCENES:
        png = open(os.path.join(scenes_dir, fname), 'rb').read()
        slug = name.lower().replace(' ', '_')
        files = {}
        for lvl, count in LEVELS.items():
            html = build(png, count, band, n * 31)
            f = f'{n:02d}_{slug}_hearts_{lvl}.html'
            for sub, h in (('plain', html), ('with-roll', wrap(html))):
                open(os.path.join(tags, sub, f), 'w', encoding='utf-8', newline='\n').write(h)
            files[lvl] = f
            print(f'{name:14} {lvl:5} {len(html):6} chars  (+roll {len(wrap(html))})')
        man.append({'n': n, 'name': name, 'desc': desc, 'levels': files})
    json.dump(man, open(os.path.join(tags, 'manifest.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
