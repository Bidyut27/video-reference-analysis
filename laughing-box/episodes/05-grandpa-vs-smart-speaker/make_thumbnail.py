#!/usr/bin/env python3
"""Render the 9:16 cover for "Grandpa vs. the Smart Speaker".

  python make_thumbnail.py OUT_DIR    # writes cover-1080x1920.png
"""
import math
import os
import sys

import ep1

th = ep1.thumb()
ep5 = ep1.load(os.path.join(ep1.HERE, "make_video.py"), "ep5_video")
mv = ep5.mv


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else ep1.HERE
    W, H = 1080, 1920
    s_, ctx = th.mb.surface(W, H)
    th.background(ctx, W, H, 540, 1150)
    mv.glow(ctx, 760, 1450, 420, "#2fb7ff", 0.45)
    # headline inside the 3:4 centre Instagram keeps on the profile grid (y 240-1680)
    th.big_text(ctx, "GRANDPA", W / 2, 330, 170)
    th.big_text(ctx, "VS THE", W / 2, 480, 110, "#ff3b3b")
    th.big_text(ctx, "SPEAKER", W / 2, 620, 140, "#ffffff")
    ep5.feathers(ctx, 0.7, n=14, seed=5, area=(40, 720, 1040, 1660), speed=0)
    mv.cu(ctx, mv.GRANDPA, "furious", 0.0, hx=360, hy=1120, s=1.3, blink=False, look=(1, 0.5),
          pose=dict(ra1=80, ra2=60))
    for i in range(3):
        a = -0.4 + i * 0.4
        mv.stroke_line(ctx, [(560 + 70 * math.cos(a), 1200 + 70 * math.sin(a)),
                             (560 + 150 * math.cos(a), 1200 + 150 * math.sin(a))], 12)
    ep5.speaker(ctx, 800, 1620, 1.3, 0.0, "party")
    for i, (x, y) in enumerate(((880, 820), (700, 900))):
        ep5.duck(ctx, x, y, 0.7, i)
    for x, y, r in ((110, 760, 24), (980, 1080, 22), (120, 1600, 20)):
        mv.star4(ctx, x, y, r, "#ffffff")
    s_.write_to_png(os.path.join(out, "cover-1080x1920.png"))
    print("written to", out)


if __name__ == "__main__":
    main()
