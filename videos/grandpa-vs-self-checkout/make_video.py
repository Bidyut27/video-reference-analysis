#!/usr/bin/env python3
"""Render the picture for "Grandpa vs. the Self-Checkout", an original wordless 9:16 cartoon.

Every character, prop and background is drawn procedurally with Cairo, so no
third-party artwork is used.

  python make_video.py --stills out_dir   # one PNG per shot (for review)
  python make_video.py picture.mp4        # full render, silent H.264
"""
import math
import os
import random
import subprocess
import sys
from multiprocessing import Pool

import cairo

from timeline import FPS, H, SHOTS, TOTAL, W

PI = math.pi
INK = (0.09, 0.07, 0.10, 1.0)
OL = 7.0


# ---------------------------------------------------------------- helpers
def C(h, a=1.0):
    if isinstance(h, tuple):
        return h if len(h) == 4 else (*h, a)
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def setc(ctx, c, a=None):
    c = C(c)
    if a is not None:
        c = (c[0], c[1], c[2], a)
    ctx.set_source_rgba(*c)


def darker(c, k=0.85):
    c = C(c)
    return (c[0] * k, c[1] * k, c[2] * k, c[3])


def fill_ol(ctx, c, ol=OL):
    setc(ctx, c)
    ctx.fill_preserve()
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(ol)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()


def ell(ctx, x, y, rx, ry):
    ctx.new_sub_path()
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.arc(0, 0, 1, 0, 2 * PI)
    ctx.restore()


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -PI / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, PI / 2)
    ctx.arc(x + r, y + h - r, r, PI / 2, PI)
    ctx.arc(x + r, y + r, r, PI, 1.5 * PI)
    ctx.close_path()


def poly(ctx, pts, close=False):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()


def stroke_line(ctx, pts, w, c=INK):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    poly(ctx, pts)
    setc(ctx, c)
    ctx.set_line_width(w)
    ctx.stroke()


def limb(ctx, pts, w, c, ol=OL):
    stroke_line(ctx, pts, w + 2 * ol, INK)
    stroke_line(ctx, pts, w, c)


def text(ctx, s, x, y, size, col="#ffffff", ol=0.0, font="DejaVu Sans", align="c"):
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    xb, yb, tw, th, xa, _ = ctx.text_extents(s)
    px = {"c": x - tw / 2 - xb, "l": x, "r": x - xa}[align]
    ctx.new_path()
    ctx.move_to(px, y - th / 2 - yb)
    ctx.text_path(s)
    if ol:
        ctx.set_source_rgba(*INK)
        ctx.set_line_width(ol)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
    setc(ctx, col)
    ctx.fill()


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def eio(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def eout(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def eback(t):
    t = clamp(t)
    c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def flash(t, times, k=4.0):
    return max([math.exp(-(t - x) * k) for x in times if t >= x] or [0.0])


def shake(t, t0, amp, decay=7.0):
    return amp * math.exp(-(t - t0) * decay) if t >= t0 else 0.0


def cam(ctx, z=1.0, fx=W / 2, fy=H / 2, rot=0.0, shake_amp=0.0, seed=0):
    rnd = random.Random(seed)
    sx, sy = rnd.uniform(-1, 1) * shake_amp, rnd.uniform(-1, 1) * shake_amp
    ctx.translate(W / 2 + sx, H / 2 + sy)
    ctx.rotate(rot)
    ctx.scale(z, z)
    ctx.translate(-fx, -fy)


# ---------------------------------------------------------------- characters
GRANDPA = dict(skin="#f1c09a", top="#e3a72f", sleeve="#e3a72f", style="cardigan", pants="#6b4a2f",
               shoe="#3a2a20", hair="sides", hair_c="#f4f3ee", brow="#f4f3ee", brow_w=0.1,
               moustache=True, glasses=True, nose="big")
GRANDMA = dict(skin="#f3c7a5", top="#b78ad8", sleeve="#b78ad8", style="dress", pants="#e2c8b4",
               shoe="#5b3d6b", hair="grey_bun", hair_c="#cfd0d8", brow="#8f8f9c", nose="small")
TEEN = dict(skin="#e3ad84", top="#f6efe2", sleeve="#f6efe2", style="apron", apron="#1fa59a",
            pants="#2f3b52", shoe="#222222", hair="spiky", hair_c="#2b1d14", brow="#2b1d14",
            nose="small", freckles=True)
SHOPPER = dict(skin="#d39b74", top="#5bb04a", sleeve="#5bb04a", style="hoodie", pants="#3b4a6b",
               shoe="#222222", hair="ball_cap", hair_c="#e85d3a", brow="#3a2414", beard="#5a3a22",
               nose="small", wide=1.35)
Q_WOMAN = dict(skin="#c98e66", top="#e86fa0", sleeve="#e86fa0", style="plain", pants="#34344a",
               shoe="#222222", hair="long", hair_c="#3a2a1a", brow="#3a2a1a", nose="small")
Q_OLDMAN = dict(skin="#efc3a0", top="#7d8c99", sleeve="#7d8c99", style="plain", pants="#4a4038",
                shoe="#2a2a2a", hair="bald_ring", hair_c="#bdbdbd", brow="#9a9a9a", nose="big",
                glasses=True)
Q_KID = dict(skin="#e8b48c", top="#ffcf33", sleeve="#ffcf33", style="plain", pants="#3a6fd8",
             shoe="#e94f37", hair="spiky", hair_c="#6b3d1f", brow="#6b3d1f", nose="small")

BROWS = {"neutral": (0, 0), "smug": (0.02, -0.06), "furious": (0.13, -0.05), "shock": (-0.14, -0.12),
         "cry": (-0.1, 0.05), "happy": (-0.06, -0.06), "victory": (-0.08, -0.08),
         "nervous": (-0.09, 0.03), "wink": (-0.05, -0.05), "yawn": (-0.03, -0.03)}


def hair_front(ctx, x, y, r, hs, hc, ol):
    if hs in ("sides", "bald_ring"):
        k = 1.0 if hs == "sides" else 0.8
        blobs = [(0.92, -0.33, 0.2), (1.0, -0.08, 0.23), (0.9, 0.14, 0.17)]
        for s in (-1, 1):
            for bx, by, br in blobs:
                ell(ctx, x + s * bx * r, y + by * r, br * r * k, br * r * k)
                fill_ol(ctx, hc, ol)
        for s in (-1, 1):
            for bx, by, br in blobs:
                ell(ctx, x + s * bx * r, y + by * r, br * r * k - ol * 0.7, br * r * k - ol * 0.7)
                setc(ctx, hc)
                ctx.fill()
        ell(ctx, x - 0.32 * r, y - 0.7 * r, 0.2 * r, 0.09 * r)
        setc(ctx, "#ffffff", 0.45)
        ctx.fill()
        if hs == "sides":
            for dx in (-0.08, 0.06):
                ctx.new_path()
                ctx.arc(x + dx * r, y - 1.12 * r, 0.09 * r, PI * 0.6, PI * 1.9)
                ctx.set_source_rgba(*INK)
                ctx.set_line_width(ol * 0.8)
                ctx.stroke()
    elif hs == "spiky":
        ctx.new_path()
        ctx.arc(x, y, r * 1.05, PI * 1.0, PI * 2.0)
        n = 7
        for i in range(n + 1):
            px = x + r * 1.02 - i * (2.04 * r / n)
            py = y - (0.3 if i % 2 == 0 else 0.55) * r
            ctx.line_to(px, py)
        ctx.close_path()
        fill_ol(ctx, hc, ol)
    elif hs in ("grey_bun", "long"):
        ctx.new_path()
        ctx.arc(x, y, r * 1.06, PI * 0.95, PI * 2.05)
        ctx.line_to(x + 0.9 * r, y - 0.15 * r)
        ctx.curve_to(x + 0.55 * r, y - 0.75 * r, x + 0.15 * r, y - 0.62 * r, x, y - 0.5 * r)
        ctx.curve_to(x - 0.15 * r, y - 0.62 * r, x - 0.55 * r, y - 0.75 * r, x - 0.9 * r, y - 0.15 * r)
        ctx.close_path()
        fill_ol(ctx, hc, ol)
    elif hs == "ball_cap":
        ctx.new_path()
        ctx.arc(x, y - 0.4 * r, r * 0.97, PI, 2 * PI)
        ctx.close_path()
        fill_ol(ctx, hc, ol)
        ell(ctx, x + 0.55 * r, y - 0.42 * r, 0.62 * r, 0.11 * r)
        fill_ol(ctx, darker(hc), ol)
        ell(ctx, x, y - 1.37 * r, 0.09 * r, 0.06 * r)
        fill_ol(ctx, darker(hc), ol)


def glasses(ctx, x, y, r, ol, lens=0.24):
    ey = y - 0.06 * r
    for s in (-1, 1):
        ctx.new_path()
        ctx.arc(x + s * 0.34 * r, ey, r * lens, 0, 2 * PI)
        setc(ctx, "#ffffff", 0.16)
        ctx.fill_preserve()
        ctx.set_source_rgba(*INK)
        ctx.set_line_width(r * 0.035)
        ctx.stroke()
        stroke_line(ctx, [(x + s * (0.34 + lens) * r, ey), (x + s * 0.95 * r, ey - 0.05 * r)], r * 0.03)
    stroke_line(ctx, [(x - (0.34 - lens) * r, ey), (x + (0.34 - lens) * r, ey)], r * 0.035)


def face(ctx, x, y, r, expr, P, t=0.0, look=(0, 0), glasses_y=None, blink=False):
    ol = max(3.0, r * 0.035)
    hs, hc, skin = P.get("hair"), P.get("hair_c", "#333333"), P["skin"]
    if hs == "grey_bun":
        ell(ctx, x, y - r * 1.02, r * 0.45, r * 0.38)
        fill_ol(ctx, hc, ol)
    if hs == "long":
        rrect(ctx, x - r * 1.15, y - r * 0.9, r * 2.3, r * 2.0, r * 0.9)
        fill_ol(ctx, hc, ol)
    for s in (-1, 1):
        ell(ctx, x + s * r * 0.97, y + r * 0.08, r * 0.17, r * 0.24)
        fill_ol(ctx, skin, ol)
    ell(ctx, x, y, r, r * 1.04)
    fill_ol(ctx, skin, ol)
    if expr == "furious":
        ell(ctx, x, y + 0.1 * r, r - ol, r * 0.94 - ol)
        setc(ctx, "#ff2a2a", 0.25)
        ctx.fill()
    hair_front(ctx, x, y, r, hs, hc, ol)
    if expr in ("happy", "smug", "victory", "nervous", "wink"):
        for s in (-1, 1):
            ell(ctx, x + s * 0.58 * r, y + 0.22 * r, 0.16 * r, 0.09 * r)
            setc(ctx, "#ff6f91", 0.35)
            ctx.fill()
    if P.get("freckles"):
        setc(ctx, "#b5714a")
        for s in (-1, 1):
            for fx, fy in ((0.5, 0.18), (0.6, 0.24), (0.45, 0.27)):
                ell(ctx, x + s * fx * r, y + fy * r, 0.022 * r, 0.022 * r)
                ctx.fill()

    # eyes
    er = r * 0.155
    for s in (-1, 1):
        ex, ey = x + s * r * 0.34, y - r * 0.06
        if expr in ("happy", "victory") or (expr == "wink" and s == 1):
            ctx.new_path()
            ctx.arc(ex, ey + er * 0.5, er * 0.85, PI * 1.15, PI * 1.85)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_source_rgba(*INK)
            ctx.set_line_width(r * 0.05)
            ctx.stroke()
        elif expr == "cry":
            ctx.new_path()
            ctx.arc(ex, ey - er * 0.6, er * 0.85, PI * 0.15, PI * 0.85)
            ctx.set_source_rgba(*INK)
            ctx.set_line_width(r * 0.05)
            ctx.stroke()
        elif expr == "yawn" or blink:
            stroke_line(ctx, [(ex - er, ey), (ex + er, ey)], r * 0.045)
        else:
            sx, sy, pr = 1.0, 1.2, 0.5
            if expr == "shock":
                sx, sy, pr = 1.3, 1.45, 0.22
            elif expr == "furious":
                sy, pr = 0.85, 0.36
            elif expr == "nervous":
                pr = 0.3
            if expr == "suspicious" and s == -1:
                sy = 0.45
            ell(ctx, ex, ey, er * sx, er * sy)
            fill_ol(ctx, "#ffffff", ol * 0.8)
            px, py = ex + look[0] * er * sx * 0.45, ey + look[1] * er * sy * 0.45
            ell(ctx, px, py, er * pr, er * pr * 1.1)
            ctx.set_source_rgba(*INK)
            ctx.fill()
            ell(ctx, px - er * pr * 0.35, py - er * pr * 0.4, er * pr * 0.32, er * pr * 0.32)
            setc(ctx, "#ffffff")
            ctx.fill()
            if expr == "smug":
                ctx.save()
                ell(ctx, ex, ey, er * sx, er * sy)
                ctx.clip()
                ctx.rectangle(ex - 2 * er, ey - 2 * er, 4 * er, 1.9 * er)
                setc(ctx, skin)
                ctx.fill()
                ctx.restore()
                stroke_line(ctx, [(ex - er, ey - 0.1 * er), (ex + er, ey - 0.1 * er)], ol)
        # brows
        if expr == "suspicious":
            di, do = (0.07, 0.07) if s == -1 else (-0.1, -0.15)
        else:
            di, do = BROWS.get(expr, (0, 0))
        by = ey - r * (0.4 if expr == "shock" else 0.3)
        limb(ctx, [(ex - s * r * 0.15, by + di * r), (ex + s * r * 0.15, by + do * r)],
             r * P.get("brow_w", 0.06), P["brow"], ol * 0.7)

    if P.get("beard"):
        ctx.new_path()
        ctx.move_to(x - 0.97 * r, y)
        ctx.curve_to(x - 0.95 * r, y + 1.25 * r, x + 0.95 * r, y + 1.25 * r, x + 0.97 * r, y)
        ctx.line_to(x + 0.7 * r, y + 0.15 * r)
        ctx.curve_to(x + 0.4 * r, y + 0.3 * r, x - 0.4 * r, y + 0.3 * r, x - 0.7 * r, y + 0.15 * r)
        ctx.close_path()
        fill_ol(ctx, P["beard"], ol)

    # mouth
    my = y + (0.6 if P.get("moustache") else 0.47) * r
    dark = "#7a1f2b"
    if expr in ("happy", "victory", "wink"):
        ctx.new_path()
        ctx.move_to(x - 0.25 * r, my - 0.04 * r)
        ctx.curve_to(x - 0.2 * r, my + 0.3 * r, x + 0.2 * r, my + 0.3 * r, x + 0.25 * r, my - 0.04 * r)
        ctx.close_path()
        ctx.save()
        ctx.clip_preserve()
        fill_ol(ctx, dark, ol)
        ell(ctx, x, my + 0.22 * r, 0.14 * r, 0.08 * r)
        setc(ctx, "#ff7f9b")
        ctx.fill()
        ctx.restore()
    elif expr == "shock":
        ell(ctx, x, my + 0.06 * r, 0.12 * r, 0.17 * r)
        fill_ol(ctx, dark, ol)
    elif expr == "yawn":
        ell(ctx, x, my + 0.08 * r, 0.17 * r, 0.23 * r)
        fill_ol(ctx, dark, ol)
    elif expr in ("furious", "nervous"):
        hw = 0.22 if expr == "furious" else 0.3
        rrect(ctx, x - hw * r, my - 0.07 * r, 2 * hw * r, 0.15 * r, 0.05 * r)
        fill_ol(ctx, "#ffffff", ol)
        n = 4 if expr == "furious" else 6
        for i in range(1, n):
            lx = x - hw * r + i * 2 * hw * r / n
            stroke_line(ctx, [(lx, my - 0.07 * r), (lx, my + 0.08 * r)], ol * 0.6)
        stroke_line(ctx, [(x - hw * r, my + 0.005 * r), (x + hw * r, my + 0.005 * r)], ol * 0.6)
    elif expr == "cry":
        ctx.new_path()
        pts_top = [(x - 0.22 * r + i * 0.044 * r, my - 0.02 * r + 0.03 * r * math.sin(i * 1.3 + t * 20)) for i in range(11)]
        pts_bot = [(x + 0.22 * r - i * 0.044 * r, my + 0.16 * r + 0.03 * r * math.sin(i * 1.7 + t * 18)) for i in range(11)]
        poly(ctx, pts_top + pts_bot, close=True)
        fill_ol(ctx, dark, ol)
    elif expr == "smug":
        ctx.new_path()
        ctx.move_to(x - 0.18 * r, my + 0.03 * r)
        ctx.curve_to(x - 0.05 * r, my + 0.09 * r, x + 0.12 * r, my + 0.05 * r, x + 0.23 * r, my - 0.09 * r)
        ctx.set_source_rgba(*INK)
        ctx.set_line_width(r * 0.045)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    elif expr == "suspicious":
        stroke_line(ctx, [(x - 0.15 * r, my + 0.02 * r), (x + 0.15 * r, my - 0.04 * r)], r * 0.045)
    else:
        ctx.new_path()
        ctx.arc(x, my - 0.14 * r, 0.17 * r, PI * 0.3, PI * 0.7)
        ctx.set_source_rgba(*INK)
        ctx.set_line_width(r * 0.045)
        ctx.stroke()

    if P.get("moustache"):
        for s in (-1, 1):
            ctx.new_path()
            ctx.move_to(x, y + 0.32 * r)
            ctx.curve_to(x + s * 0.2 * r, y + 0.16 * r, x + s * 0.52 * r, y + 0.2 * r, x + s * 0.58 * r, y + 0.44 * r)
            ctx.curve_to(x + s * 0.42 * r, y + 0.4 * r, x + s * 0.25 * r, y + 0.52 * r, x, y + 0.45 * r)
            ctx.close_path()
            fill_ol(ctx, P["hair_c"], ol)
    if P.get("nose") == "big":
        ell(ctx, x, y + 0.2 * r, 0.17 * r, 0.14 * r)
        fill_ol(ctx, darker(skin, 0.93), ol)
    else:
        ell(ctx, x, y + 0.17 * r, 0.08 * r, 0.06 * r)
        fill_ol(ctx, darker(skin, 0.93), ol * 0.7)
    if P.get("glasses"):
        glasses(ctx, x, y, r, ol)
    if glasses_y is not None:
        glasses(ctx, x, y + glasses_y * r, r, ol, lens=0.21)

    if expr == "cry":
        for s in (-1, 1):
            ex, ey = x + s * r * 0.34, y - r * 0.06
            rrect(ctx, ex - 0.05 * r, ey + 0.02 * r, 0.1 * r, 0.75 * r, 0.05 * r)
            fill_ol(ctx, C("#7fd3ff", 0.9), ol * 0.6)
            for k in range(2):
                ph = (t * 1.8 + k * 0.5 + (0.25 if s > 0 else 0)) % 1
                ell(ctx, ex + s * ph * 0.25 * r, ey + 0.8 * r + ph * 0.6 * r, 0.05 * r, 0.065 * r)
                fill_ol(ctx, "#7fd3ff", ol * 0.5)
    if expr == "nervous":
        dy = (t * 0.6 % 1) * 0.35 * r
        sx, sy, sr = x + 0.8 * r, y - 0.5 * r + dy, 0.09 * r
        ctx.new_path()
        ctx.move_to(sx, sy - 2.2 * sr)
        ctx.curve_to(sx + 0.4 * sr, sy - sr, sx + sr, sy - 0.3 * sr, sx + sr, sy + 0.2 * sr)
        ctx.arc(sx, sy + 0.2 * sr, sr, 0, PI)
        ctx.curve_to(sx - sr, sy - 0.3 * sr, sx - 0.4 * sr, sy - sr, sx, sy - 2.2 * sr)
        ctx.close_path()
        fill_ol(ctx, "#8fdcff", ol * 0.7)


DEFAULT_POSE = dict(la1=-8, la2=-4, ra1=8, ra2=4, ll=0, rl=0, lean=0, bob=0)


def walk_pose(ph, amp=22):
    s = math.sin(ph)
    return dict(ll=amp * s, rl=-amp * s, la1=-6 - 14 * s, la2=-6 - 10 * s, ra1=6 + 14 * s, ra2=6 + 10 * s,
                bob=abs(math.cos(ph)) * 16)


def torso(ctx, P):
    w = P.get("wide", 1.0)
    st = P.get("style", "plain")
    if st == "dress":
        poly(ctx, [(-125 * w, -470), (125 * w, -470), (205 * w, -170), (-205 * w, -170)], close=True)
        fill_ol(ctx, P["top"])
    ctx.new_path()
    ctx.move_to(-110 * w, -735)
    ctx.curve_to(-150 * w, -732, -152 * w, -690, -146 * w, -660)
    ctx.line_to(-126 * w, -305)
    ctx.line_to(126 * w, -305)
    ctx.line_to(146 * w, -660)
    ctx.curve_to(152 * w, -690, 150 * w, -732, 110 * w, -735)
    ctx.close_path()
    fill_ol(ctx, P["top"])
    if st != "dress":
        rrect(ctx, -126 * w, -335, 252 * w, 40, 12)
        fill_ol(ctx, P["pants"])
    if st == "cardigan":
        poly(ctx, [(-42, -735), (42, -735), (26, -335), (-26, -335)], close=True)
        fill_ol(ctx, "#fbf7ee")
        for by in (-640, -540, -440):
            ell(ctx, -54, by, 12, 12)
            fill_ol(ctx, "#7a4b1e", 4)
        for px in (-115, 55):
            rrect(ctx, px, -470, 62, 58, 10)
            fill_ol(ctx, darker(P["top"], 0.9), 5)
    elif st == "apron":
        rrect(ctx, -105, -650, 210, 345, 22)
        fill_ol(ctx, P["apron"])
        stroke_line(ctx, [(-80, -650), (-98, -735)], 16, INK)
        stroke_line(ctx, [(80, -650), (98, -735)], 16, INK)
        rrect(ctx, 25, -610, 60, 32, 6)
        fill_ol(ctx, "#ffffff", 4)
    elif st == "hoodie":
        poly(ctx, [(-80 * w, -470), (80 * w, -470), (100 * w, -360), (-100 * w, -360)], close=True)
        fill_ol(ctx, darker(P["top"], 0.9), 5)
        stroke_line(ctx, [(-28, -725), (-34, -610)], 7, "#ffffff")
        stroke_line(ctx, [(28, -725), (34, -610)], 7, "#ffffff")
    elif st == "dress":
        ell(ctx, 0, -728, 62, 22)
        fill_ol(ctx, "#ffffff", 5)
        for i in range(-3, 4):
            ell(ctx, i * 17, -700 + abs(i) * -4, 8, 8)
            fill_ol(ctx, "#fff8f0", 3)


def melon(ctx, x, y, r, ol=OL):
    ell(ctx, x, y, r, r * 0.92)
    fill_ol(ctx, "#8fce55", ol)
    ctx.save()
    ell(ctx, x, y, r, r * 0.92)
    ctx.clip()
    for k in range(-2, 3):
        ctx.new_path()
        ctx.move_to(x + k * r * 0.35, y - r)
        ctx.curve_to(x + k * r * 0.55, y - r * 0.3, x + k * r * 0.55, y + r * 0.3, x + k * r * 0.35, y + r)
        setc(ctx, "#4f8f2f")
        ctx.set_line_width(r * 0.09)
        ctx.stroke()
    ctx.restore()
    ell(ctx, x - r * 0.35, y - r * 0.4, r * 0.22, r * 0.12)
    setc(ctx, "#ffffff", 0.45)
    ctx.fill()


def person(ctx, x, y, s, P, pose=None, expr="neutral", t=0.0, look=(0, 0), glasses_y=None, blink=None,
           hold=None):
    pz = dict(DEFAULT_POSE)
    pz.update(pose or {})
    if blink is None:
        blink = expr in ("neutral", "smug", "suspicious") and ((t + s * 3) % 2.9) < 0.09
    rad = math.radians
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.translate(0, -pz["bob"])
    w = P.get("wide", 1.0)
    for side, ang in ((-1, pz["ll"]), (1, pz["rl"])):
        hx, hy = side * 58 * w, -330
        fx, fy = hx + math.sin(rad(ang)) * 300, hy + math.cos(rad(ang)) * 300
        limb(ctx, [(hx, hy), (fx, fy)], 78, P["pants"])
        ell(ctx, fx + side * 14, fy + 10, 54, 28)
        fill_ol(ctx, P["shoe"])
    ctx.translate(0, -330)
    ctx.rotate(rad(pz["lean"]))
    ctx.translate(0, 330)
    torso(ctx, P)
    face(ctx, 0, -900, 190, expr, P, t, look, glasses_y, blink)
    hands = {}
    for side, a1, a2 in ((-1, pz["la1"], pz["la2"]), (1, pz["ra1"], pz["ra2"])):
        sx, sy = side * 125 * w, -690
        e = (sx + math.sin(rad(a1)) * 165, sy + math.cos(rad(a1)) * 165)
        hnd = (e[0] + math.sin(rad(a2)) * 155, e[1] + math.cos(rad(a2)) * 155)
        limb(ctx, [(sx, sy), e, hnd], 58, P["sleeve"])
        hands[side] = hnd
        if pz.get("palm") and side == 1:
            for i in range(4):
                rrect(ctx, hnd[0] - 46 + i * 24, hnd[1] - 105, 22, 70, 11)
                fill_ol(ctx, P["skin"])
            ell(ctx, hnd[0], hnd[1] - 20, 54, 56)
            fill_ol(ctx, P["skin"])
        elif pz.get("thumb") and side == 1:
            rrect(ctx, hnd[0] - 12, hnd[1] - 95, 26, 70, 13)
            fill_ol(ctx, P["skin"])
            ell(ctx, hnd[0], hnd[1], 42, 40)
            fill_ol(ctx, P["skin"])
        else:
            ell(ctx, hnd[0], hnd[1], 38, 38)
            fill_ol(ctx, P["skin"])
    for side, item in (hold or {}).items():
        hx, hy = hands[side]
        if item == "melon":
            melon(ctx, hx, hy - 30, 78)
        elif item == "balloon":
            stroke_line(ctx, [(hx, hy), (hx + 20, hy - 330)], 4)
            ell(ctx, hx + 20, hy - 430, 85, 100)
            fill_ol(ctx, "#ff4d6d")
            ell(ctx, hx - 5, hy - 470, 22, 30)
            setc(ctx, "#ffffff", 0.5)
            ctx.fill()
    ctx.restore()


def cu(ctx, P, expr, t, hx=W / 2, hy=1000, s=2.1, **kw):
    person(ctx, hx, hy + 900 * s, s, P, expr=expr, t=t, **kw)


# ---------------------------------------------------------------- props
def xmark(ctx, x, y, s, col, w):
    stroke_line(ctx, [(x - s, y - s), (x + s, y + s)], w, col)
    stroke_line(ctx, [(x - s, y + s), (x + s, y - s)], w, col)


def check(ctx, x, y, s, col, w):
    stroke_line(ctx, [(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.7)], w, col)


def heart(ctx, x, y, s):
    ctx.new_path()
    ctx.move_to(x, y + s * 0.45)
    ctx.curve_to(x - s * 1.1, y - s * 0.25, x - s * 0.5, y - s * 1.0, x, y - s * 0.45)
    ctx.curve_to(x + s * 0.5, y - s * 1.0, x + s * 1.1, y - s * 0.25, x, y + s * 0.45)
    ctx.close_path()


SCREEN_COLS = {"idle": "#3b82f6", "x": "#e53935", "ok": "#43a047", "hearts": "#ff6fa8",
               "glitch": "#111111", "off": "#0d0f14"}


def screen(ctx, x, y, w, h, state, g=0):
    m = min(w, h)
    rrect(ctx, x, y, w, h, m * 0.06)
    setc(ctx, SCREEN_COLS[state])
    ctx.fill()
    cx, cy = x + w / 2, y + h / 2
    ctx.save()
    rrect(ctx, x, y, w, h, m * 0.06)
    ctx.clip()
    if state == "idle":
        for i in range(14):
            bw = (3, 7, 4, 10)[i % 4] * m / 300
            ctx.rectangle(cx - m * 0.3 + i * m * 0.043, cy - m * 0.3, bw, m * 0.3)
            setc(ctx, "#ffffff")
            ctx.fill()
        text(ctx, "SCAN", cx, cy + m * 0.22, m * 0.2)
    elif state == "x":
        xmark(ctx, cx, cy, m * 0.27, "#ffffff", m * 0.11)
    elif state == "ok":
        check(ctx, cx, cy + m * 0.03, m * 0.3, "#ffffff", m * 0.11)
    elif state == "hearts":
        heart(ctx, cx, cy + m * 0.05, m * 0.32)
        setc(ctx, "#ffffff")
        ctx.fill()
    elif state == "glitch":
        rnd = random.Random(g)
        for _ in range(16):
            by, bh = rnd.uniform(y, y + h), rnd.uniform(4, h * 0.08)
            ctx.rectangle(x, by, w, bh)
            setc(ctx, rnd.choice(["#ff2244", "#22ff88", "#2266ff", "#ffffff", "#ff22ff"]), 0.8)
            ctx.fill()
        xmark(ctx, cx + rnd.uniform(-20, 20), cy, m * 0.27, C("#ff2244", 0.7), m * 0.1)
        xmark(ctx, cx + rnd.uniform(-20, 20), cy, m * 0.27, C("#22e6ff", 0.6), m * 0.1)
    poly(ctx, [(x + w * 0.55, y), (x + w * 0.75, y), (x + w * 0.35, y + h), (x + w * 0.15, y + h)], close=True)
    setc(ctx, "#ffffff", 0.1)
    ctx.fill()
    ctx.restore()


def kiosk(ctx, x, y, s, state, g=0, scan=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -110, -640, 220, 640, 20)
    fill_ol(ctx, "#9aa5b5")
    rrect(ctx, -90, -560, 180, 70, 12)
    fill_ol(ctx, "#7d8796")
    rrect(ctx, -190, -700, 380, 90, 18)
    fill_ol(ctx, "#c5ced9")
    rrect(ctx, -120, -690, 240, 40, 10)
    fill_ol(ctx, "#2b2f36")
    if scan > 0:
        rrect(ctx, -110, -675, 220, 10, 5)
        setc(ctx, "#ff3030", scan)
        ctx.fill()
        poly(ctx, [(-100, -672), (100, -672), (40, -900), (-40, -900)], close=True)
        setc(ctx, "#ff3030", 0.25 * scan)
        ctx.fill()
    rrect(ctx, -200, -1080, 400, 330, 28)
    fill_ol(ctx, "#2d3440")
    screen(ctx, -175, -1055, 350, 280, state, g)
    rrect(ctx, -150, -1180, 300, 80, 14)
    fill_ol(ctx, "#ffd23f")
    text(ctx, "SELF CHECKOUT", 0, -1140, 31, "#2b2f36")
    ctx.restore()


def cart(ctx, x, y, s, t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.new_path()
    ctx.arc(-80, -560, 120, 0, 2 * PI)
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(22)
    ctx.stroke()
    ctx.new_path()
    ctx.arc(-80, -560, 120, 0, 2 * PI)
    setc(ctx, "#e94f37")
    ctx.set_line_width(10)
    ctx.stroke()
    rrect(ctx, -10, -720, 230, 160, 14)
    fill_ol(ctx, "#20232a")
    rrect(ctx, 8, -704, 194, 128, 8)
    setc(ctx, "#4fb3ff")
    ctx.fill()
    for i in range(4):
        rrect(ctx, -200 + i * 56, -520 - (i % 2) * 40, 52, 110, 16)
        fill_ol(ctx, "#ffffff")
    for i in range(3):
        rrect(ctx, 30 + i * 18, -560 - i * 50, 140 - i * 36, 50, 8)
        fill_ol(ctx, ("#ff99c8", "#fff1d0", "#ff99c8")[i])
    poly(ctx, [(-230, -420), (230, -420), (190, -110), (-200, -110)], close=True)
    setc(ctx, "#b8c4d0", 0.55)
    ctx.fill_preserve()
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(OL)
    ctx.stroke()
    for i in range(1, 7):
        gx = -230 + i * 66
        stroke_line(ctx, [(gx, -420), (gx - 6 + i * 0.5, -110)], 4, "#5d6b7a")
    for gy in (-320, -220):
        stroke_line(ctx, [(-220, gy), (215, gy)], 4, "#5d6b7a")
    stroke_line(ctx, [(230, -420), (320, -470)], 16)
    stroke_line(ctx, [(-170, -110), (-170, -30), (160, -30), (160, -110)], 12, "#5d6b7a")
    for wx in (-150, 140):
        ell(ctx, wx, -10, 30, 30)
        fill_ol(ctx, "#2b2f36")
    ctx.restore()


def star4(ctx, x, y, r, col="#ffffff", rot=0.0):
    ctx.new_path()
    for i in range(8):
        a = rot + i * PI / 4 - PI / 2
        rr = r if i % 2 == 0 else r * 0.22
        ctx.line_to(x + math.cos(a) * rr, y + math.sin(a) * rr)
    ctx.close_path()
    setc(ctx, col)
    ctx.fill()


def impact_star(ctx, x, y, r, seed=0):
    rnd = random.Random(seed)
    pts = []
    for i in range(16):
        a = i * PI / 8
        rr = r * (1.0 if i % 2 == 0 else 0.5) * rnd.uniform(0.85, 1.15)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    poly(ctx, pts, close=True)
    fill_ol(ctx, "#ffe14d", 8)
    poly(ctx, [(x + (px - x) * 0.55, y + (py - y) * 0.55) for px, py in pts], close=True)
    setc(ctx, "#ff7a1a")
    ctx.fill()


def speed_lines(ctx, cx, cy, col, seed, n=70, inner=420):
    rnd = random.Random(seed)
    ctx.new_path()
    for _ in range(n):
        a, w = rnd.uniform(0, 2 * PI), rnd.uniform(0.008, 0.03)
        r0 = inner * rnd.uniform(0.8, 1.6)
        ctx.move_to(cx + math.cos(a) * r0, cy + math.sin(a) * r0)
        ctx.line_to(cx + math.cos(a - w) * 2600, cy + math.sin(a - w) * 2600)
        ctx.line_to(cx + math.cos(a + w) * 2600, cy + math.sin(a + w) * 2600)
        ctx.close_path()
    setc(ctx, col)
    ctx.fill()


def halftone(ctx, base, dot, cx, cy):
    setc(ctx, base)
    ctx.paint()
    setc(ctx, dot)
    maxd = math.hypot(W, H) * 0.6
    for gy in range(0, H + 40, 44):
        for gx in range(0 if (gy // 44) % 2 == 0 else 22, W + 40, 44):
            r = 3 + 17 * clamp(math.hypot(gx - cx, gy - cy) / maxd)
            ell(ctx, gx, gy, r, r)
    ctx.fill()


def radial_bg(ctx, c1, c2, cx=W / 2, cy=H / 2, r=1300):
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, r)
    g.add_color_stop_rgb(0, *C(c1)[:3])
    g.add_color_stop_rgb(1, *C(c2)[:3])
    ctx.set_source(g)
    ctx.paint()


def glow(ctx, x, y, r, col, a):
    c = C(col)
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g)
    ctx.paint()


def vignette(ctx, a=0.35):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, a)
    ctx.set_source(g)
    ctx.paint()


def rays(ctx, cx, cy, t, col, a, n=16):
    ctx.new_path()
    for i in range(n):
        a0 = t * 0.4 + i * 2 * PI / n
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a0) * 2600, cy + math.sin(a0) * 2600)
        ctx.line_to(cx + math.cos(a0 + PI / n) * 2600, cy + math.sin(a0 + PI / n) * 2600)
        ctx.close_path()
    setc(ctx, col, a)
    ctx.fill()


def bokeh(ctx, t, col, seed=3, n=18):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y0, r, sp = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(30, 110), rnd.uniform(40, 120)
        ell(ctx, x, (y0 - t * sp) % (H + 200) - 100, r, r)
        setc(ctx, col, rnd.uniform(0.1, 0.25))
        ctx.fill()


def sparkles(ctx, t, seed=5, n=10, col="#ffffff", area=(0, 0, W, H)):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3])
        ph = rnd.uniform(0, 1)
        k = max(0.0, math.sin((t * 1.6 + ph) * 2 * PI))
        if k > 0.05:
            star4(ctx, x, y, 14 + 40 * k, col, rot=t)


def steam(ctx, x, y, t, d):
    for k in range(5):
        ph = (t * 1.6 + k / 5) % 1
        ell(ctx, x + d * ph * 90, y - ph * 300, 30 + ph * 70, 30 + ph * 70)
        setc(ctx, "#ffffff", (1 - ph) * 0.85)
        ctx.fill()


def wall_clock(ctx, x, y, r, t):
    ell(ctx, x, y, r, r)
    fill_ol(ctx, "#ffffff")
    for i in range(12):
        a = i * PI / 6
        stroke_line(ctx, [(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78),
                          (x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9)], 5)
    for ang, ln, wd in ((t * 2 * PI * 1.3, 0.75, 7), (t * 2 * PI * 0.11, 0.5, 10)):
        stroke_line(ctx, [(x, y), (x + math.sin(ang) * r * ln, y - math.cos(ang) * r * ln)], wd)


SHELF_COLS = ["#e94f37", "#f6c90e", "#3fa7d6", "#59cd90", "#ee6c4d", "#a06cd5", "#f79256", "#ffffff",
              "#7bdff2", "#ff99c8"]


def shelf_unit(ctx, x, y, w, h, seed):
    rnd = random.Random(seed * 7919 + 17)
    rrect(ctx, x, y, w, h, 10)
    fill_ol(ctx, "#d9a066")
    for lv in range(4):
        by = y + (lv + 1) * h / 4
        cxp = x + 18
        while cxp < x + w - 40:
            pw, ph = rnd.uniform(36, 80), rnd.uniform(70, h / 4 - 40)
            if cxp + pw > x + w - 14:
                break
            col = rnd.choice(SHELF_COLS)
            rrect(ctx, cxp, by - ph - 14, pw, ph, 6)
            fill_ol(ctx, col, 4)
            if rnd.random() < 0.5:
                ctx.rectangle(cxp + 4, by - ph * 0.6 - 14, pw - 8, ph * 0.2)
                setc(ctx, "#ffffff", 0.75)
                ctx.fill()
            cxp += pw + rnd.uniform(4, 12)
        rrect(ctx, x - 6, by - 16, w + 12, 24, 6)
        fill_ol(ctx, "#b97a45", 5)


def store_bg(ctx, off=0.0, soft=0.0):
    g = cairo.LinearGradient(0, 0, 0, 1400)
    g.add_color_stop_rgb(0, *C("#fbeed3")[:3])
    g.add_color_stop_rgb(1, *C("#f1dbb0")[:3])
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, 1400)
    ctx.fill()
    setc(ctx, "#e2cfa8")
    ctx.rectangle(0, 0, W, 120)
    ctx.fill()
    for i in range(-1, 5):
        lx = i * 360 - (off * 0.3) % 360
        rrect(ctx, lx + 60, 40, 240, 40, 20)
        setc(ctx, "#ffffff")
        ctx.fill()
    for k in range(-1, 3):
        cx = W / 2 - off * 0.35 + k * 1800
        if -400 < cx < W + 400:
            rrect(ctx, cx - 330, 170, 660, 130, 30)
            fill_ol(ctx, "#2e9e5b")
            text(ctx, "PICKLE MART", cx + 20, 236, 74)
            ell(ctx, cx - 280, 236, 22, 44)
            fill_ol(ctx, "#a4d65e", 5)
    uw, base = 400, off * 0.6
    first = int(math.floor(base / uw)) - 1
    for i in range(first, first + 5):
        shelf_unit(ctx, i * uw - base + 20, 380, uw - 40, 1000, i)
    setc(ctx, "#dccaa4")
    ctx.rectangle(0, 1380, W, H - 1380)
    ctx.fill()
    ctx.set_line_width(3)
    setc(ctx, "#c9b48a")
    y, step = 1380, 40
    while y < H:
        ctx.move_to(0, y)
        ctx.line_to(W, y)
        y += step
        step *= 1.35
    sp = 260
    for k in range(-8, 9):
        xb = W / 2 + k * sp - (off % sp)
        ctx.move_to(W / 2 + (xb - W / 2) * 0.3, 1380)
        ctx.line_to(xb, H)
    ctx.stroke()
    if soft > 0:
        setc(ctx, "#fff8ec", soft)
        ctx.paint()


# ---------------------------------------------------------------- shots
def sh_hook_eye(ctx, t, d, g):
    store_bg(ctx)
    setc(ctx, "#12060a", 0.65)
    ctx.paint()
    p = flash(t, [0.15, 1.35])
    ctx.save()
    cam(ctx, lerp(1.0, 1.12, eio(t / d)), shake_amp=shake(t, 0.15, 10) + shake(t, 1.35, 10), seed=g)
    r = 950
    fx, fy = W / 2 + 0.34 * r, H / 2 + 0.06 * r
    face(ctx, fx, fy, r, "furious", GRANDPA, t, look=(0.0, 0.4))
    ex, ey = fx - 0.34 * r, fy - 0.06 * r
    xmark(ctx, ex - 0.1 * r, ey - 0.11 * r, 0.04 * r, C("#ff3b3b", 0.4 + 0.6 * p), 0.022 * r)
    ctx.restore()
    glow(ctx, W / 2, H + 150, 1500, "#ff2020", 0.2 + 0.5 * p)


def sh_store_wide(ctx, t, d, g):
    store_bg(ctx)
    ctx.save()
    cam(ctx, lerp(1.0, 1.05, t / d))
    kiosk(ctx, 770, 1640, 0.72, "idle", g)
    person(ctx, 960, 1700, 0.62, TEEN, expr="happy", t=t, pose=dict(bob=4 * math.sin(t * 5)))
    p = clamp(t / 2.4)
    pose = walk_pose(t * 7.5) if p < 1 else {}
    pose.update(ra1=20, ra2=70)
    person(ctx, lerp(-220, 330, p), 1720, 0.78, GRANDPA, pose=pose, expr="smug", t=t,
           look=(1, 0), hold={1: "melon"})
    ctx.restore()


def sh_teen_offer(ctx, t, d, g):
    store_bg(ctx, 200, soft=0.35)
    ctx.save()
    cam(ctx, lerp(1.0, 1.05, t / d))
    cu(ctx, TEEN, "happy", t, hy=950, s=1.9,
       pose=dict(ra1=140, ra2=165 + 28 * math.sin(t * 14), bob=4 * math.sin(t * 6)))
    ctx.restore()
    star4(ctx, 830, 560, 30 + 25 * abs(math.sin(t * 5)), "#ffd23f", rot=t)
    star4(ctx, 260, 700, 20 + 15 * abs(math.sin(t * 4 + 1)), "#ffffff", rot=-t)


def sh_grandpa_no(ctx, t, d, g):
    store_bg(ctx)
    ctx.save()
    cam(ctx, 1 + 0.12 * eout(t / 0.3), rot=-0.05)
    person(ctx, 540, 2450, 1.6, GRANDPA, pose=dict(ra1=35, ra2=160, palm=True, la1=-20, la2=-30),
           expr="smug", t=t, look=(0, 0.1))
    ctx.restore()
    if t > 0.28:
        k = clamp((t - 0.28) / 0.25)
        for i in range(3):
            a = -0.9 + i * 0.5
            stroke_line(ctx, [(990 + math.cos(a) * 120, 1150 + math.sin(a) * 120),
                              (990 + math.cos(a) * (120 + 90 * k), 1150 + math.sin(a) * (120 + 90 * k))], 12)


def two_shot(ctx, t, g, state, gpose, gexpr, z=1.5, scan=0.0, gjit=0.0, look=(1, 0)):
    store_bg(ctx)
    ctx.save()
    cam(ctx, z, 560, 1150, shake_amp=gjit, seed=g)
    kiosk(ctx, 780, 1700, 0.8, state, g, scan)
    person(ctx, 330, 1730, 0.85, GRANDPA, pose=gpose, expr=gexpr, t=t, look=look, hold={1: "melon"})
    ctx.restore()


def sh_grandpa_ready(ctx, t, d, g):
    two_shot(ctx, t, g, "idle", dict(ra1=120, ra2=150, bob=6 * abs(math.sin(t * 4))), "smug", z=1.35)
    sparkles(ctx, t, seed=11, n=4, col="#ffd23f", area=(500, 600, 950, 1000))


def sh_scan1(ctx, t, d, g):
    store_bg(ctx, soft=0.3)
    ctx.save()
    cam(ctx, 2.0, 610, 1000, shake_amp=shake(t, 0.75, 18, 8), seed=g)
    kiosk(ctx, 700, 1700, 0.9, "x" if t > 0.75 else "idle", g, scan=1.0 if 0.5 < t < 0.8 else 0.0)
    mx, my = lerp(200, 600, eout(clamp(t / 0.6))), 1085
    limb(ctx, [(mx - 420, my + 70), (mx - 60, my + 25)], 70, GRANDPA["sleeve"])
    ell(ctx, mx - 45, my + 25, 40, 40)
    fill_ol(ctx, GRANDPA["skin"])
    melon(ctx, mx, my, 62)
    ctx.restore()


def sh_suspicious(ctx, t, d, g):
    store_bg(ctx, 100, soft=0.4)
    ctx.save()
    cam(ctx, lerp(1.0, 1.07, t / d))
    cu(ctx, GRANDPA, "suspicious", t, look=(0.7, 0) if t < 0.8 else (0.9, 0.2))
    ctx.restore()


def sh_scan2(ctx, t, d, g):
    if t < 0.45:
        ra1, ra2 = lerp(110, 165, eout(t / 0.4)), 170
    else:
        k = eout((t - 0.45) / 0.15)
        ra1, ra2 = lerp(165, 75, k), lerp(170, 95, k)
    two_shot(ctx, t, g, "x" if t > 0.8 else "idle", dict(ra1=ra1, ra2=ra2, lean=8 if t > 0.5 else -4),
             "furious", gjit=shake(t, 0.6, 22, 7))
    if 0.6 <= t < 0.9:
        k = (t - 0.6) / 0.3
        impact_star(ctx, 570, 1000, 120 + 120 * k, seed=g)


def sh_teen_nervous(ctx, t, d, g):
    store_bg(ctx, 300, soft=0.4)
    cu(ctx, TEEN, "nervous", t, hx=540 + 3 * math.sin(t * 50), s=2.0, look=(-0.7, 0))


def sh_furious(ctx, t, d, g):
    radial_bg(ctx, "#ff3b3b", "#7a0010", cy=1000)
    speed_lines(ctx, W / 2, 1000, C("#4a0008", 0.55), seed=g // 2)
    hx = 540 + 8 * math.sin(t * 45)
    cu(ctx, GRANDPA, "furious", t, hx=hx, look=(0, 0.1))
    for sd in (-1, 1):
        steam(ctx, hx + sd * 400, 960, t, sd)


def sh_screen_x(ctx, t, d, g):
    setc(ctx, "#1a1d24")
    ctx.paint()
    ctx.save()
    cam(ctx, lerp(1.6, 2.7, eout(t / 0.15)), 540, 1900 - 1.2 * 915, shake_amp=shake(t, 0.05, 14, 6), seed=g)
    kiosk(ctx, 540, 1900, 1.2, "x", g)
    ctx.restore()
    speed_lines(ctx, W / 2, H / 2, C("#000000", 0.25), seed=g, inner=520)


def sh_scan3(ctx, t, d, g):
    w = math.sin(t * 30)
    two_shot(ctx, t, g, "x" if (t * 3) % 1 < 0.6 else "idle",
             dict(ra1=118 + 12 * w, ra2=150 + 15 * math.sin(t * 30 + 1), la1=-30, la2=-60 + 10 * w),
             "furious", gjit=4)


def sh_queue_track(ctx, t, d, g):
    off = lerp(0, 1700, eio(clamp((t - 0.3) / (d - 0.6))))
    store_bg(ctx, off)
    wall_clock(ctx, 1250 - off * 0.35, 245, 80, t)
    ctx.save()
    ctx.translate(-off, 0)
    kiosk(ctx, 300, 1700, 0.72, "x" if (t * 2) % 1 < 0.6 else "idle", g)
    person(ctx, 110 + 3 * math.sin(t * 40), 1720, 0.75, GRANDPA, expr="furious", t=t,
           pose=dict(ra1=118 + 12 * math.sin(t * 30), ra2=150), hold={1: "melon"})
    person(ctx, 470, 1700, 0.6, TEEN, expr="nervous", t=t, look=(-0.8, 0))
    person(ctx, 820, 1720, 0.74, Q_WOMAN, expr="suspicious", t=t, look=(0.2, 0.6),
           pose=dict(la1=40, la2=110, rl=-12 * abs(math.sin(t * 9))))
    yawning = (t % 2.2) < 1.4
    person(ctx, 1180, 1720, 0.72, Q_OLDMAN, expr="yawn" if yawning else "neutral", t=t,
           pose=dict(la1=-160, la2=-170, ra1=160, ra2=170) if yawning else {})
    person(ctx, 1500, 1750, 0.48, Q_KID, expr="happy", t=t, pose=dict(ra1=150, ra2=175, bob=10 * abs(math.sin(t * 6))),
           hold={1: "balloon"})
    person(ctx, 1980, 1720, 0.8, SHOPPER, expr="happy", t=t, pose=dict(bob=5 * math.sin(t * 5)))
    cart(ctx, 2290, 1740, 0.8, t)
    ctx.restore()


def sh_grandma_enter(ctx, t, d, g):
    store_bg(ctx)
    kiosk(ctx, 800, 1640, 0.72, "x", g)
    person(ctx, 640 + 3 * math.sin(t * 40), 1720, 0.78, GRANDPA, expr="furious", t=t,
           pose=dict(ra1=118 + 12 * math.sin(t * 30), ra2=150), hold={1: "melon"})
    p = clamp(t / 1.8)
    person(ctx, lerp(-250, 230, p), 1730, 0.74, GRANDMA, expr="smug" if t > 1.95 else "neutral", t=t,
           look=(1, 0), pose=walk_pose(t * 7, 16) if p < 1 else {})


def sh_grandma_glasses(ctx, t, d, g):
    store_bg(ctx, 500, soft=0.35)
    setc(ctx, "#b78ad8", 0.15)
    ctx.paint()
    ctx.save()
    cam(ctx, lerp(1.0, 1.06, t / d))
    gy = lerp(-1.7, 0, eback(clamp((t - 0.2) / 0.6)))
    cu(ctx, GRANDMA, "smug", t, glasses_y=gy, look=(0.6, 0))
    ctx.restore()
    if t > 0.9:
        k = clamp((t - 0.9) / 0.5)
        star4(ctx, 540 - 0.34 * 399 - 40, 1000 - 0.06 * 399 - 50, 90 * math.sin(PI * k), "#ffffff", rot=k)


def sh_split(ctx, t, d, g):
    xt = lerp(-W, 0, eout(t / 0.3))
    xb = lerp(W, 0, eout((t - 0.12) / 0.3))
    ctx.save()
    poly(ctx, [(0, 0), (W, 0), (W, H * 0.45), (0, H * 0.55)], close=True)
    ctx.clip()
    ctx.translate(xt, 0)
    radial_bg(ctx, "#ff5a3c", "#8a0a12", cy=520)
    speed_lines(ctx, W / 2, 520, C("#ffffff", 0.35), seed=g // 2)
    cu(ctx, GRANDPA, "furious", t, hy=500, s=1.7, look=(0.3, 0.6))
    ctx.restore()
    ctx.save()
    poly(ctx, [(0, H * 0.55), (W, H * 0.45), (W, H), (0, H)], close=True)
    ctx.clip()
    ctx.translate(xb, 0)
    radial_bg(ctx, "#4d8dff", "#0b1f6b", cy=1450)
    speed_lines(ctx, W / 2, 1450, C("#ffffff", 0.35), seed=g // 2 + 7)
    rrect(ctx, 110, 1130, 860, 660, 50)
    fill_ol(ctx, "#2d3440", 10)
    screen(ctx, 150, 1170, 780, 580, "x", g)
    ctx.restore()
    stroke_line(ctx, [(-20, H * 0.552), (W + 20, H * 0.448)], 44)
    stroke_line(ctx, [(-20, H * 0.552), (W + 20, H * 0.448)], 26, "#ffffff")
    if t > 0.35:
        k = eback((t - 0.35) / 0.25)
        ell(ctx, W / 2, H / 2, 110 * k, 110 * k)
        fill_ol(ctx, "#ffd23f", 10)
        if k > 0.3:
            text(ctx, "VS", W / 2, H / 2, 90 * k, "#e53935", ol=10)


def make_rapid(kind, zoom):
    def f(ctx, t, d, g):
        if kind == "eyes":
            radial_bg(ctx, "#ff4040", "#5a0008")
            speed_lines(ctx, W / 2, H / 2, C("#2a0004", 0.5), seed=g, inner=600)
            r = 1000 * zoom
            face(ctx, W / 2, H / 2 + 0.06 * r, r, "furious", GRANDPA, t)
        else:
            setc(ctx, "#101216")
            ctx.paint()
            s = shake(t, 0, 16, 6)
            rnd = random.Random(g)
            w, h = 900 * zoom, 720 * zoom
            ox, oy = W / 2 - w / 2 + rnd.uniform(-s, s), H / 2 - h / 2 + rnd.uniform(-s, s)
            rrect(ctx, ox - 40, oy - 40, w + 80, h + 80, 50)
            fill_ol(ctx, "#2d3440", 10)
            screen(ctx, ox, oy, w, h, "x", g)
            speed_lines(ctx, W / 2, H / 2, C("#000000", 0.3), seed=g, inner=650)
    return f


def sh_chop(ctx, t, d, g):
    halftone(ctx, "#ffd23f", "#ff9f1c", 800, 1130)
    speed_lines(ctx, 800, 1130, C("#ffffff", 0.55), seed=g // 2, inner=300)
    ctx.save()
    cam(ctx, 1.0, shake_amp=shake(t, 0.55, 30, 6), seed=g)
    impact = t >= 0.55
    kiosk(ctx, 800, 1800, 1.0, "glitch" if impact and (t * 12) % 1 < 0.5 else "x", g)
    jump = 180 * math.sin(PI * clamp(t / 0.7))
    if t < 0.4:
        ra1, ra2 = lerp(90, 175, eout(t / 0.3)), 185
    else:
        k = eout((t - 0.4) / 0.15)
        ra1, ra2 = lerp(175, 75, k), lerp(185, 100, k)
    person(ctx, 350, 1800 - jump, 1.0, GRANDPA, expr="furious", t=t,
           pose=dict(ra1=ra1, ra2=ra2, la1=-110, la2=-80, ll=-35, rl=30, lean=12))
    if 0.38 < t < 0.65:
        ctx.new_path()
        ctx.arc(560, 1000, 330, -PI * 0.55, -PI * 0.05)
        setc(ctx, "#ffffff", 0.85)
        ctx.set_line_width(26)
        ctx.stroke()
    ctx.restore()
    if impact and t < 1.0:
        impact_star(ctx, 790, 1130, 140 + 220 * eout((t - 0.55) / 0.3), seed=g)


def sh_glitch(ctx, t, d, g):
    setc(ctx, "#08090c")
    ctx.paint()
    rrect(ctx, 50, 560, 980, 800, 50)
    fill_ol(ctx, "#2d3440", 10)
    screen(ctx, 90, 600, 900, 720, "glitch" if t < 0.55 else "off", g)


def sh_ok(ctx, t, d, g):
    radial_bg(ctx, "#9dffb0", "#0f5a25")
    rays(ctx, W / 2, H / 2, t, "#ffffff", 0.18)
    k = lerp(0.55, 1.0, eback(t / 0.3))
    w, h = 900 * k, 720 * k
    ox, oy = W / 2 - w / 2, H / 2 - h / 2
    rrect(ctx, ox - 40, oy - 40, w + 80, h + 80, 50)
    fill_ol(ctx, "#2d3440", 10)
    screen(ctx, ox, oy, w, h, "ok", g)
    sparkles(ctx, t, seed=21, n=12, col="#ffffff")


def sh_victory(ctx, t, d, g):
    radial_bg(ctx, "#fff1a8", "#e08a00", cy=900)
    rays(ctx, W / 2, 900, t, "#ffffff", 0.22)
    bokeh(ctx, t, "#ffffff")
    ctx.save()
    cam(ctx, 1.0, rot=0.04 * math.sin(t * 2.5))
    bounce = abs(math.sin(t * 5)) * 30
    person(ctx, 540, 1880 - bounce, 1.2, GRANDPA, expr="victory", t=t,
           pose=dict(la1=-155, la2=-170, ra1=155, ra2=170, ll=-10, rl=10), hold={1: "melon"})
    ctx.restore()
    sparkles(ctx, t, seed=31, n=14, col="#ffffff")


def sh_teen_clap(ctx, t, d, g):
    store_bg(ctx, 300, soft=0.4)
    k = abs(math.sin(PI * t * 4))
    cu(ctx, TEEN, "happy", t, s=1.6, pose=dict(la1=25, la2=20 - 32 * k, ra1=-25, ra2=-(20 - 32 * k)))
    sparkles(ctx, t, seed=41, n=8, col="#ffd23f")


def sh_shopper_pass(ctx, t, d, g):
    store_bg(ctx)
    ctx.save()
    cam(ctx, 1.25, 540, 1150)
    kiosk(ctx, 330, 1700, 0.78, "ok", g)
    if t < 1.1:
        sx = lerp(1450, 640, t / 1.1)
    elif t < 1.9:
        sx = 640
    else:
        sx = lerp(640, -700, (t - 1.9) / 1.1)
    paused = 1.1 <= t < 1.9
    person(ctx, 130, 1730, 0.82, GRANDPA, expr="happy" if t < 1.6 else "neutral", t=t,
           look=(clamp((sx - 130) / 500, -1, 1), 0), hold={1: "melon"}, pose=dict(ra1=30, ra2=60))
    cart(ctx, sx - 380, 1780, 0.85, t)
    pose = dict(thumb=True, ra1=120, ra2=175) if paused else walk_pose(t * 7, 14)
    person(ctx, sx, 1770, 0.88, SHOPPER, expr="wink" if paused else "happy", t=t, pose=pose)
    ctx.restore()
    if 1.35 < t < 1.9:
        k = (t - 1.35) / 0.55
        star4(ctx, 760, 760, 70 * math.sin(PI * k), "#ffd23f", rot=k * 2)


def receipt_paper(ctx):
    x0, x1, y0, y1 = 250, 830, 280, 1620
    pts = [(x0, y0)]
    n = 16
    for i in range(1, n + 1):
        pts.append((x0 + i * (x1 - x0) / n, y0 + (0 if i % 2 == 0 else 18)))
    for i in range(n, -1, -1):
        pts.append((x0 + i * (x1 - x0) / n, y1 - (0 if i % 2 == 0 else 18)))
    poly(ctx, pts, close=True)
    fill_ol(ctx, "#fffdf5", 8)
    mono = "DejaVu Sans Mono"
    text(ctx, "PICKLE MART", W / 2, 360, 52, "#20232a", font=mono)
    text(ctx, "SELF CHECKOUT #3", W / 2, 420, 30, "#5d6b7a", font=mono)
    stroke_line(ctx, [(290, 470), (790, 470)], 4, "#9aa5b5")
    items = [("MELON", "2.40"), ("TV 55in", "899.00"), ("BICYCLE", "249.00"), ("CAKE x12", "60.00"),
             ("T.PAPER x40", "38.50")]
    for i, (name, price) in enumerate(items):
        y = 560 + i * 140
        ix = 320
        if i == 0:
            melon(ctx, ix, y, 34, 4)
        elif i == 1:
            rrect(ctx, ix - 40, y - 28, 80, 54, 6)
            fill_ol(ctx, "#20232a", 4)
            ctx.rectangle(ix - 32, y - 20, 64, 38)
            setc(ctx, "#4fb3ff")
            ctx.fill()
        elif i == 2:
            for wx in (-22, 22):
                ell(ctx, ix + wx, y + 8, 20, 20)
                ctx.set_source_rgba(*INK)
                ctx.set_line_width(6)
                ctx.stroke()
            stroke_line(ctx, [(ix - 22, y + 8), (ix, y - 18), (ix + 22, y + 8)], 6, "#e94f37")
        elif i == 3:
            for k in range(3):
                rrect(ctx, ix - 36 + k * 6, y + 14 - k * 18, 72 - k * 12, 20, 6)
                fill_ol(ctx, ("#ff99c8", "#fff1d0", "#ff99c8")[k], 4)
        else:
            rrect(ctx, ix - 22, y - 30, 44, 60, 10)
            fill_ol(ctx, "#ffffff", 4)
            ell(ctx, ix, y - 30, 22, 8)
            fill_ol(ctx, "#e6e6e6", 4)
        text(ctx, name, 380, y, 36, "#20232a", font=mono, align="l")
        text(ctx, price, 800, y, 36, "#20232a", font=mono, align="r")
    stroke_line(ctx, [(290, 1250), (790, 1250)], 4, "#9aa5b5")
    text(ctx, "TOTAL", 300, 1340, 50, "#e53935", font=mono, align="l")
    text(ctx, "1,248.90", 800, 1340, 58, "#e53935", font=mono, align="r")
    text(ctx, "PAID", W / 2, 1490, 44, "#43a047", font=mono)


def sh_receipt(ctx, t, d, g):
    setc(ctx, "#2a2f3a")
    ctx.paint()
    speed_lines(ctx, W / 2, H / 2, C("#ffffff", 0.06), seed=3)
    z0 = lerp(0.4, 1.0, eback(t / 0.3))
    fy = lerp(700, 1150, eio((t - 0.5) / 1.5))
    punch = 1 + 0.35 * eback((t - 2.2) / 0.25) if t > 2.2 else 1
    fy = lerp(fy, 1340, eout((t - 2.2) / 0.25)) if t > 2.2 else fy
    ctx.save()
    cam(ctx, 1.45 * z0 * punch, 540, fy, shake_amp=shake(t, 2.2, 14, 6), seed=g)
    receipt_paper(ctx)
    ctx.restore()
    if t > 2.2:
        glow(ctx, W / 2, H / 2, 1200, "#ff2020", 0.35 * flash(t, [2.2], 2))


def sh_gloom(ctx, t, d, g):
    radial_bg(ctx, "#2b3a67", "#0b1230", cy=900)
    for i in range(14):
        x = 40 + i * 78
        ctx.new_path()
        for k in range(40):
            y = k * 50
            ctx.line_to(x + 14 * math.sin(k * 0.6 + t * 3 + i), y + (t * 120) % 50)
        setc(ctx, "#7a8fd6", 0.35)
        ctx.set_line_width(5)
        ctx.stroke()
    cu(ctx, GRANDPA, "cry", t, hy=1060 + 8 * math.sin(t * 2), s=2.0, pose=dict(lean=-3))
    setc(ctx, "#1b2a5a", 0.2)
    ctx.paint()


def sh_grandma_pays(ctx, t, d, g):
    store_bg(ctx)
    ctx.save()
    cam(ctx, 1.3, 560, 1180)
    person(ctx, 150, 1560, 0.52, GRANDPA, expr="shock", t=t, hold={1: "melon"})
    kiosk(ctx, 640, 1700, 0.8, "idle" if t < 0.9 else "hearts", g)
    k = eout(t / 0.7)
    person(ctx, 380, 1740, 0.78, GRANDMA, expr="smug", t=t, look=(1, -0.3),
           pose=dict(ra1=lerp(10, 100, k), ra2=lerp(10, 140, k)))
    clap = abs(math.sin(PI * (t - 1.0) * 4)) if t > 1.0 else 1.0
    person(ctx, 930, 1730, 0.72, TEEN, expr="happy" if t > 1.0 else "neutral", t=t, look=(-1, 0),
           pose=dict(la1=25, la2=20 - 32 * clap, ra1=-25, ra2=-(20 - 32 * clap)) if t > 1.0 else {})
    if t > 0.9:
        for i in range(5):
            ph = ((t - 0.9) * 0.8 + i * 0.2) % 1
            hx = 640 + 120 * math.sin(i * 2.1 + ph * 4)
            heart(ctx, hx, 940 - ph * 500, 26 + 10 * i % 3)
            setc(ctx, "#ff4d8d", 1 - ph)
            ctx.fill()
    ctx.restore()


def sh_final(ctx, t, d, g):
    store_bg(ctx)
    setc(ctx, "#12060a", 0.55)
    ctx.paint()
    p = flash(t, [1.0], 3)
    ctx.save()
    cam(ctx, lerp(1.0, 1.08, eio(t / d)), shake_amp=shake(t, 1.0, 8), seed=g)
    cu(ctx, GRANDPA, "shock", t, s=2.2, blink=False, hold={1: "melon"})
    r = 190 * 2.2
    for sd in (-1, 1):
        xmark(ctx, 540 + sd * 0.34 * r - 0.08 * r, 1000 - 0.06 * r - 0.1 * r, 0.035 * r,
              C("#ff3b3b", 0.35 + 0.6 * p), 0.02 * r)
    ctx.restore()
    glow(ctx, W / 2, H + 150, 1500, "#ff2020", 0.25 + 0.45 * p)


SHOT_FUNCS = {
    "hook_eye": sh_hook_eye, "store_wide": sh_store_wide, "teen_offer": sh_teen_offer,
    "grandpa_no": sh_grandpa_no, "grandpa_ready": sh_grandpa_ready, "scan1": sh_scan1,
    "suspicious": sh_suspicious, "scan2": sh_scan2, "teen_nervous": sh_teen_nervous,
    "furious": sh_furious, "screen_x": sh_screen_x, "scan3": sh_scan3, "queue_track": sh_queue_track,
    "grandma_enter": sh_grandma_enter, "grandma_glasses": sh_grandma_glasses, "split": sh_split,
    "rapid_a": make_rapid("eyes", 1.0), "rapid_b": make_rapid("screen", 1.0),
    "rapid_c": make_rapid("eyes", 1.3), "rapid_d": make_rapid("screen", 1.25), "chop": sh_chop,
    "glitch": sh_glitch, "ok": sh_ok, "victory": sh_victory, "teen_clap": sh_teen_clap,
    "shopper_pass": sh_shopper_pass, "receipt": sh_receipt, "gloom": sh_gloom,
    "grandma_pays": sh_grandma_pays, "final": sh_final,
}


# ---------------------------------------------------------------- render
def locate(tg):
    acc = 0.0
    for name, dur, _ in SHOTS:
        if tg < acc + dur:
            return name, tg - acc, dur
        acc += dur
    name, dur, _ = SHOTS[-1]
    return name, dur - 1e-3, dur


def draw(ctx, name, t, d, g):
    ctx.save()
    SHOT_FUNCS[name](ctx, t, d, g)
    ctx.restore()
    vignette(ctx, 0.3)


def render_frame(fi):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    name, t, d = locate(fi / FPS)
    draw(ctx, name, t, d, fi)
    surf.flush()
    return bytes(surf.get_data())


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--stills":
        out = sys.argv[2]
        os.makedirs(out, exist_ok=True)
        acc = 0.0
        for i, (name, dur, _) in enumerate(SHOTS):
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
            ctx = cairo.Context(surf)
            draw(ctx, name, dur * 0.7, dur, int((acc + dur * 0.7) * FPS))
            surf.write_to_png(os.path.join(out, f"{i:02d}_{name}.png"))
            acc += dur
        return
    out = sys.argv[1] if len(sys.argv) > 1 else "picture.mp4"
    n = int(round(TOTAL * FPS))
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for i, buf in enumerate(pool.imap(render_frame, range(n), chunksize=4)):
            ff.stdin.write(buf)
            if i % 240 == 0:
                print(f"frame {i}/{n}", flush=True)
    ff.stdin.close()
    sys.exit(ff.wait())


if __name__ == "__main__":
    main()
