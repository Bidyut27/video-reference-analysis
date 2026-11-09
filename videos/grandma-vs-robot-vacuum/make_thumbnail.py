#!/usr/bin/env python3
"""Render the 9:16 cover for "Grandma vs. the Robot Vacuum".

  python make_thumbnail.py OUT_DIR    # writes cover-1080x1920.png
"""
import os
import sys

import ep1

th = ep1.thumb()
ep3 = ep1.load(os.path.join(ep1.HERE, "make_video.py"), "ep3_video")
mv = ep3.mv


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else ep1.HERE
    W, H = 1080, 1920
    s_, ctx = th.mb.surface(W, H)
    th.background(ctx, W, H, 540, 1150)
    mv.glow(ctx, 540, 1150, 520, "#ff4d8d", 0.3)
    # headline inside the 3:4 centre Instagram keeps on the profile grid (y 240-1680)
    th.big_text(ctx, "GRANDMA", W / 2, 330, 170)
    th.big_text(ctx, "VS THE", W / 2, 480, 110, "#ff3b3b")
    th.big_text(ctx, "ROBOT", W / 2, 620, 150, "#ffffff")
    # Grandpa riding Cookie in the background
    ctx.save()
    ctx.translate(880, 1240)
    ctx.rotate(0.12)
    ctx.translate(-880, -1240)
    ep3.vacuum(ctx, 880, 1240, 0.6, 0.3, face=-1, moving=True, bow_col=ep3.BLUE, led="#ff3b3b")
    mv.person(ctx, 870, 1240 - 52, 0.5, mv.GRANDPA, expr="shock", t=0.0, look=(-0.8, 0), blink=False,
              pose=dict(lean=-10, la1=-120, la2=-170, ra1=120, ra2=170))
    ctx.restore()
    for i in range(4):
        mv.stroke_line(ctx, [(1010 + i * 10, 1080 + i * 30), (1080, 1080 + i * 30)], 8, (1, 1, 1, 0.8))
    # Grandma hugging Biscuit
    mv.cu(ctx, mv.GRANDMA, "happy", 0.0, hx=420, hy=1130, s=1.45, blink=False)
    ep3.held_vacuum(ctx, 420, 1640, 1.15, 0.0, mv.GRANDMA)
    for x, y in ((200, 860), (660, 820), (150, 1380)):
        mv.heart(ctx, x, y, 34)
        mv.setc(ctx, ep3.PINK)
        ctx.fill()
    for x, y, r in ((110, 760, 24), (980, 760, 22), (980, 1640, 20)):
        mv.star4(ctx, x, y, r, "#ffffff")
    s_.write_to_png(os.path.join(out, "cover-1080x1920.png"))
    print("written to", out)


if __name__ == "__main__":
    main()
