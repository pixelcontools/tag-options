"""Procedural pixel-art banner for the PIXELCONS guild tag ("Pixel Dawn" skyline scene)."""
import random, math, sys
from PIL import Image, ImageDraw

W, H = 280, 84
GOLD, LBLUE, BLUE, RED, NAVY = (255, 202, 58), (199, 235, 250), (25, 130, 196), (231, 29, 54), (14, 52, 92)
rnd = random.Random(7)

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def ramp(stops, t):
    t = max(0, min(1, t))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            return lerp(c0, c1, (t - t0) / (t1 - t0 or 1))
    return stops[-1][1]


im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
px = im.load()

# ---- sky: diagonal brand gradient, banded + ordered-dithered so it reads as pixel art
SKY = [(0.0, (255, 214, 102)), (0.30, (255, 238, 170)), (0.52, LBLUE), (0.78, (96, 178, 224)), (1.0, BLUE)]
BANDS = 9
for y in range(H):
    for x in range(W):
        t = (x * 0.55 + y * 0.85) / (W * 0.55 + H * 0.85)
        v = t * BANDS + (BAYER[y % 4][x % 4] / 16 - 0.5)
        band = max(0, min(BANDS, round(v)))
        px[x, y] = ramp(SKY, band / BANDS) + (255,)

d = ImageDraw.Draw(im)

# ---- sun, rising behind the skyline on the left
sx, sy = 40, 60
for k in range(16):
    a = k * math.pi / 8
    r0, r1 = 17, 27 if k % 2 == 0 else 23
    for r in range(r0, r1):
        x, y = round(sx + math.cos(a) * r), round(sy + math.sin(a) * r)
        d.rectangle([x - 1, y - 1, x, y], fill=(255, 190, 40, 255))
d.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(255, 168, 0, 255))
d.ellipse([sx - 12, sy - 12, sx + 12, sy + 12], fill=(255, 205, 40, 255))
d.ellipse([sx - 8, sy - 9, sx + 5, sy + 2], fill=(255, 236, 130, 255))


# ---- pixel clouds
def cloud(cx, cy, s=1.0):
    blobs = [(0, 0, 11, 6), (-9, 2, 8, 5), (10, 2, 9, 5), (3, -4, 7, 5)]
    for shade, off in (((205, 224, 240, 255), 2), ((255, 255, 255, 255), 0)):
        for bx, by, rx, ry in blobs:
            d.ellipse([cx + (bx - rx) * s, cy + (by - ry) * s + off, cx + (bx + rx) * s, cy + (by + ry) * s + off], fill=shade)


cloud(112, 15, 0.95)
cloud(228, 11, 0.8)
cloud(20, 14, 0.65)

# ---- skyline (two parallax layers) with lit windows
def skyline(base, color, top_min, top_max, wmin, wmax, windows, seed):
    r = random.Random(seed)
    x = -4
    while x < W:
        bw = r.randint(wmin, wmax)
        bh = r.randint(top_min, top_max)
        d.rectangle([x, H - bh, x + bw - 1, H], fill=color + (255,))
        if r.random() < 0.4:   # antenna / water tower block
            d.rectangle([x + bw // 2 - 1, H - bh - 3, x + bw // 2, H - bh], fill=color + (255,))
        if windows:
            for wy in range(H - bh + 3, H - 2, 4):
                for wx in range(x + 2, x + bw - 2, 4):
                    if r.random() < 0.38:
                        d.rectangle([wx, wy, wx + 1, wy + 1], fill=GOLD + (255,))
        x += bw


skyline(0, (86, 160, 208), 16, 30, 10, 18, False, 3)
skyline(0, NAVY, 8, 21, 8, 15, True, 11)

# ---- tiny pixel hearts (the guild's 💛💙)
HEART = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]


def heart(x0, y0, col, hi):
    for j, row in enumerate(HEART):
        for i, c in enumerate(row):
            if c == '1':
                px[x0 + i, y0 + j] = col + (255,)
    px[x0 + 1, y0 + 1] = hi + (255,); px[x0 + 2, y0 + 1] = hi + (255,)
    for j, row in enumerate(HEART):          # dark outline
        for i, c in enumerate(row):
            if c == '1':
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    X, Y = x0 + i + dx, y0 + j + dy
                    if 0 <= X < W and 0 <= Y < H and (i + dx < 0 or i + dx > 6 or j + dy < 0 or j + dy > 5 or HEART[j + dy][i + dx] == '0'):
                        px[X, Y] = (40, 30, 20, 255)


heart(9, 28, (255, 214, 10), (255, 250, 190))
heart(264, 36, (25, 130, 196), (150, 210, 245))
heart(250, 12, (255, 214, 10), (255, 250, 190))

# ---- chunky pixel wordmark: P I X E L C O N S, slanted, outlined, shadowed
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
WORD = 'PIXELCONS'
COL = {'P': BLUE, 'I': BLUE, 'X': RED, 'E': RED, 'L': RED, 'C': BLUE, 'O': BLUE, 'N': BLUE, 'S': BLUE}
S, GAP = 3, 3
tw = len(WORD) * 5 * S + (len(WORD) - 1) * GAP
x_start, y_start = (W - tw) // 2 + 1, 29
mask = Image.new('L', (W, H), 0)      # letter pixels
shade = Image.new('RGBA', (W, H), (0, 0, 0, 0))
mp, sp = mask.load(), shade.load()
for n, ch in enumerate(WORD):
    gx = x_start + n * (5 * S + GAP)
    for r, row in enumerate(GLYPH[ch]):
        for c, bit in enumerate(row):
            if bit != '1':
                continue
            for dy in range(S):
                for dx in range(S):
                    yy = y_start + r * S + dy
                    xx = gx + c * S + dx + (20 - (r * S + dy)) // 10    # slant
                    if 0 <= xx < W and 0 <= yy < H:
                        mp[xx, yy] = 255
                        base = COL[ch]
                        top = (r * S + dy) < 4          # lighter top rows for a bevel
                        sp[xx, yy] = (lerp(base, (255, 255, 255), 0.38) if top else base) + (255,)


def grow(m, r):
    out = m.copy(); o = out.load(); src = m.load()
    for y in range(H):
        for x in range(W):
            if src[x, y]:
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if 0 <= x + dx < W and 0 <= y + dy < H and dx * dx + dy * dy <= r * r + 1:
                            o[x + dx, y + dy] = 255
    return out


outline = grow(mask, 2)
shadow = Image.new('L', (W, H), 0); shadow.paste(outline, (1, 3))
im.paste(Image.new('RGBA', (W, H), (12, 38, 86, 225)), (0, 0), shadow)       # drop shadow
im.paste(Image.new('RGBA', (W, H), (255, 255, 255, 255)), (0, 0), outline)   # white outline
im.alpha_composite(shade)

# ---- glints near the lettering (like Cub Beach's sparkles)
def sparkle(cx, cy, r=3, col=(255, 255, 255, 255)):
    for k in range(-r, r + 1):
        for (x, y) in ((cx + k, cy), (cx, cy + k)):
            if 0 <= x < W and 0 <= y < H:
                a = 255 if abs(k) <= 1 else 190
                px[x, y] = (col[0], col[1], col[2], a)


for (sx_, sy_, rr) in ((70, 20, 3), (199, 22, 4), (137, 47, 2), (232, 40, 3), (108, 22, 2), (54, 50, 2)):
    sparkle(sx_, sy_, rr)

# ---- rounded corners + soft white edge, like the original badge
RAD = 9
rm = Image.new('L', (W, H), 0)
ImageDraw.Draw(rm).rounded_rectangle([0, 0, W - 1, H - 1], radius=RAD, fill=255)
edge = Image.new('L', (W, H), 0)
ImageDraw.Draw(edge).rounded_rectangle([0, 0, W - 1, H - 1], radius=RAD, outline=255, width=2)
im.paste(Image.new('RGBA', (W, H), (255, 255, 255, 235)), (0, 0), edge)
alpha = im.getchannel('A'); im.putalpha(Image.composite(alpha, Image.new('L', (W, H), 0), rm))

out = sys.argv[1] if len(sys.argv) > 1 else 'banner.png'
im.save(out, optimize=True)
print(out, im.size)
