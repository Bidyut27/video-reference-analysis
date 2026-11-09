#!/usr/bin/env python3
"""Render the Laughbox brand kit (logo, avatars, banners, watermark) with Cairo.

  python make_branding.py OUT_DIR

Reuses the characters and drawing helpers from the first episode so the channel
art matches the videos.
"""
import math
import os
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "videos", "grandpa-vs-self-checkout"))
import make_video as mv  # noqa: E402
from make_video import (GRANDMA, GRANDPA, INK, PI, SHOPPER, TEEN, ell, fill_ol, person,  # noqa: E402
                        poly, rrect, setc, star4)

BOX = "#f2a54a"
BOX_DARK = "#d9822b"
SUN = "#ffd23f"
PINK = "#ff4d8d"
TEAL = "#1fa59a"
LETTER_COLS = ["#ffd23f", "#ff7a3d", "#ff4d8d", "#9b6bff", "#2fb7ff", "#25c486", "#ffd23f", "#ff7a3d"]


# ---------------------------------------------------------------- mascot
def mascot(ctx, cx, cy, s):
    """Laughing cardboard box. (cx, cy) is the centre of the box front; s=1 -> box 400 px wide."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ol = 12
    # flying "HA"s and stars behind the lid
    for x, y, rot, size, col in ((-150, -390, -0.35, 70, PINK), (10, -455, 0.05, 86, SUN),
                                 (165, -385, 0.38, 66, "#2fb7ff")):
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(rot)
        mv.text(ctx, "HA", 0, 0, size, col, ol=14)
        ctx.restore()
    star4(ctx, -250, -300, 34, "#ffffff", 0.3)
    star4(ctx, 255, -290, 28, "#ffffff", -0.2)
    # back flaps
    poly(ctx, [(-200, -200), (-120, -330), (120, -330), (200, -200)], close=True)
    fill_ol(ctx, BOX_DARK, ol)
    # box body (slight 3-D side)
    poly(ctx, [(200, -200), (250, -235), (250, 165), (200, 200)], close=True)
    fill_ol(ctx, BOX_DARK, ol)
    rrect(ctx, -200, -200, 400, 400, 22)
    fill_ol(ctx, BOX, ol)
    # side flaps flung open like waving arms
    poly(ctx, [(-200, -200), (-330, -290), (-300, -160), (-195, -150)], close=True)
    fill_ol(ctx, BOX, ol)
    poly(ctx, [(200, -200), (335, -300), (310, -165), (200, -150)], close=True)
    fill_ol(ctx, BOX, ol)
    # packing tape
    rrect(ctx, -32, -200, 64, 70, 6)
    setc(ctx, "#f7d39a")
    ctx.fill()
    # face: happy closed eyes, rosy cheeks, big laughing mouth
    for sd in (-1, 1):
        ctx.new_path()
        ctx.arc(sd * 82, -60, 40, PI * 1.12, PI * 1.88)
        ctx.set_source_rgba(*INK)
        ctx.set_line_width(18)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
        ell(ctx, sd * 128, 10, 34, 20)
        setc(ctx, "#ff6f91", 0.55)
        ctx.fill()
    ctx.new_path()
    ctx.move_to(-115, 0)
    ctx.curve_to(-105, 150, 105, 150, 115, 0)
    ctx.close_path()
    ctx.save()
    ctx.clip_preserve()
    fill_ol(ctx, "#7a1f2b", ol)
    rrect(ctx, -80, -10, 160, 30, 8)
    setc(ctx, "#ffffff")
    ctx.fill()
    ell(ctx, 0, 112, 62, 34)
    setc(ctx, "#ff7f9b")
    ctx.fill()
    ctx.restore()
    ctx.new_path()
    ctx.move_to(-115, 0)
    ctx.curve_to(-105, 150, 105, 150, 115, 0)
    ctx.close_path()
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(ol)
    ctx.stroke()
    ctx.restore()


def wordmark(ctx, cx, cy, size, word="LAUGHBOX", tilt=True):
    """Bouncy, multi-colour letters; returns total width."""
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    adv = [ctx.text_extents(ch)[4] * 0.96 for ch in word]
    total = sum(adv)
    x = cx - total / 2
    for i, ch in enumerate(word):
        lx = x + adv[i] / 2
        dy = (-0.06 if i % 2 else 0.04) * size if tilt else 0
        rot = (-0.07 if i % 2 else 0.06) if tilt else 0
        for pass_ in ("shadow", "main"):
            ctx.save()
            ox, oy = (size * 0.05, size * 0.07) if pass_ == "shadow" else (0, 0)
            ctx.translate(lx + ox, cy + dy + oy)
            ctx.rotate(rot)
            if pass_ == "shadow":
                mv.text(ctx, ch, 0, 0, size, (0.09, 0.07, 0.10, 0.9), ol=size * 0.2)
            else:
                mv.text(ctx, ch, 0, 0, size, LETTER_COLS[i % len(LETTER_COLS)], ol=size * 0.16)
                ctx.new_path()
                ell(ctx, -size * 0.12, -size * 0.2, size * 0.07, size * 0.035)
                setc(ctx, "#ffffff", 0.55)
                ctx.fill()
            ctx.restore()
        x += adv[i]
    return total


# ---------------------------------------------------------------- backgrounds
def sunburst(ctx, w, h, cx, cy, c1="#fff1a8", c2="#ff9d2e", n=24):
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, max(w, h) * 0.75)
    g.add_color_stop_rgb(0, *mv.C(c1)[:3])
    g.add_color_stop_rgb(1, *mv.C(c2)[:3])
    ctx.set_source(g)
    ctx.paint()
    L = max(w, h) * 2
    ctx.new_path()
    for i in range(n):
        a = i * 2 * PI / n
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a) * L, cy + math.sin(a) * L)
        ctx.line_to(cx + math.cos(a + PI / n) * L, cy + math.sin(a + PI / n) * L)
        ctx.close_path()
    setc(ctx, "#ffffff", 0.16)
    ctx.fill()


def dots(ctx, w, h, col="#ffffff", a=0.18, step=46):
    setc(ctx, col, a)
    for gy in range(0, h + step, step):
        for gx in range(0 if (gy // step) % 2 == 0 else step // 2, w + step, step):
            ell(ctx, gx, gy, 6, 6)
    ctx.fill()


def confetti(ctx, w, h, seed=4, n=60, region=None):
    import random
    rnd = random.Random(seed)
    x0, y0, x1, y1 = region or (0, 0, w, h)
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        col = rnd.choice(LETTER_COLS)
        if rnd.random() < 0.5:
            star4(ctx, x, y, rnd.uniform(10, 24), col, rnd.uniform(0, 1))
        else:
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(rnd.uniform(0, PI))
            rrect(ctx, -12, -5, 24, 10, 4)
            setc(ctx, col)
            ctx.fill()
            ctx.restore()


def surface(w, h, alpha=False):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32 if alpha else cairo.FORMAT_RGB24, w, h)
    return s, cairo.Context(s)


# ---------------------------------------------------------------- assets
def logo(out):
    s, ctx = surface(2000, 1300, alpha=True)
    mascot(ctx, 1000, 560, 1.05)
    wordmark(ctx, 1000, 1080, 230)
    s.write_to_png(os.path.join(out, "laughbox-logo.png"))


def avatar(out, size=800):
    s, ctx = surface(size, size)
    k = size / 800
    ctx.scale(k, k)
    sunburst(ctx, 800, 800, 400, 400)
    dots(ctx, 800, 800, a=0.12)
    # everything important stays inside the circle crop
    mascot(ctx, 400, 470, 0.95)
    s.write_to_png(os.path.join(out, f"profile-{size}x{size}.png"))


def watermark(out):
    s, ctx = surface(300, 300, alpha=True)
    ell(ctx, 150, 150, 146, 146)
    setc(ctx, SUN)
    ctx.fill_preserve()
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(8)
    ctx.stroke()
    mascot(ctx, 150, 180, 0.36)
    s.write_to_png(os.path.join(out, "watermark-300x300.png"))


def cast(ctx, x, y, s, P, expr, look, pose=None):
    person(ctx, x, y, s, P, expr=expr, t=0.0, look=look, pose=pose, blink=False)


def youtube_banner(out):
    W, H = 2560, 1440
    s, ctx = surface(W, H)
    sunburst(ctx, W, H, W / 2, H / 2)
    dots(ctx, W, H, a=0.1)
    confetti(ctx, W, H, n=110)
    # characters sit outside the 1546x423 all-device safe area (visible on desktop/TV)
    cast(ctx, 330, 1290, 0.62, GRANDPA, "victory", (0.5, 0), dict(la1=-150, la2=-165, ra1=40, ra2=60))
    cast(ctx, 2230, 1290, 0.6, GRANDMA, "smug", (-0.6, 0), dict(ra1=100, ra2=140))
    cast(ctx, 2480, 1190, 0.5, TEEN, "happy", (-0.8, 0))
    cast(ctx, 80, 1190, 0.5, SHOPPER, "wink", (0.8, 0), dict(thumb=True, ra1=120, ra2=175))
    # logo + tagline inside the safe area (x 507-2053, y 508-931)
    mascot(ctx, 820, 760, 0.52)
    wordmark(ctx, 1450, 680, 150)
    rrect(ctx, 1010, 790, 880, 92, 46)
    fill_ol(ctx, "#20232a", 8)
    mv.text(ctx, "CARTOON COMEDY  •  NEW EVERY WEEK", 1450, 836, 40, "#ffffff")
    s.write_to_png(os.path.join(out, "youtube-banner-2560x1440.png"))
    # review copy with safe areas drawn
    ctx.rectangle(507, 508, 1546, 423)
    ctx.set_source_rgba(0, 1, 0, 0.9)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.rectangle(0, 508, W, 423)
    ctx.set_source_rgba(0, 0.4, 1, 0.9)
    ctx.stroke()
    s.write_to_png(os.path.join(out, "_preview-youtube-banner-safe-areas.png"))


def facebook_cover(out):
    W, H = 1640, 624
    s, ctx = surface(W, H)
    sunburst(ctx, W, H, W / 2, H * 0.55)
    dots(ctx, W, H, a=0.1)
    confetti(ctx, W, H, seed=9, n=70)
    # mobile crops the sides, so keep logo/text in the centre ~1100 px
    cast(ctx, 180, 1030, 0.62, GRANDPA, "victory", (0.6, 0), dict(la1=-150, la2=-165, ra1=40, ra2=60))
    cast(ctx, 1470, 1030, 0.6, GRANDMA, "smug", (-0.6, 0), dict(ra1=100, ra2=140))
    mascot(ctx, 470, 360, 0.5)
    wordmark(ctx, 990, 300, 106)
    rrect(ctx, 645, 390, 690, 76, 38)
    fill_ol(ctx, "#20232a", 7)
    mv.text(ctx, "CARTOON COMEDY • NEW EVERY WEEK", 990, 428, 31, "#ffffff")
    s.write_to_png(os.path.join(out, "facebook-cover-1640x624.png"))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    os.makedirs(out, exist_ok=True)
    logo(out)
    avatar(out, 800)
    watermark(out)
    youtube_banner(out)
    facebook_cover(out)
    print("written to", out)


if __name__ == "__main__":
    main()
