#!/usr/bin/env python3
"""Render the 9:16 cover for "Grandpa vs. the Video Call".

  python make_thumbnail.py OUT_DIR    # writes cover-1080x1920.png
"""
import os
import sys

import ep1

th = ep1.thumb()
ep2 = ep1.load(os.path.join(ep1.HERE, "make_video.py"), "ep2_video")
mv = ep2.mv


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else ep1.HERE
    W, H = 1080, 1920
    s_, ctx = th.mb.surface(W, H)
    th.background(ctx, W, H, 540, 1250)
    mv.glow(ctx, 560, 1250, 520, "#ff2a2a", 0.35)
    mv.impact_star(ctx, 560, 1230, 430, seed=5)
    # headline inside the 3:4 centre Instagram keeps on the profile grid (y 240-1680)
    th.big_text(ctx, "GRANDPA", W / 2, 330, 170)
    th.big_text(ctx, "VS THE", W / 2, 480, 110, "#ff3b3b")
    th.big_text(ctx, "VIDEO CALL", W / 2, 620, 125, "#ffffff")
    s = 3.9
    ctx.save()
    ctx.translate(560, 1310)
    ctx.rotate(-0.07)
    mv.rrect(ctx, -80 * s, -150 * s, 160 * s, 300 * s, 26 * s)
    mv.fill_ol(ctx, "#22252c", 12)
    ep2.draw_view(ctx, "nose", 0.4, (-70 * s, -135 * s, 140 * s, 270 * s), expr="neutral")
    pip = (12 * s, -125 * s, 48 * s, 70 * s)
    ep2.draw_view(ctx, "leo", 0.0, pip, expr="shock")
    mv.rrect(ctx, *pip, 26)
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.restore()
    for x, y, r in ((110, 820, 26), (980, 860, 22), (150, 1600, 20), (960, 1560, 24)):
        mv.star4(ctx, x, y, r, "#ffffff")
    s_.write_to_png(os.path.join(out, "cover-1080x1920.png"))
    print("written to", out)


if __name__ == "__main__":
    main()
