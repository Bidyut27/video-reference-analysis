#!/usr/bin/env python3
"""Render the 9:16 cover for "Grandpa's First Flight".

  python make_thumbnail.py OUT_DIR    # writes cover-1080x1920.png
"""
import os
import sys

import ep1

th = ep1.thumb()
ep6 = ep1.load(os.path.join(ep1.HERE, "make_video.py"), "ep6_video")
mv = ep6.mv


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else ep1.HERE
    W, H = 1080, 1920
    s_, ctx = th.mb.surface(W, H)
    th.background(ctx, W, H, 540, 1150)
    # headline inside the 3:4 centre Instagram keeps on the profile grid (y 240-1680)
    th.big_text(ctx, "GRANDPA'S", W / 2, 320, 150)
    th.big_text(ctx, "FIRST", W / 2, 470, 120, "#ff3b3b")
    th.big_text(ctx, "FLIGHT", W / 2, 615, 150, "#ffffff")
    ep6.window(ctx, 540, 1180, 380, 470, "clouds", 1.0, frame=50)
    ep6.plane(ctx, 650, 900, 0.45, 0.0)
    s = 1.25
    mv.cu(ctx, mv.GRANDPA, "shock", 0.0, hx=540, hy=1230, s=s, blink=False, look=(0, 0.2))
    ep6.vest(ctx, 540, 1230 + 900 * s, s, 1.0, 0.0)
    for x, y, r in ((110, 780, 24), (980, 760, 22), (110, 1560, 20), (980, 1580, 24)):
        mv.star4(ctx, x, y, r, "#ffffff")
    s_.write_to_png(os.path.join(out, "cover-1080x1920.png"))
    print("written to", out)


if __name__ == "__main__":
    main()
