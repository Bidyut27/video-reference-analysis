#!/usr/bin/env python3
"""Render thumbnails for Grandpa vs. the Self-Checkout with Cairo.

  python make_thumbnail.py OUT_DIR

Writes cover-1080x1920.png (9:16 cover for Shorts / Reels).
"""
import os
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "brand-kit"))
import make_branding as mb  # noqa: E402
import make_video as mv  # noqa: E402
from make_video import GRANDPA, glow, impact_star, kiosk, person, star4  # noqa: E402


def big_text(ctx, s, x, y, size, col="#ffd23f"):
    """Thumbnail headline: drop shadow, thick black outline, bright fill."""
    mv.text(ctx, s, x + size * 0.05, y + size * 0.08, size, (0, 0, 0, 0.55), ol=size * 0.24)
    mv.text(ctx, s, x, y, size, col, ol=size * 0.2)


def background(ctx, w, h, cx, cy):
    mb.sunburst(ctx, w, h, cx, cy, c1="#fff3b0", c2="#ff5a36", n=22)
    mb.dots(ctx, w, h, a=0.08)


def anger(ctx, x, y, r):
    """Cartoon anger vein mark."""
    ctx.save()
    ctx.translate(x, y)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(4):
        ctx.save()
        ctx.rotate(k * mv.PI / 2)
        ctx.new_path()
        ctx.move_to(r * 0.25, -r)
        ctx.curve_to(r * 0.25, -r * 0.35, r * 0.35, -r * 0.25, r, -r * 0.25)
        ctx.set_source_rgba(*mv.INK)
        ctx.set_line_width(r * 0.5)
        ctx.stroke_preserve()
        mv.setc(ctx, "#ff2a2a")
        ctx.set_line_width(r * 0.28)
        ctx.stroke()
        ctx.restore()
    ctx.restore()


def grandpa(ctx, x, base, s):
    person(ctx, x, base, s, GRANDPA, expr="furious", t=0.0, look=(1, 0), blink=False,
           pose=dict(la1=-150, la2=-170, ra1=60, ra2=80, lean=4), hold={1: "melon"})


def vertical(out):
    W, H = 1080, 1920
    s, ctx = mb.surface(W, H)
    background(ctx, W, H, 760, 1150)
    glow(ctx, 780, 1150, 380, "#ff2a2a", 0.45)
    impact_star(ctx, 780, 1150, 260, seed=3)
    kiosk(ctx, 780, 2330, 1.25, "x")
    grandpa(ctx, 320, 2400, 1.35)
    anger(ctx, 480, 900, 46)
    # headline kept inside the 3:4 centre Instagram shows on the profile grid (y 240-1680)
    big_text(ctx, "GRANDPA", W / 2, 360, 170)
    big_text(ctx, "VS", W / 2, 520, 120, "#ff3b3b")
    big_text(ctx, "THE MACHINE", W / 2, 670, 130, "#ffffff")
    for x, y, r in ((120, 820, 26), (980, 760, 22), (560, 1500, 20)):
        star4(ctx, x, y, r, "#ffffff")
    s.write_to_png(os.path.join(out, "cover-1080x1920.png"))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    os.makedirs(out, exist_ok=True)
    vertical(out)
    print("written to", out)


if __name__ == "__main__":
    main()
