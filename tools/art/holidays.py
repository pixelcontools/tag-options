"""Holiday PIXELCONS banner scenes (280x84 PNG), numbered from 100 in the gallery. Reuses the helpers in scenes.py.

    python holidays.py OUTDIR     # halloween, christmas, nye, valentine, lunar, easter, sakura, july4 (.png, no hearts: those are HTML overlays)
"""
import math, os, random, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenes import W, H, GOLD, LBLUE, BLUE, RED, gradient, sparkle, wordmark, finish, skyline, lerp

HEART = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
BAT = ["1000001", "1100011", "1111111", "0110110", "0000000"]


def dot(px, x, y, col):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = col if len(col) == 4 else col + (255,)


def sprite(px, x0, y0, rows, col, s=1):
    for j, row in enumerate(rows):
        for i, c in enumerate(row):
            if c == '1':
                for dy in range(s):
                    for dx in range(s):
                        dot(px, x0 + i * s + dx, y0 + j * s + dy, col)


def stars(px, seed, n, ymax, cols=((255, 255, 255), (255, 240, 190), (170, 200, 255))):
    r = random.Random(seed)
    for _ in range(n):
        dot(px, r.randrange(W), r.randrange(0, ymax), r.choice(cols))


def burst(px, cx, cy, rad, col, rays=16, seed=0):
    """firework: dotted rays that fade outward, with a bright core"""
    r = random.Random(seed)
    for k in range(rays):
        a = k / rays * 2 * math.pi + r.random() * 0.2
        for s in range(2, rad + 1, 2):
            f = 1 - s / (rad + 3)
            c = lerp((255, 255, 255), col, min(1, s / rad * 1.2))
            dot(px, round(cx + math.cos(a) * s), round(cy + math.sin(a) * s), c + (int(255 * (0.4 + 0.6 * f)),))
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        dot(px, cx + dx, cy + dy, (255, 255, 255))


def ball(d, cx, cy, rad, fill, shade=None, hi=(255, 255, 255)):
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=fill + (255,))
    if shade:
        d.arc([cx - rad, cy - rad, cx + rad, cy + rad], 20, 160, fill=shade + (255,))
    d.point((cx - rad // 2, cy - rad // 2), fill=hi + (255,))


# ------------------------------------------------------------------ halloween
def halloween():
    im = gradient([(0, (22, 8, 48)), (0.5, (86, 28, 110)), (0.85, (214, 96, 40)), (1, (255, 150, 40))], 9, 0.04, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    stars(px, 3, 40, 24)
    ball(d, 236, 15, 12, (255, 196, 70), (255, 150, 30))                  # harvest moon
    for cx, cy in ((232, 12), (240, 19), (236, 9)):
        d.point((cx, cy), fill=(236, 160, 50, 255))
    for x, y in ((24, 6), (62, 16), (176, 8), (205, 20), (110, 4)):
        sprite(px, x, y, BAT, (14, 6, 24))
    # haunted house
    d.polygon([(26, 84), (26, 52), (46, 40), (66, 52), (66, 84)], fill=(14, 6, 24, 255))
    d.rectangle([60, 36, 72, 84], fill=(14, 6, 24, 255)); d.polygon([(58, 38), (66, 24), (74, 38)], fill=(14, 6, 24, 255))
    for wx, wy in ((32, 58), (46, 58), (36, 68), (63, 44), (63, 56)):
        d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 168, 40, 255))
    d.rectangle([44, 72, 49, 84], fill=(60, 20, 70, 255))
    # dead tree
    for pts in (((250, 84), (252, 56)), ((252, 56), (244, 44)), ((252, 62), (262, 50)), ((244, 44), (238, 40)), ((262, 50), (268, 46))):
        d.line(pts, fill=(14, 6, 24, 255), width=2)
    # pumpkins
    for cx, cy, rad in ((100, 78, 7), (116, 80, 5), (212, 78, 8), (196, 81, 5)):
        d.ellipse([cx - rad, cy - rad + 1, cx + rad, cy + rad], fill=(255, 128, 20, 255))
        d.arc([cx - rad, cy - rad + 1, cx + rad, cy + rad], 200, 340, fill=(255, 190, 90, 255))
        d.rectangle([cx - 1, cy - rad - 1, cx, cy - rad + 1], fill=(40, 120, 40, 255))
        if rad > 5:
            for ex in (cx - 3, cx + 2):
                d.polygon([(ex, cy - 3), (ex + 2, cy - 3), (ex + 1, cy - 1)], fill=(40, 14, 6, 255))
            d.line([(cx - 3, cy + 2), (cx - 1, cy + 3), (cx + 1, cy + 3), (cx + 3, cy + 2)], fill=(40, 14, 6, 255))
    cols = {c: ((150, 235, 70) if c in 'XEL' else (255, 138, 28)) for c in 'PIXELCONS'}
    wordmark(im, colors=cols, outline=(22, 6, 40), shadow=(120, 30, 150, 235), glow=(255, 120, 20, 255))
    return finish(im, edge=(255, 160, 60, 235))


# ------------------------------------------------------------------ christmas
def christmas():
    im = gradient([(0, (6, 14, 48)), (0.55, (24, 58, 112)), (0.9, (96, 150, 200)), (1, (150, 190, 225))], 10, 0.0, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    stars(px, 8, 50, 40)
    # snowy ground
    d.rectangle([0, 72, W, H], fill=(236, 244, 255, 255))
    for x in range(0, W, 3):
        d.line([(x, 72 + int(1.5 * math.sin(x / 11))), (x, 74)], fill=(236, 244, 255, 255))
    d.rectangle([0, 78, W, H], fill=(200, 218, 240, 255))
    # trees with lights
    lights = [(255, 60, 60), (255, 210, 60), (90, 170, 255), (120, 255, 140)]
    r = random.Random(4)
    for bx in (24, 54, 226, 256):
        top = 30 if bx in (24, 256) else 38
        for k in range(4):
            w = 5 + k * 5; y = top + k * 9
            d.polygon([(bx, y), (bx - w, y + 12), (bx + w, y + 12)], fill=(18, 92, 52, 255))
            d.polygon([(bx, y), (bx - w, y + 12), (bx - w + 4, y + 12)], fill=(12, 66, 38, 255))
            for _ in range(3):
                dot(px, bx + r.randint(-w + 2, w - 2), y + r.randint(4, 11), r.choice(lights))
        d.rectangle([bx - 1, min(top + 34, 71), bx + 1, 73], fill=(84, 52, 28, 255))
        sparkle(px, bx, top - 2, 2, (255, 230, 120))
    # presents
    for x, y, w, h, c in ((84, 72, 10, 8, (210, 40, 50)), (96, 74, 8, 6, (70, 150, 230)), (186, 73, 9, 7, (240, 190, 50)), (172, 75, 7, 5, (60, 170, 90))):
        d.rectangle([x, y, x + w, y + h], fill=c + (255,))
        d.line([(x + w // 2, y), (x + w // 2, y + h)], fill=(255, 255, 255, 255)); d.line([(x, y + h // 2), (x + w, y + h // 2)], fill=(255, 255, 255, 255))
    for _ in range(70):
        dot(px, r.randrange(W), r.randrange(0, 80), (255, 255, 255))
    cols = {c: ((24, 170, 80) if c in 'XEL' else (226, 34, 48)) for c in 'PIXELCONS'}
    wordmark(im, colors=cols, outline=(255, 255, 255), shadow=(10, 50, 40, 235), glow=(255, 214, 120, 255))
    return finish(im, edge=(255, 255, 255, 235))


# ------------------------------------------------------------------ new year's eve
def nye():
    im = gradient([(0, (4, 4, 20)), (0.6, (18, 22, 70)), (1, (44, 40, 110))], 10, 0.0, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    stars(px, 11, 45, 40)
    burst(px, 38, 20, 16, (255, 200, 60), 18, 1)
    burst(px, 244, 22, 18, (255, 90, 160), 18, 2)
    burst(px, 142, 11, 10, (110, 190, 255), 14, 3)
    burst(px, 92, 44, 8, (150, 255, 170), 12, 4)
    burst(px, 200, 46, 8, (255, 160, 90), 12, 5)
    skyline(d, (14, 14, 40), 14, 26, 10, 18, None, 0, 21)
    skyline(d, (6, 6, 24), 6, 18, 8, 15, GOLD, 0.45, 22)
    r = random.Random(9)
    for _ in range(60):                                                # confetti
        dot(px, r.randrange(W), r.randrange(0, 80), r.choice([(255, 90, 160), (255, 210, 70), (110, 190, 255), (255, 255, 255)]))
    cols = {c: ((235, 235, 245) if c in 'XEL' else (255, 200, 60)) for c in 'PIXELCONS'}
    wordmark(im, colors=cols, outline=(10, 10, 40), shadow=(0, 0, 10, 235), glow=(255, 200, 80, 255))
    return finish(im, edge=(255, 215, 110, 235))


# ------------------------------------------------------------------ valentine's day
def valentine():
    im = gradient([(0, (255, 196, 210)), (0.5, (255, 130, 168)), (1, (176, 44, 112))], 10, 0.04, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    r = random.Random(14)
    for _ in range(26):
        x, y = r.randrange(-2, W - 6), r.randrange(-2, H - 4)
        if 22 < x < 258 and 25 < y < 54:
            continue
        sprite(px, x, y, HEART, r.choice([(255, 255, 255), (255, 232, 238), (255, 70, 110), (214, 24, 78)]), r.choice([1, 1, 2]))
    sprite(px, 8, 12, HEART, (255, 255, 255), 3); sprite(px, 250, 56, HEART, (255, 255, 255), 3)
    for cx, cy in ((60, 14), (210, 70), (140, 74), (150, 8)):
        sparkle(px, cx, cy, 2, (255, 255, 255))
    cols = {c: (255, 255, 255) for c in 'PIXELCONS'}
    wordmark(im, colors=cols, outline=(196, 24, 84), shadow=(110, 12, 66, 235), glow=(255, 150, 190, 255), bevel=0)
    return finish(im, edge=(255, 255, 255, 235))


# ------------------------------------------------------------------ lunar new year
def lunar():
    im = gradient([(0, (110, 8, 18)), (0.5, (190, 24, 30)), (1, (120, 10, 22))], 10, 0.05, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    gold, dgold = (255, 208, 70), (200, 140, 30)
    for cx, ln in ((16, 12), (50, 20), (232, 18), (266, 10)):                       # hanging lanterns
        d.line([(cx, 0), (cx, ln)], fill=dgold + (255,))
        d.rectangle([cx - 3, ln, cx + 3, ln + 2], fill=gold + (255,))
        d.ellipse([cx - 7, ln + 2, cx + 7, ln + 18], fill=(226, 30, 40, 255), outline=dgold + (255,))
        d.line([(cx, ln + 2), (cx, ln + 18)], fill=dgold + (255,)); d.line([(cx - 4, ln + 4), (cx - 4, ln + 16)], fill=(150, 14, 24, 255))
        d.rectangle([cx - 3, ln + 17, cx + 3, ln + 19], fill=gold + (255,))
        d.line([(cx, ln + 20), (cx, ln + 27)], fill=gold + (255,)); d.point((cx, ln + 28), fill=gold + (255,))
    for y0 in (66, 74):                                                             # gold wave pattern along the bottom
        for x in range(-6, W, 12):
            d.arc([x, y0, x + 12, y0 + 12], 180, 360, fill=dgold + (255,)); d.arc([x + 1, y0 + 1, x + 11, y0 + 11], 180, 360, fill=gold + (255,))
    r = random.Random(6)
    for _ in range(40):
        dot(px, r.randrange(80, 200), r.choice([r.randrange(2, 24), r.randrange(56, 64)]), r.choice([gold, (255, 240, 170)]))
    for cx, cy in ((96, 14), (180, 12), (120, 60), (170, 62)):
        sparkle(px, cx, cy, 2, (255, 230, 140))
    cols = {c: gold for c in 'PIXELCONS'}
    wordmark(im, colors=cols, outline=(84, 4, 12), shadow=(50, 2, 8, 235), glow=(255, 190, 60, 255))
    return finish(im, edge=(255, 208, 70, 240))


# ------------------------------------------------------------------ easter
def easter():
    im = gradient([(0, (170, 218, 255)), (0.6, (226, 236, 255)), (0.8, (255, 236, 248))], 9, 0.0, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    for cx, cy, s in ((40, 12, 1.0), (214, 9, 1.2), (130, 6, 0.8)):                  # clouds
        for ox, oy, rr in ((0, 0, 7), (8, 2, 6), (-8, 3, 5), (15, 4, 4)):
            d.ellipse([cx + ox * s - rr * s, cy + oy - rr * s, cx + ox * s + rr * s, cy + oy + rr * s], fill=(255, 255, 255, 255))
    # meadow with dithered stripes
    for y in range(62, H):
        base = (126, 210, 120) if (y // 4) % 2 else (146, 224, 130)
        d.line([(0, y), (W, y)], fill=base + (255,))
    r = random.Random(2)
    for _ in range(60):
        dot(px, r.randrange(W), r.randrange(63, H), (96, 184, 100))
    for x, y, c in ((12, 66, (255, 255, 255)), (70, 74, (255, 210, 70)), (200, 68, (255, 255, 255)), (262, 72, (255, 150, 190)), (120, 77, (255, 210, 70))):
        d.rectangle([x, y, x + 1, y + 1], fill=c + (255,)); d.point((x - 1, y), fill=c + (255,)); d.point((x + 2, y + 1), fill=c + (255,)); d.point((x, y - 1), fill=c + (255,))
    # eggs
    eggs = [(26, 66, (255, 150, 190), 'z'), (46, 72, (255, 214, 90), 's'), (234, 66, (120, 190, 255), 'z'), (256, 72, (190, 150, 240), 's'), (98, 76, (140, 220, 170), 'z'), (186, 76, (255, 170, 120), 's')]
    for cx, cy, col, pat in eggs:
        d.ellipse([cx - 5, cy - 7, cx + 5, cy + 6], fill=col + (255,))
        light = lerp(col, (255, 255, 255), 0.55)
        if pat == 'z':
            for k in range(-4, 5, 2):
                d.point((cx + k, cy - 1 + (1 if k % 4 == 0 else 0)), fill=light + (255,)); d.point((cx + k, cy + 2 - (1 if k % 4 == 0 else 0)), fill=light + (255,))
        else:
            d.line([(cx - 4, cy), (cx + 4, cy)], fill=light + (255,)); d.point((cx - 2, cy - 4), fill=light + (255,)); d.point((cx + 2, cy + 3), fill=light + (255,))
        d.point((cx - 2, cy - 4), fill=(255, 255, 255, 255))
    pastel = {'P': (255, 120, 168), 'I': (250, 196, 50), 'X': (70, 196, 146), 'E': (70, 150, 230), 'L': (172, 120, 226), 'C': (255, 120, 168), 'O': (250, 196, 50), 'N': (70, 196, 146), 'S': (70, 150, 230)}
    wordmark(im, colors=pastel, outline=(255, 255, 255), shadow=(130, 110, 170, 230))
    return finish(im, edge=(255, 255, 255, 240))


# ------------------------------------------------------------------ spring sakura
def sakura():
    im = gradient([(0, (255, 222, 232)), (0.5, (255, 190, 208)), (1, (250, 160, 190))], 9, 0.06, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    # distant mountain with a snow cap
    d.polygon([(110, 84), (162, 22), (214, 84)], fill=(150, 156, 206, 255))
    d.polygon([(162, 22), (148, 40), (156, 36), (162, 42), (168, 36), (176, 40)], fill=(255, 255, 255, 255))
    d.polygon([(60, 84), (96, 52), (132, 84)], fill=(176, 170, 214, 255))
    d.rectangle([0, 76, W, H], fill=(112, 76, 120, 255))
    # branch with blossoms, top left and bottom right
    d.line([(0, 14), (30, 12), (60, 4), (84, 0)], fill=(82, 48, 52, 255), width=3)
    d.line([(30, 12), (40, 22)], fill=(82, 48, 52, 255), width=2)
    d.line([(W, 66), (258, 60), (238, 54), (220, 58)], fill=(82, 48, 52, 255), width=3)

    def blossom(cx, cy):
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) + abs(dy) <= 3 and not (abs(dx) == 2 and abs(dy) == 2):
                    dot(px, cx + dx, cy + dy, (255, 170, 196) if max(abs(dx), abs(dy)) == 2 else (255, 236, 242))
        dot(px, cx, cy, (232, 86, 130))
    for cx, cy in ((10, 12), (22, 10), (38, 8), (48, 18), (58, 5), (72, 2), (30, 20), (84, 3), (40, 26), (250, 58), (238, 62), (226, 54), (262, 64), (244, 50), (212, 60)):
        blossom(cx, cy)
    r = random.Random(7)
    for _ in range(46):                                                                # falling petals
        x, y = r.randrange(W), r.randrange(H)
        dot(px, x, y, (255, 240, 246) if r.random() < .6 else (255, 150, 182)); dot(px, x + 1, y + 1, (255, 190, 210))
    cols = {c: ((240, 54, 110) if c in 'XEL' else BLUE) for c in 'PIXELCONS'}
    wordmark(im, colors=cols, outline=(255, 255, 255), shadow=(150, 60, 110, 220))
    return finish(im, edge=(255, 255, 255, 240))


# ------------------------------------------------------------------ independence day (4th of july)
def july4():
    im = gradient([(0, (4, 8, 36)), (0.6, (14, 26, 80)), (1, (30, 44, 120))], 10, 0.0, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    stars(px, 17, 40, 40)
    burst(px, 40, 20, 17, (255, 70, 80), 18, 1)
    burst(px, 238, 18, 18, (90, 150, 255), 18, 2)
    burst(px, 140, 9, 9, (255, 255, 255), 14, 3)
    burst(px, 92, 46, 7, (255, 70, 80), 12, 4)
    burst(px, 196, 44, 8, (90, 150, 255), 12, 5)
    d.rectangle([0, 70, W, H], fill=(8, 14, 52, 255))                                  # lake with reflections
    r = random.Random(3)
    for cx, col in ((40, (255, 70, 80)), (238, (90, 150, 255)), (140, (255, 255, 255))):
        for _ in range(16):
            dot(px, cx + r.randint(-14, 14), r.randrange(71, H), col + (150,))
    d.rectangle([0, 66, W, 70], fill=(6, 8, 30, 255))                                  # far shore treeline
    for x in range(0, W, 5):
        d.rectangle([x, 62 + (x * 7 % 4), x + 3, 70], fill=(6, 8, 30, 255))
    cols = {}
    for i, c in enumerate('PIXELCONS'):
        cols[c] = (52, 112, 240) if i < 3 else ((234, 40, 56) if i < 6 else (255, 255, 255))
    wordmark(im, colors=cols, outline=(200, 214, 255), shadow=(0, 0, 30, 235))
    return finish(im, edge=(235, 240, 255, 235))


SCENES = (('halloween', halloween), ('christmas', christmas), ('nye', nye), ('valentine', valentine),
          ('lunar', lunar), ('easter', easter), ('sakura', sakura), ('july4', july4))

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    for name, fn in SCENES:
        im = fn(); p = os.path.join(out, name + '.png'); im.save(p, optimize=True)
        print(name, os.path.getsize(p), 'bytes')
