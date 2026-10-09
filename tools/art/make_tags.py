"""Build tag HTML for the PNG scenes at three heart levels (none / few / all) and update docs/tags (plain/ + manifest.json).
few = a yellow and a blue heart beside the banner; all = that pair plus small hearts floating over the banner around the lettering.
The with-<companion>/ folders are produced by `python tools/build.py`.

    python make_tags.py <scenes_dir> <repo_root>
"""
import base64, json, os, random, re, sys

P = 'maplibregl-user-location-dot-pulse'
GOLD, BLUE = '#ffca3a', '#1982c4'
YEL, BLU = '\U0001f49b', '\U0001f499'
PAD_Y, PAD_X = 0, 26                    # side padding leaves room for the two hearts beside the banner
BW, BH = 280, 84
LEVELS = {'none': 0, 'few': 2, 'all': 16}       # number of hearts per level

SCENES = [
    # file, number, name, description, lettering band (banner y0, y1)
    ('dawn.png', 22, 'Pixel Dawn', 'A pixel-art sunrise skyline banner with a chunky PIXELCONS wordmark and twinkling sparkles. One embedded PNG, so it stays light and sharp.', (27, 52)),
    ('night.png', 24, 'Pixel Night', 'The skyline after dark: crescent moon, shooting star, glowing wordmark and lit windows.', (27, 52)),
    ('arcade.png', 25, 'Pixel Arcade', 'Retro synthwave: striped sun, neon grid floor, scanlines and a pink-glow wordmark.', (13, 38)),
    ('space.png', 26, 'Pixel Space', 'A starfield with nebula clouds, a ringed gold planet and a blue moon behind the wordmark.', (27, 52)),
    ('citypop.png', 28, 'Pixel City Pop', 'Retro Japan, 80s city pop: a white Countach cruises an elevated road above a pastel Tokyo skyline with street lights and a bus stop, toward a sign with a heart-shaped sobbing face and an arrow. Katakana (ピクセルコンズ) runs down the side.', (12, 37)),
    ('citypop2.png', 29, 'Pixel City Pop: Gold to Blue', 'City Pop again, but the whole scene follows the guild gradient: golden hour on the left cooling to blue on the right, down to the skyline, road tint and lamp glow.', (12, 37)),
    ('sky.png', 27, 'Pixel Sky', 'Bright sky islands with trees, a little red-roofed house and drifting clouds.', (25, 50)),
    # franchise-themed scenes (tools/art/themed.py)
    ('namek.png', 30, 'Planet Namek', 'Dragon Ball Z style: a green-to-yellow Namek sky with pale suns, a striped planet, tall pink-purple cliffsides with blue grass, a blue sea and white domes; Dragon Ball Z style lettering (Saiyan Sans) in bright yellow with red XEL and a Dragon Ball for the O.', (22, 64)),
    # holiday styles (tools/art/holidays.py), numbered from 100
    ('halloween.png', 100, 'Halloween', 'Purple dusk with a harvest moon, bats, a haunted house, a dead tree and grinning pumpkins; the wordmark glows pumpkin orange with slime-green XEL.', (27, 52)),
    ('christmas.png', 101, 'Christmas', 'A snowy night with lit pine trees, presents in the snow and a warm glow behind a red and green wordmark.', (27, 52)),
    ('nye.png', 102, "New Year's Eve", 'Midnight over a gold-windowed skyline with fireworks, confetti and a golden wordmark.', (27, 52)),
    ('valentine.png', 103, "Valentine's Day", 'A pink sunset sky full of pixel hearts around a white wordmark with a rose outline.', (27, 52)),
    ('lunar.png', 104, 'Lunar New Year', 'Red and gold: hanging paper lanterns, gold wave patterns along the bottom and a golden wordmark.', (27, 52)),
    ('easter.png', 105, 'Easter', 'A pastel sky and a green meadow with decorated eggs, flowers and a rainbow-pastel wordmark.', (27, 52)),
    ('sakura.png', 106, 'Spring Sakura', 'A soft pink sky with cherry blossom branches, drifting petals and a distant snow-capped mountain.', (27, 52)),
    ('july4.png', 107, 'Independence Day', 'Night-time fireworks over a lake and treeline with a red, white and blue wordmark (US Fourth of July).', (27, 52)),
]


SPARKS = [(90, 10, 2.6, -0.4), (171, 70, 3.1, -1.7), (246, 20, 2.8, -1.1)]
DAWN_SPARKS = [(90, 12, 2.6, -0.4), (171, 50, 3.1, -1.7), (246, 24, 2.8, -1.1), (30, 24, 3.4, -2.3), (120, 56, 2.9, -0.9)]


def heart(emo, col, size, dur, delay, pos):
    return (f'<span style="position: absolute; {pos}; font-size: {size}px; line-height: 1; filter: drop-shadow(0 0 {max(3, size // 4)}px {col}); '
            f'animation: {dur}s linear {delay}s infinite {P}">{emo}</span>')


def hearts(count, band, seed):
    """0 -> nothing; 2 -> one yellow heart left and one blue heart right of the banner, centred vertically;
    more -> that pair plus small hearts floating over the banner above/below the lettering band. All render on top (z-index 2)."""
    if count == 0:
        return ''
    mid = PAD_Y + BH // 2 - 12
    out = [heart(YEL, GOLD, 24, 2.0, -2.0, f'left: 2px; top: {mid}px; z-index: 2'),
           heart(BLU, BLUE, 24, 2.0, -1.0, f'right: 2px; top: {mid}px; z-index: 2')]
    r = random.Random(seed)
    ly0, ly1 = band
    n_float = count - 2
    xs = [(i + 0.5) / n_float for i in range(n_float)] if n_float else []
    r.shuffle(xs)                                   # x slots spread across the banner; alternate above / below the lettering
    for i, x in enumerate(xs):
        emo, col = (YEL, GOLD) if i % 2 == 0 else (BLU, BLUE)
        size = r.choice([8, 9, 10, 11, 12, 13])
        above = (i % 2 == 0) and ly0 > 24
        lo, hi = (3, max(4, ly0 - 5 - size)) if above else (ly1 + 5, BH - size - 3)
        y = PAD_Y + round(lo + r.random() * max(0, hi - lo))
        out.append(heart(emo, col, size, round(1.7 + r.random() * 1.1, 1), -round(r.random() * 2.4, 1),
                         f'left: {PAD_X + round(x * (BW - 16))}px; top: {y}px; z-index: 2'))
    return ''.join(out)


def sparkle(x, y, dur, dl):
    return (f'<span style="position: absolute; left: {x}px; top: {y}px; width: 1px; height: 1px; background: #fff; '
            f'box-shadow: 0 -1px #fff, 0 1px #fff, -1px 0 #fff, 1px 0 #fff; animation: {dur}s ease-out {dl}s infinite {P}"></span>')


def build(png_bytes, count, band, seed, sparks=None):
    img = ('<img src="data:image/png;base64,' + base64.b64encode(png_bytes).decode() +
           f'" width="{BW}" height="{BH}" style="display: block; position: relative; z-index: 1; image-rendering: pixelated" alt="">')
    # the side padding is always there (it is where the hearts go), so the tag keeps the same size and the same gap to the
    # companion image whether the hearts are on or off
    return (f'<span style="position: relative; display: inline-block; padding: {PAD_Y}px {PAD_X}px">' + img +
            ''.join(sparkle(PAD_X + x, PAD_Y + y, d, dl) for x, y, d, dl in (sparks or SPARKS)) +
            hearts(count, band, seed) + '</span>')


def main(scenes_dir, root):
    tags = os.path.join(root, 'docs', 'tags')
    man = json.load(open(os.path.join(tags, 'manifest.json'), encoding='utf-8'))
    man = [m for m in man if m['n'] not in {s[1] for s in SCENES} | {23}]       # 23 (Pixel Dawn Hearts) is now the 'all' level of 22
    for fname, n, name, desc, band in SCENES:
        src = os.path.join(scenes_dir, fname)
        if not os.path.exists(src):                                      # dawn.png is a committed asset, not generated by scenes.py
            src = os.path.join(root, 'tools', 'art', fname)
        png = open(src, 'rb').read()
        slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')      # no colons etc. in file names
        for stale in ('pair', 'many'):                                   # older heart-count variants
            p = os.path.join(tags, 'plain', f'{n:02d}_{slug}_hearts_{stale}.html')
            if os.path.exists(p):
                os.remove(p)
        files = {}
        for lvl, count in LEVELS.items():
            html = build(png, count, band, n * 31, DAWN_SPARKS if n == 22 else None)
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
