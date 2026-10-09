"""Franchise-themed PIXELCONS banner scenes (280x84 PNG). Reuses the helpers in scenes.py.

    python themed.py OUTDIR                       # namek.png (Planet Namek, Dragon Ball Z style wordmark; no hearts: those are HTML overlays)
    python themed.py --render-wordmark FONT       # re-draw tools/art/namek_wordmark.png from a Saiyan Sans .woff/.ttf (only needed to change the lettering)

The lettering is drawn once from the fan font "Saiyan Sans" (Cufon Fonts, listed free for commercial use; it imitates the Dragon Ball Z logo) into
tools/art/namek_wordmark.png, which is committed, so building the scene does not need the font and the font file is not part of this repo.
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenes import W, H, gradient, sparkle, wordmark, finish, lerp


def dot(px, x, y, col):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = col if len(col) == 4 else col + (255,)


WORDMARK_PNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'namek_wordmark.png')


def render_wordmark(font_path, text='PIXELCONS', size=44, ss=8):
    """Draw the Dragon Ball Z style lettering from the font as PIXEL ART: the glyphs are rasterised at ss x, reduced to the 280x84 grid and
    thresholded (hard edges, no anti-aliasing), shaded with three flat colour bands, given a solid 2 px outline and an indigo drop shadow.
    The O is replaced by a pixel-drawn Dragon Ball. Saved as a transparent 280x84 PNG."""
    from PIL import ImageFont
    f = ImageFont.truetype(font_path, size * ss)
    Wd, Hd = W * ss, H * ss
    adv = [f.getlength(c) for c in text]
    x = (Wd - sum(adv)) / 2
    bb_all = f.getbbox(text)
    base_y = int(Hd * 0.5 - (bb_all[3] + bb_all[1]) / 2)

    def to_grid(hi):                       # hi-res mask -> 280x84 hard-edged mask
        return hi.resize((W, H), Image.BOX).point(lambda v: 255 if v >= 128 else 0)

    fills = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sil = Image.new('L', (W, H), 0)
    ball = None
    for c, a in zip(text, adv):
        if c == 'O':
            bb = f.getbbox('O')
            ball = ((x + a / 2) / ss, (base_y + (bb[1] + bb[3]) / 2) / ss, max(bb[2] - bb[0], bb[3] - bb[1]) / 2 / ss * 1.1)
        else:
            hi = Image.new('L', (Wd, Hd), 0)
            ImageDraw.Draw(hi).text((x, base_y), c, font=f, fill=255)
            m = to_grid(hi)
            sil.paste(255, (0, 0), m)
            y0, y1 = m.getbbox()[1], m.getbbox()[3]
            if c in 'XEL':
                bands = ((255, 142, 108), (232, 44, 40), (170, 16, 26))
            else:
                bands = ((255, 250, 150), (255, 220, 40), (250, 160, 14))
            px_m, px_f = m.load(), fills.load()
            for yy in range(y0, y1):
                t = (yy - y0) / max(1, y1 - y0)
                col = bands[0] if t < 0.2 else bands[1] if t < 0.74 else bands[2]
                for xx in range(W):
                    if px_m[xx, yy]:
                        px_f[xx, yy] = col + (255,)
        x += a
    cx, cy, r = ball
    ball_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(ball_layer)
    ci, cj, ri = round(cx), round(cy), round(r)
    bd.ellipse([ci - ri, cj - ri, ci + ri, cj + ri], fill=(222, 108, 10, 255))                          # shaded rim
    bd.ellipse([ci - ri, cj - ri, ci + ri - 2, cj + ri - 3], fill=(250, 150, 16, 255))                  # lit face (leaves a crescent of shade)
    bd.ellipse([ci - ri + 2, cj - ri + 2, ci - ri + 5, cj - ri + 5], fill=(255, 236, 170, 255))          # glint
    for sx, sy in ((-4, -3), (4, -3), (-4, 3), (4, 3)):                                                    # four stars as red plus signs
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            bd.point((ci + sx + dx, cj + sy + dy), fill=(214, 22, 22, 255))
    ball_sil = Image.new('L', (W, H), 0)
    ImageDraw.Draw(ball_sil).ellipse([ci - ri, cj - ri, ci + ri, cj + ri], fill=255)
    sil.paste(255, (0, 0), ball_sil)
    grown = sil.filter(ImageFilter.MaxFilter(5))                                                           # 2 px outline
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sh = Image.new('L', (W, H), 0); sh.paste(grown, (1, 3))
    out.paste(Image.new('RGBA', (W, H), (30, 20, 70, 255)), (0, 0), sh)                                    # solid drop shadow
    out.paste(Image.new('RGBA', (W, H), (34, 12, 8, 255)), (0, 0), grown)                                  # outline
    out.alpha_composite(fills)
    out.alpha_composite(ball_layer)
    out.save(WORDMARK_PNG, optimize=True)
    return WORDMARK_PNG


def glow_ball(d, cx, cy, r, core, edge):
    d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=lerp(edge, (255, 255, 255), 0.35) + (90,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=edge + (255,))
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], fill=core + (255,))


# ------------------------------------------------------------------ Planet Namek (Dragon Ball Z style)
# the cliffs are pink-purple nudged toward beige (about 30%), but clearly less beige than the sand patches
BEIGE_TINT = (226, 200, 154)
PINK, PINK_L, PINK_D = (lerp((196, 128, 176), BEIGE_TINT, 0.3), lerp((230, 164, 204), BEIGE_TINT, 0.3), lerp((148, 92, 140), BEIGE_TINT, 0.3))
CAP = (20, 150, 226)


PINK_DD = lerp((112, 66, 108), BEIGE_TINT, 0.3)


def cliff(d, px, x0, x1, top_at, seed, jag=None):
    """a tall pink-purple cliff face with a blue grass cap. Strata are wavy (not straight columns), with dark layer lines, light and dark
    rock chunks, and, when jag is 'L' (cliff on the left, inner edge on the right) or 'R', a ragged inner edge with grass-topped ledges."""
    r = random.Random(seed)
    off, v = [0] * H, 0
    for y in range(H):                                  # inner edge: random walk, one step every 3 rows
        if y % 3 == 0:
            v = max(-6, min(6, v + r.choice([-2, -1, 0, 0, 1, 2])))
        off[y] = v
    def lim(y):                                         # first/last column drawn at row y
        return (x1 + off[y]) if jag == 'L' else (x0 + off[y]) if jag == 'R' else None
    for y in range(H):
        for x in range(x0 - (6 if jag == 'R' else 0), x1 + (6 if jag == 'L' else 0)):
            if y < top_at(min(max(x, x0), x1 - 1)):
                continue
            if jag == 'L' and x >= lim(y):
                continue
            if jag == 'R' and x < lim(y):
                continue
            wob = int(2.2 * math.sin(y / 6.0 + seed) + 1.6 * math.sin(y / 2.6 + x / 8.0))        # strata drift with height
            k = (x + wob + seed) // 3
            shade = PINK_L if k % 7 == 0 else PINK_D if k % 4 == 0 else PINK
            px[x, y] = shade + (255,)
    # short, broken, softer cracks that follow the wavy strata (long straight dark lines looked wrong)
    for yy in range(16, H, r.randint(9, 13)):
        x = x0 + r.randint(0, 6)
        while x < x1:
            seg = r.randint(2, 5)
            for k in range(seg):
                xx = x + k
                y2 = yy + int(1.6 * math.sin(xx / 4.0 + yy))
                if xx < x1 and y_ok(top_at, xx, y2) and 0 <= y2 < H and px[xx, y2][3] and px[xx, y2][:3] != CAP:
                    px[xx, y2] = lerp((166, 100, 154), BEIGE_TINT, 0.3) + (255,)
            x += seg + r.randint(4, 9)
    for _ in range((x1 - x0) // 2 + 6):
        cx, cy = r.randrange(x0, x1), r.randrange(10, H - 4)
        w, h = r.randint(2, 4), r.randint(1, 3)
        col = PINK_L if r.random() < 0.5 else PINK_D
        for xx in range(cx, cx + w):
            for yy in range(cy, cy + h):
                if 0 <= xx < W and yy < H and y_ok(top_at, xx, yy) and px[xx, yy][3] and px[xx, yy][:3] != CAP:
                    px[xx, yy] = col + (255,)
    for _ in range((x1 - x0) * 2):                                                                 # speckle
        x, y = r.randrange(x0, x1), r.randrange(8, H)
        if y_ok(top_at, x, y) and px[x, y][3] and px[x, y][:3] != CAP:
            px[x, y] = (PINK_L if r.random() < .5 else PINK_D) + (255,)
    # blue grass cap on the top edge (with hanging tufts) and on every ledge of the ragged edge
    for x in range(x0, x1):
        t = top_at(x)
        d.line([(x, t), (x, t + 2)], fill=CAP + (255,))
        if r.random() < 0.35:
            d.line([(x, t + 3), (x, t + 3 + r.randint(1, 4))], fill=CAP + (255,))
    if jag:
        for y in range(1, H):
            a_, b_ = lim(y - 1), lim(y)
            if y < top_at(min(max(a_ if jag == 'L' else b_, x0), x1 - 1)) + 3:
                continue                                       # still above the rock: no ledge here
            if jag == 'L' and b_ > a_:
                d.line([(a_, y), (b_ - 1, y)], fill=CAP + (255,)); d.line([(a_, y + 1), (b_ - 1, y + 1)], fill=CAP + (255,))
            if jag == 'R' and b_ < a_:
                d.line([(b_, y), (a_ - 1, y)], fill=CAP + (255,)); d.line([(b_, y + 1), (a_ - 1, y + 1)], fill=CAP + (255,))
            edge = b_ - 1 if jag == 'L' else b_
            if 0 <= edge < W and y >= top_at(min(max(edge, x0), x1 - 1)) and px[edge, y][:3] != CAP:
                px[edge, y] = PINK_DD + (255,)                                                         # dark rim on the inner edge


def y_ok(top_at, x, y):
    return 0 <= x < W and y >= top_at(x) + 3


def namek():
    # vivid green sky fading to a yellow-green horizon, like Namek's
    im = gradient([(0, (30, 146, 26)), (0.4, (104, 202, 40)), (0.62, (186, 234, 70)), (0.8, (226, 246, 112))], 9, 0.0, 1.0)
    d, px = ImageDraw.Draw(im), im.load()
    r = random.Random(11)
    # pale suns and a striped neighbour planet
    glow_ball(d, 150, 13, 5, (255, 252, 218), (250, 238, 150))
    glow_ball(d, 126, 8, 2, (255, 252, 218), (250, 238, 150))
    d.ellipse([186, 4, 202, 20], fill=(232, 168, 130, 255))
    for yy, col in ((7, (252, 214, 180)), (11, (252, 214, 180)), (15, (244, 190, 150))):
        d.line([(188, yy), (200, yy)], fill=col + (255,))
    for cx, cy in ((92, 14), (172, 22)):                                            # thin clouds
        for ox, oy, rr in ((0, 0, 4), (6, 1, 3), (-6, 1, 3)):
            d.ellipse([cx + ox - rr, cy + oy - 1, cx + ox + rr, cy + oy + 1], fill=(236, 248, 186, 255))
    # distant mesas (behind the lettering), then the bright blue grass
    for x0, x1, top in ((58, 100, 54), (108, 128, 58), (160, 186, 57), (192, 232, 52)):
        cliff(d, px, x0, x1, lambda x, t=top: t + (1 if x % 7 == 0 else 0), x0)
    # Namek's grass is bright blue with darker blue blades, not water: flat blue base, mottling, then tufts of leaning blades
    d.rectangle([0, 66, W, H], fill=(24, 148, 238, 255))
    d.line([(0, 66), (W, 66)], fill=(92, 192, 252, 255))
    for _ in range(70):                                                                   # darker / lighter mottling
        x, y = r.randrange(W), r.randrange(68, H)
        d.rectangle([x, y, x + r.randint(3, 8), y + r.randint(1, 2)], fill=((18, 136, 228) if r.random() < .6 else (34, 158, 242)) + (255,))
    def blades(n, only_blue=False):
        for _ in range(n):
            x, y = r.randrange(2, W - 2), r.randrange(69, H)
            dark = r.random() < .62
            col = (14, 118, 214) if dark else (72, 186, 250)          # close to the base blue: a soft texture
            for k in (-2, 0, 2) if r.random() < .25 else (0,):                             # a tuft is one to three blades
                bx, by, lean = x + k, y - (1 if k else 0), r.choice((-1, 1))
                for dx, dy in ((0, 0), (0, -1), (lean, -2)):
                    if 0 <= bx + dx < W and 66 < by + dy < H and (not only_blue or (px[bx + dx, by + dy][2] > 200 and px[bx + dx, by + dy][0] < 140)):
                        px[bx + dx, by + dy] = col + (255,)
    blades(55)
    # light beige sandy patches on the ground, so it is not all blue (a darker lower edge and a few pebbles give them depth)
    pr = random.Random(21)
    for cx, cy, rw, rh in ((90, 76, 17, 4), (150, 77, 25, 4), (200, 74, 14, 4), (60, 79, 10, 3), (230, 78, 10, 3), (122, 71, 9, 2)):
        for x in range(cx - rw - 1, cx + rw + 2):
            for y in range(cy - rh - 1, cy + rh + 2):
                if not (66 < y < H) or not (0 <= x < W):
                    continue
                dd = ((x - cx) / rw) ** 2 + ((y - cy) / rh) ** 2 + pr.uniform(-0.18, 0.18)
                if dd < 1.0:
                    low = y > cy + rh * 0.35 or dd > 0.78
                    px[x, y] = ((214, 190, 142) if low else (244, 228, 188) if y < cy else (230, 208, 160)) + (255,)
        for _ in range(rw):
            dot(px, pr.randint(cx - rw + 3, cx + rw - 3), pr.randint(cy - 1, cy + 2), (184, 150, 100) if pr.random() < .6 else (252, 242, 212))
    blades(30, only_blue=True)                                                           # grass tufts around the sand patches
    # the two big cliffsides, extremely tall: left one steps up, right one slants up to the corner
    cliff(d, px, 0, 46, lambda x: 12 if x < 30 else 22 - (x - 30) // 2, 3, jag='L')
    cliff(d, px, 236, W, lambda x: 4 + (W - x) * 2 // 3 if x < 262 else 2, 8, jag='R')
    # pale Namekian houses by the shore
    for cx in (86, 206):
        d.pieslice([cx - 8, 58, cx + 8, 74], 180, 360, fill=(226, 244, 226, 255))
        d.pieslice([cx - 8, 58, cx + 8, 74], 180, 240, fill=(250, 255, 250, 255))
        for wx in (-4, 0, 4):
            d.rectangle([cx + wx - 1, 63, cx + wx, 64], fill=(44, 120, 120, 255))
    # only a few trees: thin trunks with small dark-blue canopies
    for bx, by, h in ((14, 13, 7), (246, 27, 10), (118, 58, 7)):
        d.line([(bx, by), (bx, by - h)], fill=(166, 108, 56, 255))
        d.ellipse([bx - 3, by - h - 4, bx + 3, by - h + 2], fill=(24, 52, 150, 255))
        dot(px, bx - 1, by - h - 3, (80, 120, 220))
    for cx, cy in ((72, 20), (240, 40), (136, 66)):
        sparkle(px, cx, cy, 2, (255, 255, 230))
    # lettering: the Dragon Ball Z style layer drawn from Saiyan Sans (committed PNG); falls back to the pixel wordmark if it is missing
    if os.path.exists(WORDMARK_PNG):
        im.alpha_composite(Image.open(WORDMARK_PNG).convert('RGBA'))
    else:
        cols = {c: ((226, 28, 30) if c in 'XEL' else (255, 226, 40)) for c in 'PIXELCONS'}
        wordmark(im, colors=cols, outline=(34, 12, 8), shadow=(30, 20, 70, 235), bevel=0.45)
    return finish(im, edge=(255, 224, 90, 240))


SCENES = (('namek', namek),)

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--render-wordmark':
        print('wrote', render_wordmark(sys.argv[2]))
        sys.exit(0)
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    for name, fn in SCENES:
        im = fn(); p = os.path.join(out, name + '.png')
        # smooth lettering has thousands of shades; 256 colours looks the same at 280x84 and is about 3x smaller (the PNG is embedded in the tag)
        im.quantize(colors=256, method=Image.FASTOCTREE, dither=Image.NONE).save(p, optimize=True)
        print(name, os.path.getsize(p), 'bytes')
