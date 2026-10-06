"""Four more PIXELCONS banner scenes (280x84 PNG): night, arcade, space, sky islands.

    python scenes.py OUTDIR      # writes night.png arcade.png space.png sky.png (no hearts; hearts are HTML overlays)
"""
import math, random, sys, os
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import numpy as np

W, H = 280, 84
GOLD, LBLUE, BLUE, RED = (255, 202, 58), (199, 235, 250), (25, 130, 196), (231, 29, 54)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def ramp(stops, t):
    t = max(0.0, min(1.0, t))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            return lerp(c0, c1, (t - t0) / ((t1 - t0) or 1))
    return stops[-1][1]


def gradient(stops, bands, fx, fy):
    """banded + ordered-dithered gradient; t = (x*fx + y*fy)/(W*fx + H*fy)"""
    im = Image.new('RGBA', (W, H))
    px = im.load()
    norm = W * fx + H * fy
    for y in range(H):
        for x in range(W):
            v = (x * fx + y * fy) / norm * bands + (BAYER[y % 4][x % 4] / 16 - 0.5)
            px[x, y] = ramp(stops, max(0, min(bands, round(v))) / bands) + (255,)
    return im


def sparkle(px, cx, cy, r=3, col=(255, 255, 255)):
    for k in range(-r, r + 1):
        for (x, y) in ((cx + k, cy), (cx, cy + k)):
            if 0 <= x < W and 0 <= y < H:
                px[x, y] = col + (255 if abs(k) <= 1 else 190,)


GLYPH = {
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'I': ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'N': ["10001", "11001", "10101", "10101", "10011", "10001", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
}


def grow(m, r):
    a = np.array(m) > 0
    out = a.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + 1:
                out |= np.roll(np.roll(a, dy, 0), dx, 1)
    return Image.fromarray((out * 255).astype('uint8'))


def wordmark(im, colors=None, y0=29, outline=(255, 255, 255), shadow=(12, 38, 86, 225), glow=None, bevel=0.38, S=3, GAP=3):
    word = 'PIXELCONS'
    colors = colors or {c: (RED if c in 'XEL' else BLUE) for c in word}
    tw = len(word) * 5 * S + (len(word) - 1) * GAP
    x0 = (W - tw) // 2 + 1
    mask = Image.new('L', (W, H), 0)
    fill = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    mp, fp = mask.load(), fill.load()
    for n, ch in enumerate(word):
        gx = x0 + n * (5 * S + GAP)
        for r, row in enumerate(GLYPH[ch]):
            for c, bit in enumerate(row):
                if bit != '1':
                    continue
                for dy in range(S):
                    for dx in range(S):
                        yy = y0 + r * S + dy
                        xx = gx + c * S + dx + (20 - (r * S + dy)) // 10
                        if 0 <= xx < W and 0 <= yy < H:
                            mp[xx, yy] = 255
                            base = colors[ch]
                            fp[xx, yy] = (lerp(base, (255, 255, 255), bevel) if (r * S + dy) < 4 else base) + (255,)
    o = grow(mask, 2) if outline else mask
    if glow:
        g = grow(mask, 5).filter(ImageFilter.GaussianBlur(3))
        im.paste(Image.new('RGBA', (W, H), glow), (0, 0), g.point(lambda v: min(255, v * 2)))
    sh = Image.new('L', (W, H), 0); sh.paste(o, (1, 3) if outline else (2, 2))
    im.paste(Image.new('RGBA', (W, H), shadow), (0, 0), sh)
    if outline:
        im.paste(Image.new('RGBA', (W, H), outline + (255,)), (0, 0), o)
    im.alpha_composite(fill)


def finish(im, edge=(255, 255, 255, 235), rad=9):
    rm = Image.new('L', (W, H), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, W - 1, H - 1], radius=rad, fill=255)
    e = Image.new('L', (W, H), 0)
    ImageDraw.Draw(e).rounded_rectangle([0, 0, W - 1, H - 1], radius=rad, outline=255, width=2)
    im.paste(Image.new('RGBA', (W, H), edge), (0, 0), e)
    im.putalpha(ImageChops.multiply(im.getchannel('A'), rm))
    return im


def skyline(d, color, top_min, top_max, wmin, wmax, win_col, win_p, seed, step=4):
    r = random.Random(seed)
    x = -4
    while x < W:
        bw = r.randint(wmin, wmax); bh = r.randint(top_min, top_max)
        d.rectangle([x, H - bh, x + bw - 1, H], fill=color + (255,))
        if r.random() < 0.4:
            d.rectangle([x + bw // 2 - 1, H - bh - 3, x + bw // 2, H - bh], fill=color + (255,))
        if win_col:
            for wy in range(H - bh + 3, H - 2, step):
                for wx in range(x + 2, x + bw - 2, step):
                    if r.random() < win_p:
                        d.rectangle([wx, wy, wx + 1, wy + 1], fill=win_col + (255,))
        x += bw


# ------------------------------------------------------------------ 1. night
def night():
    im = gradient([(0, (8, 10, 36)), (0.45, (22, 36, 96)), (0.8, (58, 92, 170)), (1, (255, 190, 90))], 10, 0.05, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    r = random.Random(5)
    for _ in range(90):
        x, y = r.randrange(W), r.randrange(0, 52)
        px[x, y] = r.choice([(255, 255, 255, 255), (255, 240, 190, 255), (170, 200, 255, 255)])
    # crescent moon
    mk = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mk)
    md.ellipse([226, 9, 252, 35], fill=255); md.ellipse([233, 6, 259, 32], fill=0)
    im.paste(Image.new('RGBA', (W, H), (255, 240, 180, 255)), (0, 0), mk)
    # shooting star
    for k in range(16):
        x, y = 40 + k * 2, 6 + k
        a = int(255 * (1 - k / 16))
        px[x, y] = (255, 255, 255, a) if a > 40 else px[x, y]
    px[38, 5] = (255, 255, 255, 255); px[39, 5] = (255, 255, 255, 255)
    for (cx, cy, rr) in ((24, 30, 3), (252, 50, 2), (120, 8, 3), (170, 12, 2), (90, 46, 2)):
        sparkle(px, cx, cy, rr, (230, 240, 255))
    skyline(d, (30, 52, 110), 18, 32, 10, 18, None, 0, 4)
    skyline(d, (8, 14, 38), 8, 22, 8, 15, GOLD, 0.5, 12)
    wordmark(im, glow=(110, 170, 255, 255), shadow=(4, 8, 30, 235))
    return finish(im, edge=(190, 215, 255, 220))


# ------------------------------------------------------------------ 2. arcade / synthwave
def arcade():
    im = gradient([(0, (16, 6, 44)), (0.40, (70, 20, 110)), (0.62, (200, 56, 120)), (0.74, (255, 150, 70))], 10, 0.0, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    hz = 62
    # sun
    sx, sy, sr = 140, hz, 31
    for y in range(sy - sr, hz):
        t = (y - (sy - sr)) / sr
        col = lerp((255, 224, 80), (255, 90, 90), t)
        half = int(math.sqrt(max(0, sr * sr - (y - sy) ** 2)))
        # horizontal slits getting wider toward the horizon
        if y > sy - sr * 0.55 and (y - hz) % 5 in (0, 1, 2) and t > 0.45 + 0.12 * ((y - hz) % 5 == 0):
            continue
        d.line([sx - half, y, sx + half, y], fill=col + (255,))
    # distant mountains
    for (cx, w, h) in ((38, 44, 20), (92, 36, 14), (214, 40, 18), (256, 40, 22)):
        d.polygon([(cx - w, hz), (cx, hz - h), (cx + w, hz)], fill=(24, 8, 56, 255))
        d.line([(cx - w, hz), (cx, hz - h), (cx + w, hz)], fill=BLUE + (255,))
    # grid floor
    d.rectangle([0, hz, W, H], fill=(18, 6, 44, 255))
    for k in range(1, 9):
        y = hz + int((k / 8) ** 2 * (H - hz))
        d.line([0, y, W, y], fill=BLUE + (255,))
    for k in range(-14, 15):
        d.line([sx, hz, sx + k * 26, H], fill=BLUE + (255,))
    d.line([0, hz, W, hz], fill=(255, 220, 150, 255))
    for (cx, cy, rr) in ((20, 14, 3), (250, 12, 3), (60, 30, 2), (222, 34, 2)):
        sparkle(px, cx, cy, rr, (255, 235, 200))
    wordmark(im, y0=15, colors={c: ((255, 214, 10) if c in 'XEL' else (60, 190, 255)) for c in 'PIXELCONS'}, glow=(255, 70, 160, 255),
             shadow=(40, 0, 70, 235), outline=(255, 255, 255))
    # scanlines
    a = np.array(im)
    a[::3, :, :3] = (a[::3, :, :3] * 0.82).astype('uint8')
    im = Image.fromarray(a)
    return finish(im, edge=(255, 170, 230, 225))


# ------------------------------------------------------------------ 3. space
def space():
    rng = np.random.default_rng(3)
    yy, xx = np.mgrid[0:H, 0:W]
    def blob(cx, cy, sx, sy):
        return np.exp(-(((xx - cx) / sx) ** 2 + ((yy - cy) / sy) ** 2))
    neb_b = blob(60, 30, 60, 22) + 0.7 * blob(230, 60, 55, 18)
    neb_r = blob(200, 18, 48, 16) + 0.6 * blob(20, 70, 40, 14)
    neb_g = blob(140, 74, 70, 10)
    im = Image.new('RGBA', (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            th = BAYER[y % 4][x % 4] / 16
            def q(v):          # quantise to 4 levels with dithering
                return min(3, int(v * 3.2 + th)) / 3
            b, r_, g = q(neb_b[y, x]), q(neb_r[y, x]), q(neb_g[y, x])
            col = (6, 8, 24)
            col = lerp(col, (25, 100, 170), b * 0.75)
            col = lerp(col, (170, 30, 60), r_ * 0.7)
            col = lerp(col, (200, 150, 40), g * 0.5)
            px[x, y] = col + (255,)
    d = ImageDraw.Draw(im)
    r = random.Random(9)
    for _ in range(140):
        x, y = r.randrange(W), r.randrange(H)
        px[x, y] = r.choice([(255, 255, 255, 255), (255, 235, 170, 255), (160, 200, 255, 255)])
    # orbit ellipse
    for k in range(0, 360, 6):
        x, y = round(60 + math.cos(math.radians(k)) * 52), round(66 + math.sin(math.radians(k)) * 11)
        if 0 <= x < W and 0 <= y < H:
            px[x, y] = (120, 160, 220, 255)
    # ringed gold planet (bottom-left)
    def planet(cx, cy, rad, base, light, dark):
        for y in range(cy - rad, cy + rad + 1):
            for x in range(cx - rad, cx + rad + 1):
                dx, dy = x - cx, y - cy
                if dx * dx + dy * dy <= rad * rad and 0 <= x < W and 0 <= y < H:
                    t = (dx * -0.6 + dy * -0.8) / rad * 0.5 + 0.5
                    t = t + (BAYER[y % 4][x % 4] / 16 - 0.5) * 0.35
                    px[x, y] = (light if t > 0.72 else base if t > 0.3 else dark) + (255,)
    planet(36, 62, 14, (255, 180, 40), (255, 228, 120), (190, 110, 20))
    for k in range(-30, 31):
        x = 36 + k; y = 62 + round(k * 0.22)
        if 0 <= x < W and (abs(k) > 15 or y > 62):
            d.point((x, y), fill=(255, 225, 150, 255)); d.point((x, y + 1), fill=(190, 140, 70, 255))
    planet(246, 18, 9, (25, 130, 196), (150, 210, 250), (10, 60, 120))
    planet(222, 66, 5, (231, 29, 54), (255, 150, 150), (120, 10, 30))
    for (cx, cy, rr) in ((100, 14, 3), (176, 8, 2), (84, 56, 2), (192, 50, 3), (14, 24, 2)):
        sparkle(px, cx, cy, rr, (255, 255, 255))
    wordmark(im, glow=(90, 170, 255, 255), shadow=(4, 6, 30, 240))
    return finish(im, edge=(170, 200, 255, 220))


# ------------------------------------------------------------------ 4. sky islands
def sky():
    im = gradient([(0, (70, 160, 232)), (0.55, (150, 213, 250)), (1, (226, 246, 255))], 9, 0.1, 1.0)
    d, px = ImageDraw.Draw(im), im.load()

    def cloud(cx, cy, s=1.0):
        blobs = [(0, 0, 11, 6), (-9, 2, 8, 5), (10, 2, 9, 5), (3, -4, 7, 5)]
        for shade, off in (((204, 224, 244, 255), 2), ((255, 255, 255, 255), 0)):
            for bx, by, rx, ry in blobs:
                d.ellipse([cx + (bx - rx) * s, cy + (by - ry) * s + off, cx + (bx + rx) * s, cy + (by + ry) * s + off], fill=shade)
    cloud(200, 56, 1.0); cloud(60, 66, 0.9); cloud(130, 76, 0.8); cloud(250, 12, 0.7); cloud(24, 12, 0.7)

    def island(cx, cy, w, tree=True, house=False):
        # rock underside (stepped triangle)
        for i in range(0, 16):
            ww = int(w * (1 - i / 16))
            d.rectangle([cx - ww // 2, cy + i, cx + ww // 2, cy + i], fill=((110, 78, 52) if i % 4 else (88, 60, 40)) + (255,))
        d.rectangle([cx - w // 2, cy - 3, cx + w // 2, cy + 1], fill=(112, 190, 70, 255))
        d.rectangle([cx - w // 2, cy - 3, cx + w // 2, cy - 2], fill=(160, 225, 100, 255))
        d.rectangle([cx - w // 2 + 1, cy + 2, cx + w // 2 - 1, cy + 3], fill=(76, 150, 54, 255))
        if tree:
            tx = cx - w // 4
            d.rectangle([tx, cy - 9, tx + 1, cy - 4], fill=(110, 70, 40, 255))
            d.ellipse([tx - 4, cy - 17, tx + 5, cy - 8], fill=(60, 150, 70, 255))
            d.ellipse([tx - 2, cy - 17, tx + 3, cy - 12], fill=(110, 200, 100, 255))
        if house:
            hx = cx + w // 6
            d.rectangle([hx, cy - 10, hx + 8, cy - 4], fill=(255, 240, 200, 255))
            d.polygon([(hx - 1, cy - 10), (hx + 4, cy - 15), (hx + 9, cy - 10)], fill=RED + (255,))
            d.rectangle([hx + 3, cy - 8, hx + 5, cy - 4], fill=(110, 70, 40, 255))
    island(34, 52, 44, tree=True)
    island(256, 56, 46, tree=True, house=True)
    island(150, 74, 30, tree=False)
    for (bx, by) in ((100, 14), (112, 10), (232, 24)):
        for k in range(-3, 4):
            px[bx + k, by + abs(k) // 2 * -1 + 2] = (50, 70, 110, 255)
    for (cx, cy, rr) in ((74, 22, 3), (188, 24, 3), (130, 16, 2), (268, 62, 2), (8, 40, 2)):
        sparkle(px, cx, cy, rr, (255, 255, 255))
    wordmark(im, y0=27, shadow=(18, 60, 130, 230))
    return finish(im, edge=(255, 255, 255, 240))



def heartsob(px, x0, y0, scale=2):
    """Heart-shaped sob emoji: an 8x8 pixel sprite (heartsob.png next to this file), each pixel drawn scale x scale."""
    spr = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heartsob.png')).convert('RGBA')
    for j in range(spr.height):
        for i in range(spr.width):
            c = spr.getpixel((i, j))
            if not c[3]:
                continue
            for dy in range(scale):
                for dx in range(scale):
                    X, Y = x0 + i * scale + dx, y0 + j * scale + dy
                    if 0 <= X < W and 0 <= Y < H:
                        px[X, Y] = c


# ------------------------------------------------------------------ 5. city pop (80s Japan)
def citypop():
    from PIL import ImageFont
    im = gradient([(0, (58, 168, 232)), (0.38, (140, 214, 242)), (0.62, (255, 205, 215)), (0.8, (255, 214, 160)), (1, (255, 228, 190))], 11, 0.0, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    hz = 62
    # pastel sun
    sx, sy = 140, hz + 4
    d.ellipse([sx - 37, sy - 37, sx + 37, sy + 37], fill=(255, 196, 206, 255))
    d.ellipse([sx - 31, sy - 31, sx + 31, sy + 31], fill=(255, 150, 175, 255))
    d.ellipse([sx - 22, sy - 26, sx + 6, sy - 6], fill=(255, 205, 210, 255))
    # clouds (flat pastel streaks)
    for (cx, cy, w) in ((60, 8, 22), (214, 6, 18), (262, 30, 14), (28, 44, 16)):
        d.rounded_rectangle([cx - w, cy, cx + w, cy + 3], radius=2, fill=(255, 255, 255, 235))
        d.rounded_rectangle([cx - w // 2, cy - 3, cx + w // 2, cy + 1], radius=2, fill=(255, 255, 255, 235))
    # skyline in hazy pastel, with Tokyo Tower
    r = random.Random(21)
    x = -3
    while x < W:
        bw = r.randint(9, 16); bh = r.randint(7, 17)
        d.rectangle([x, hz - bh, x + bw - 1, hz], fill=(138, 150, 208, 255))
        d.rectangle([x, hz - bh, x + bw - 1, hz - bh], fill=(176, 186, 232, 255))
        for wy in range(hz - bh + 3, hz - 2, 4):
            for wx in range(x + 2, x + bw - 2, 4):
                if r.random() < 0.25:
                    d.rectangle([wx, wy, wx + 1, wy + 1], fill=(255, 238, 190, 255))
        x += bw
    # tiny street lights along the rail, with a soft warm glow
    def streetlight(x, base=hz + 1, h=17):
        top = base - h
        gl = Image.new('L', (W, H), 0); gd = ImageDraw.Draw(gl)
        gd.ellipse([x + 4 - 9, top + 3 - 8, x + 4 + 9, top + 3 + 8], fill=50)
        gd.ellipse([x + 4 - 5, top + 3 - 5, x + 4 + 5, top + 3 + 5], fill=70)
        im.paste(Image.new('RGBA', (W, H), (255, 236, 170, 255)), (0, 0), gl)
        d.rectangle([x, top, x + 1, base], fill=(92, 98, 140, 255))                  # pole
        d.rectangle([x, top, x + 5, top], fill=(92, 98, 140, 255))                   # arm
        d.rectangle([x + 3, top + 1, x + 6, top + 1], fill=(70, 74, 110, 255))      # lamp housing
        d.rectangle([x + 3, top + 2, x + 6, top + 2], fill=(255, 244, 190, 255))    # lit lamp
    for lx in (30, 66, 104, 142, 228):
        streetlight(lx)
    # bus stop: glass shelter with a bench and a poster, plus a round bus sign on a pole
    bx = 240
    d.rectangle([bx, 49, bx + 22, 50], fill=(96, 102, 150, 255)); d.line([bx, 48, bx + 22, 48], fill=(160, 166, 210, 255))
    d.rectangle([bx + 2, 51, bx + 20, hz], fill=(196, 226, 246, 255))
    for k in range(0, 12, 4):
        d.line([bx + 3 + k, hz - 1, bx + 7 + k, 53], fill=(240, 250, 255, 255))      # glass reflections
    d.rectangle([bx + 13, 53, bx + 19, 59], fill=(255, 150, 175, 255), outline=(255, 255, 255, 255))   # poster
    d.rectangle([bx + 1, 51, bx + 1, hz + 1], fill=(96, 102, 150, 255)); d.rectangle([bx + 21, 51, bx + 21, hz + 1], fill=(96, 102, 150, 255))
    d.rectangle([bx + 4, 58, bx + 12, 59], fill=(130, 82, 48, 255))                 # bench
    d.rectangle([bx + 5, 60, bx + 5, hz], fill=(96, 102, 150, 255)); d.rectangle([bx + 11, 60, bx + 11, hz], fill=(96, 102, 150, 255))
    d.rectangle([bx + 25, 46, bx + 26, hz + 1], fill=(110, 114, 146, 255))          # sign pole
    d.ellipse([bx + 20, 36, bx + 31, 47], fill=BLUE + (255,), outline=(255, 255, 255, 255))
    d.rectangle([bx + 22, 39, bx + 29, 43], fill=(255, 255, 255, 255))               # little bus
    d.rectangle([bx + 23, 40, bx + 24, 41], fill=BLUE + (255,)); d.rectangle([bx + 26, 40, bx + 27, 41], fill=BLUE + (255,))
    px[bx + 23, 44] = (255, 255, 255, 255); px[bx + 28, 44] = (255, 255, 255, 255)
    # elevated road in the foreground: guardrail, asphalt, edge lines, dashed centre line
    d.rectangle([0, hz + 2, W, H], fill=(74, 78, 116, 255))
    for k in range(hz + 2, H, 4):
        d.line([0, k, W, k], fill=(82, 86, 126, 255))
    d.rectangle([0, hz + 1, W, hz + 2], fill=(226, 230, 244, 255))             # rail top
    d.line([0, hz + 3, W, hz + 3], fill=(150, 156, 190, 255))                   # rail shadow on the road
    for px_ in range(2, W, 9):
        d.rectangle([px_, hz - 2, px_ + 1, hz + 3], fill=(176, 182, 214, 255))  # rail posts
    d.line([0, hz + 6, W, hz + 6], fill=(240, 244, 255, 255))                   # near-side edge line
    for dx in range(-4, W, 14):
        d.rectangle([dx, 76, dx + 7, 76], fill=(255, 226, 120, 255))             # dashed centre line
    d.line([0, H - 3, W, H - 3], fill=(240, 244, 255, 255))
    # roadside sign: crying emoji + arrow pointing the way the car is heading (right)
    d.rounded_rectangle([178, 40, 222, 59], radius=2, fill=(255, 255, 255, 255), outline=BLUE + (255,))
    d.rectangle([186, 60, 187, hz + 3], fill=(110, 114, 146, 255)); d.rectangle([213, 60, 214, hz + 3], fill=(110, 114, 146, 255))
    heartsob(px, 183, 42)
    d.rectangle([202, 48, 210, 50], fill=BLUE + (255,))
    d.polygon([(209, 44), (209, 54), (218, 49)], fill=BLUE + (255,))
    # white Lamborghini Countach (side view, facing right)
    def countach(x0, y0):
        d.ellipse([x0 + 3, y0 + 10, x0 + 43, y0 + 13], fill=(40, 42, 70, 255))       # ground shadow
        body = [(2, 8), (2, 4), (9, 3), (17, 1), (27, 1), (34, 5), (46, 7), (46, 8), (44, 9), (4, 9)]
        d.polygon([(x0 + x, y0 + y) for x, y in body], fill=(255, 255, 255, 255))
        d.rectangle([x0 + 4, y0 + 7, x0 + 44, y0 + 8], fill=(212, 218, 234, 255))    # lower body shading
        d.polygon([(x0 + 18, y0 + 2), (x0 + 26, y0 + 2), (x0 + 31, y0 + 5), (x0 + 20, y0 + 5)], fill=(34, 44, 86, 255))
        d.line([(x0 + 19, y0 + 2), (x0 + 25, y0 + 2)], fill=(130, 180, 235, 255))
        d.rectangle([x0 + 12, y0 + 5, x0 + 16, y0 + 6], fill=(46, 52, 88, 255))      # side air intake
        d.line([(x0 + 24, y0 + 5), (x0 + 24, y0 + 7)], fill=(190, 196, 214, 255))      # door shut line
        d.rectangle([x0 + 44, y0 + 6, x0 + 45, y0 + 6], fill=(255, 238, 140, 255))   # headlight
        d.rectangle([x0 + 2, y0 + 5, x0 + 2, y0 + 6], fill=RED + (255,))              # tail light
        d.rectangle([x0 + 1, y0 + 0, x0 + 7, y0 + 0], fill=(255, 255, 255, 255))      # rear wing
        d.rectangle([x0 + 1, y0 + 1, x0 + 7, y0 + 1], fill=(190, 196, 214, 255))
        d.rectangle([x0 + 3, y0 + 2, x0 + 3, y0 + 3], fill=(190, 196, 214, 255))
        for wx in (11, 37):
            d.ellipse([x0 + wx - 4, y0 + 5, x0 + wx + 4, y0 + 13], fill=(46, 52, 88, 255))   # wheel arch
            d.ellipse([x0 + wx - 3, y0 + 6, x0 + wx + 3, y0 + 12], fill=(24, 24, 36, 255))   # tyre
            d.ellipse([x0 + wx - 1, y0 + 8, x0 + wx + 1, y0 + 10], fill=(196, 198, 212, 255))  # rim
        for k, (dy, ln) in enumerate(((3, 18), (5, 24), (7, 16), (9, 20))):
            d.line([(x0 - 3 - ln, y0 + dy), (x0 - 3, y0 + dy)], fill=(255, 255, 255, 170))   # speed lines
    countach(112, 68)
    # confetti / memphis bits
    d.polygon([(74, 44), (80, 44), (77, 39)], fill=(255, 120, 170, 255))
    for (cx, cy, rr) in ((52, 10, 3), (226, 8, 2), (102, 44, 2), (276, 40, 2)):
        sparkle(px, cx, cy, rr, (255, 255, 255))
    # wordmark: plain brand-blue letters with one soft pink drop shadow (no bevel, no outline, single colour)
    wordmark(im, y0=14, colors={c: BLUE for c in 'PIXELCONS'}, bevel=0, outline=None,
             shadow=(236, 84, 140, 255))
    # vertical katakana, MS Gothic bitmap glyphs (authentic 80s pixel-Japanese look)
    f = ImageFont.truetype('C:/Windows/Fonts/msgothic.ttc', 12)
    km = Image.new('L', (W, H), 0); kd = ImageDraw.Draw(km); kd.fontmode = '1'
    for i, ch in enumerate('ピクセルコンズ'):
        kd.text((8, 2 + i * 11), ch, font=f, fill=255)
    ksh = Image.new('L', (W, H), 0); ksh.paste(km, (1, 1))
    im.paste(Image.new('RGBA', (W, H), (190, 60, 120, 255)), (0, 0), ksh)
    im.paste(Image.new('RGBA', (W, H), (255, 255, 255, 255)), (0, 0), km)
    return finish(im, edge=(255, 255, 255, 240))


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    for name, fn in (('night', night), ('arcade', arcade), ('space', space), ('sky', sky), ('citypop', citypop)):
        im = fn(); p = os.path.join(out, name + '.png'); im.save(p, optimize=True)
        print(name, os.path.getsize(p), 'bytes')
