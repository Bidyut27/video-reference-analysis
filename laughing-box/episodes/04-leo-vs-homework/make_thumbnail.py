#!/usr/bin/env python3
"""Render the 9:16 cover for "Leo vs. Homework".

  python make_thumbnail.py OUT_DIR    # writes cover-1080x1920.png
"""
import os
import sys

import ep1

th = ep1.thumb()
ep4 = ep1.load(os.path.join(ep1.HERE, "make_video.py"), "ep4_video")
mv = ep4.mv


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else ep1.HERE
    W, H = 1080, 1920
    s_, ctx = th.mb.surface(W, H)
    th.background(ctx, W, H, 540, 1150)
    mv.glow(ctx, 540, 1150, 520, "#2fb7ff", 0.3)
    # headline inside the 3:4 centre Instagram keeps on the profile grid (y 240-1680)
    th.big_text(ctx, "LEO", W / 2, 330, 190)
    th.big_text(ctx, "VS", W / 2, 490, 120, "#ff3b3b")
    th.big_text(ctx, "HOMEWORK", W / 2, 635, 140, "#ffffff")
    mv.cu(ctx, ep4.LEO, "shock", 0.0, hx=540, hy=1000, s=1.35, blink=False, look=(0, 0.3),
          pose=dict(la1=-60, la2=-160, ra1=60, ra2=160))
    base = 1810
    for i, (title, col, w) in enumerate((("HISTORY", "#9b6bff", 820), ("SCIENCE", "#25c486", 760),
                                         ("ENGLISH", "#2fb7ff", 700), ("MATH", "#e53935", 640))):
        ep4.book(ctx, 540 + (i % 2) * 24 - 12, base - i * 130, w, 130, col, title, tilt=(-0.03 if i % 2 else 0.03))
    ep4.cat(ctx, 760, base - 4 * 130 + 6, 0.62, "smug", 0.0, look=(-0.6, 0))
    for x, y, r in ((110, 760, 24), (980, 760, 22), (120, 1560, 20), (980, 1600, 24)):
        mv.star4(ctx, x, y, r, "#ffffff")
    s_.write_to_png(os.path.join(out, "cover-1080x1920.png"))
    print("written to", out)


if __name__ == "__main__":
    main()
