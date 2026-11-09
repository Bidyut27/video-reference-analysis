#!/usr/bin/env python3
"""Render the Laughing Box brand kit (logo, avatar, banners, watermark) with Cairo.

  python make_branding.py OUT_DIR

Reuses the characters and drawing helpers from the first episode so the channel
art matches the videos.
"""
import math
import os
import random
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "episodes", "01-grandpa-vs-self-checkout"))
import make_video as mv  # noqa: E402
from make_video import (GRANDMA, GRANDPA, INK, PI, SHOPPER, TEEN, ell, fill_ol, person,  # noqa: E402
                        poly, rrect, setc, star4)

BOX = "#f2a54a"
BOX_LIGHT = "#f8bf72"
BOX_DARK = "#d9822b"
SUN = "#ffd23f"
PINK = "#ff4d8d"
LETTER_COLS = ["#ffd23f", "#ff7a3d", "#ff4d8d", "#9b6bff", "#2fb7ff", "#25c486", "#ffd23f", "#ff7a3d"]
NAME = "LAUGHING BOX"
HANDLE = "@Officiallaughingbox"
TAGLINE = "CARTOON COMEDY"


# ---------------------------------------------------------------- mascot
def _ha_burst(ctx):
    for x, y, rot, size, col in ((-170, -440, -0.32, 72, PINK), (40, -500, 0.04, 88, SUN),
                                 (245, -430, 0.34, 68, "#2fb7ff")):
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(rot)
        mv.text(ctx, "HA", 0, 0, size, col, ol=15)
        ctx.restore()
    star4(ctx, -300, -370, 28, "#ffffff", 0.3)
    star4(ctx, 370, -360, 24, "#ffffff", -0.2)


def mascot(ctx, cx, cy, s, ha=True):
    """Laughing open cardboard box. (cx, cy) = centre of the front face; s=1 -> front face 400 px."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    ol = 12
    dx, dy = 60, -45  # depth offset of the back edge
    if ha:
        _ha_burst(ctx)
    fl, fr = (-200, -200), (200, -200)
    bl, br = (fl[0] + dx, fl[1] + dy), (fr[0] + dx, fr[1] + dy)
    # back flap standing up
    poly(ctx, [bl, br, (br[0] - 12, br[1] - 115), (bl[0] + 12, bl[1] - 115)], close=True)
    fill_ol(ctx, BOX_DARK, ol)
    # dark inside of the box
    poly(ctx, [fl, fr, br, bl], close=True)
    fill_ol(ctx, "#7a4518", ol)
    # right side face
    poly(ctx, [fr, br, (br[0], 200 + dy), (200, 200)], close=True)
    fill_ol(ctx, BOX_DARK, ol)
    # front face
    rrect(ctx, -200, -200, 400, 400, 10)
    fill_ol(ctx, BOX, ol)
    # side flaps hinged on the top edges, flung outward like waving arms
    poly(ctx, [fl, bl, (bl[0] - 145, bl[1] - 75), (fl[0] - 145, fl[1] - 75)], close=True)
    fill_ol(ctx, BOX_LIGHT, ol)
    poly(ctx, [fr, br, (br[0] + 150, br[1] - 15), (fr[0] + 150, fr[1] - 15)], close=True)
    fill_ol(ctx, BOX_DARK, ol)
    # front flap folded down over the top of the face, with packing tape
    poly(ctx, [fl, fr, (194, -146), (-194, -146)], close=True)
    fill_ol(ctx, BOX_LIGHT, ol)
    ctx.rectangle(-28, -194, 56, 42)
    setc(ctx, "#fbe0b0")
    ctx.fill()
    # face: happy closed eyes, rosy cheeks, big laughing mouth
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for sd in (-1, 1):
        ctx.new_path()
        ctx.arc(sd * 82, -38, 38, PI * 1.12, PI * 1.88)
        ctx.set_source_rgba(*INK)
        ctx.set_line_width(18)
        ctx.stroke()
        ell(ctx, sd * 132, 28, 34, 20)
        setc(ctx, "#ff6f91", 0.55)
        ctx.fill()

    def mouth():
        ctx.new_path()
        ctx.move_to(-110, 12)
        ctx.curve_to(-100, 160, 100, 160, 110, 12)
        ctx.close_path()

    mouth()
    ctx.save()
    ctx.clip_preserve()
    fill_ol(ctx, "#7a1f2b", ol)
    rrect(ctx, -84, 4, 168, 28, 8)
    setc(ctx, "#ffffff")
    ctx.fill()
    ell(ctx, 0, 124, 60, 34)
    setc(ctx, "#ff7f9b")
    ctx.fill()
    ctx.restore()
    mouth()
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(ol)
    ctx.stroke()
    ctx.restore()


def wordmark(ctx, cx, cy, size, word=NAME, max_w=None):
    """Bouncy multi-colour sticker letters centred on (cx, cy); shrinks to fit max_w. Returns width."""
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)

    def advances():
        return [ctx.text_extents(ch)[4] * (0.97 if ch != " " else 1.6) for ch in word]

    adv = advances()
    if max_w and sum(adv) + size * 0.3 > max_w:
        size *= max_w / (sum(adv) + size * 0.3)
        ctx.set_font_size(size)
        adv = advances()
    total = sum(adv)
    cols, k = [], 0
    for ch in word:
        cols.append(LETTER_COLS[k % len(LETTER_COLS)])
        k += ch != " "
    # passes drawn across all letters so outlines never cut into neighbours
    for pass_ in ("shadow", "white", "main"):
        x = cx - total / 2
        for i, ch in enumerate(word):
            if ch == " ":
                x += adv[i]
                continue
            ctx.save()
            ox, oy = (size * 0.04, size * 0.08) if pass_ == "shadow" else (0, 0)
            ctx.translate(x + adv[i] / 2 + ox, cy + (-0.05 if i % 2 else 0.03) * size + oy)
            ctx.rotate(-0.06 if i % 2 else 0.05)
            if pass_ == "shadow":
                mv.text(ctx, ch, 0, 0, size, (0.09, 0.07, 0.10, 0.85), ol=size * 0.32)
            elif pass_ == "white":
                # dark rim then white sticker border
                mv.text(ctx, ch, 0, 0, size, "#ffffff", ol=size * 0.32)
                xb, yb, tw, th, _, _ = ctx.text_extents(ch)
                ctx.new_path()
                ctx.move_to(-tw / 2 - xb, -th / 2 - yb)
                ctx.text_path(ch)
                setc(ctx, "#ffffff")
                ctx.set_line_width(size * 0.22)
                ctx.set_line_join(cairo.LINE_JOIN_ROUND)
                ctx.stroke()
            else:
                mv.text(ctx, ch, 0, 0, size, cols[i], ol=size * 0.1)
            ctx.restore()
            x += adv[i]
    return total


def pill(ctx, s, cx, cy, size):
    """Dark rounded label sized to its text."""
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    tw = ctx.text_extents(s)[2]
    h = size * 2.0
    pad = size * 1.0
    rrect(ctx, cx - tw / 2 - pad, cy - h / 2, tw + 2 * pad, h, h / 2)
    fill_ol(ctx, "#20232a", size * 0.18)
    mv.text(ctx, s, cx, cy, size, "#ffffff")


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


def confetti(ctx, w, h, seed=4, n=60, avoid=()):
    """Scattered stars and streamers, kept out of the `avoid` rectangles (x0, y0, x1, y1)."""
    rnd = random.Random(seed)
    placed = 0
    while placed < n:
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        col = rnd.choice(LETTER_COLS)
        size, rot, kind = rnd.uniform(10, 24), rnd.uniform(0, PI), rnd.random()
        if any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in avoid):
            continue
        placed += 1
        if kind < 0.5:
            star4(ctx, x, y, size, col, rot)
        else:
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(rot)
            rrect(ctx, -12, -5, 24, 10, 4)
            setc(ctx, col)
            ctx.fill()
            ctx.restore()


def ground(ctx, w, h, top):
    """Soft curved stage floor so characters stand on something."""
    ctx.new_path()
    ctx.move_to(0, top + 30)
    ctx.curve_to(w * 0.3, top - 25, w * 0.7, top - 25, w, top + 30)
    ctx.line_to(w, h)
    ctx.line_to(0, h)
    ctx.close_path()
    g = cairo.LinearGradient(0, top, 0, h)
    g.add_color_stop_rgb(0, *mv.C("#ffb54d")[:3])
    g.add_color_stop_rgb(1, *mv.C("#f08a24")[:3])
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(6)
    ctx.stroke()


def shadow(ctx, x, y, rx):
    ell(ctx, x, y, rx, rx * 0.16)
    setc(ctx, "#000000", 0.18)
    ctx.fill()


def surface(w, h, alpha=False):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32 if alpha else cairo.FORMAT_RGB24, w, h)
    return s, cairo.Context(s)


def cast(ctx, x, y, s, P, expr, look, pose=None, floor=True):
    if floor:
        shadow(ctx, x, y + 14 * s, 170 * s)
    person(ctx, x, y, s, P, expr=expr, t=0.0, look=look, pose=pose, blink=False)


# ---------------------------------------------------------------- assets
def logo(out):
    s, ctx = surface(2000, 1480, alpha=True)
    mascot(ctx, 975, 600, 1.0)
    wordmark(ctx, 1000, 1010, 220, "LAUGHING", max_w=1900)
    wordmark(ctx, 1000, 1270, 220, "BOX")
    s.write_to_png(os.path.join(out, "laughing-box-logo.png"))


def avatar(out, size=800):
    s, ctx = surface(size, size)
    k = size / 800
    ctx.scale(k, k)
    sunburst(ctx, 800, 800, 400, 400)
    dots(ctx, 800, 800, a=0.12)
    # whole mascot stays inside the circular crop (radius 400) with margin
    mascot(ctx, 382, 488, 0.74)
    s.write_to_png(os.path.join(out, f"profile-{size}x{size}.png"))


def watermark(out):
    s, ctx = surface(300, 300, alpha=True)
    ell(ctx, 150, 150, 145, 145)
    setc(ctx, SUN)
    ctx.fill_preserve()
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(8)
    ctx.stroke()
    mascot(ctx, 140, 178, 0.31, ha=False)
    s.write_to_png(os.path.join(out, "watermark-300x300.png"))


def youtube_banner(out):
    W, H = 2560, 1440
    s, ctx = surface(W, H)
    sunburst(ctx, W, H, W / 2, 720)
    dots(ctx, W, H, a=0.1)
    ground(ctx, W, H, 1330)
    confetti(ctx, W, H, n=110, avoid=[(560, 450, 2010, 960), (0, 1300, W, H)])
    # characters sit outside the 1546x423 all-device safe area; heads show on desktop, full bodies on TV
    cast(ctx, 150, 1370, 0.56, SHOPPER, "wink", (0.8, 0), dict(thumb=True, ra1=165, ra2=175))
    cast(ctx, 420, 1380, 0.64, GRANDPA, "victory", (0.6, 0), dict(ra1=150, ra2=165))
    cast(ctx, 2140, 1380, 0.62, GRANDMA, "happy", (-0.6, 0))
    cast(ctx, 2410, 1370, 0.56, TEEN, "happy", (-0.8, 0), dict(la1=-160, la2=-170))
    # logo + tagline inside the safe area (x 507-2053, y 508-931)
    mascot(ctx, 760, 780, 0.5)
    wordmark(ctx, 1490, 670, 150, max_w=1060)
    pill(ctx, TAGLINE, 1490, 830, 52)
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
    confetti(ctx, W, H, seed=9, n=70, avoid=[(300, 50, 1360, 510)])
    # characters peek in from the edges; logo/text stay in the centre that mobile keeps
    cast(ctx, 160, 1060, 0.62, GRANDPA, "victory", (0.6, 0), dict(la1=-155, la2=-170), floor=False)
    cast(ctx, 1490, 1060, 0.6, GRANDMA, "happy", (-0.6, 0), dict(ra1=155, ra2=170), floor=False)
    mascot(ctx, 460, 390, 0.46)
    wordmark(ctx, 1010, 185, 100, "LAUGHING", max_w=680)
    wordmark(ctx, 1010, 300, 100, "BOX")
    pill(ctx, TAGLINE, 1010, 425, 36)
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
