#!/usr/bin/env python3
"""Render the picture for "Grandpa vs. the Video Call" (Laughing Box, episode 2).

Characters and drawing helpers come from episode 1 so the series stays on-model.
Captions and lip-sync are driven by voice_track.json from make_voice.py.

  python make_video.py --stills out_dir   # one PNG per shot (for review)
  python make_video.py picture.mp4        # full render, silent H.264
"""
import json
import math
import os
import random
import subprocess
import sys
from multiprocessing import Pool

import cairo

import ep1
from timeline import FPS, H, SHOTS, TOTAL, W

mv = ep1.video()
from ep1_video import (GRANDMA, GRANDPA, INK, PI, C, clamp, cu, darker, eback, eio, eout, ell,  # noqa: E402
                       face, fill_ol, flash, glow, heart, impact_star, lerp, limb, person, poly,
                       radial_bg, rrect, setc, shake, speed_lines, star4, steam, stroke_line, text,
                       vignette, walk_pose)

LEO = dict(skin="#e8b48c", top="#3a6fd8", sleeve="#3a6fd8", style="hoodie", pants="#2f3b52",
           shoe="#222222", hair="spiky", hair_c="#6b3d1f", brow="#6b3d1f", nose="small", freckles=True)
mv.SPEAKER_OF[id(LEO)] = "leo"
mv.CAPTION_COL["leo"] = "#8fd3ff"

TRACK_PATH = os.environ.get("VOICE_TRACK", os.path.join(ep1.HERE, "voice_track.json"))
if os.path.exists(TRACK_PATH):
    with open(TRACK_PATH) as _f:
        mv.TRACK = json.load(_f)["lines"]


def now():
    return mv.CUR_T


# ---------------------------------------------------------------- sets
def living_bg(ctx, soft=0.0, tint=None):
    g = cairo.LinearGradient(0, 0, 0, 1400)
    g.add_color_stop_rgb(0, *C("#f7e6c4")[:3])
    g.add_color_stop_rgb(1, *C("#efcf9c")[:3])
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, 1400)
    ctx.fill()
    setc(ctx, "#ffffff", 0.13)
    for x in range(0, W, 120):
        ctx.rectangle(x, 0, 46, 1400)
    ctx.fill()
    # window with curtains
    rrect(ctx, 70, 360, 340, 520, 14)
    fill_ol(ctx, "#ffffff")
    g = cairo.LinearGradient(0, 380, 0, 860)
    g.add_color_stop_rgb(0, *C("#8fd0ff")[:3])
    g.add_color_stop_rgb(1, *C("#d8f1ff")[:3])
    ctx.set_source(g)
    ctx.rectangle(92, 382, 296, 476)
    ctx.fill()
    ell(ctx, 170, 760, 120, 60)
    setc(ctx, "#8ccf6a")
    ctx.fill()
    stroke_line(ctx, [(240, 380), (240, 860)], 10, "#ffffff")
    stroke_line(ctx, [(90, 620), (390, 620)], 10, "#ffffff")
    for sx in (40, 360):
        poly(ctx, [(sx, 330), (sx + 80, 330), (sx + 60, 930), (sx + 10, 930)], close=True)
        fill_ol(ctx, "#d9534f")
    rrect(ctx, 20, 310, 440, 30, 15)
    fill_ol(ctx, "#8a5a33")
    # framed photo of a fish (grandpa's proudest catch)
    rrect(ctx, 560, 420, 280, 210, 10)
    fill_ol(ctx, "#8a5a33")
    ctx.rectangle(582, 442, 236, 166)
    setc(ctx, "#bfe6f2")
    ctx.fill()
    ell(ctx, 700, 525, 70, 34)
    fill_ol(ctx, "#f2a541", 5)
    poly(ctx, [(630, 525), (598, 498), (598, 552)], close=True)
    fill_ol(ctx, "#f2a541", 5)
    ell(ctx, 745, 518, 7, 7)
    setc(ctx, INK)
    ctx.fill()
    # floor lamp
    stroke_line(ctx, [(980, 560), (980, 1400)], 12, "#4a3a2a")
    glow(ctx, 980, 560, 260, "#fff3b0", 0.5)
    poly(ctx, [(900, 600), (1060, 600), (1030, 470), (930, 470)], close=True)
    fill_ol(ctx, "#ffd76a")
    # floor
    setc(ctx, "#e7c999")
    ctx.rectangle(0, 1370, W, 40)
    ctx.fill()
    setc(ctx, "#b07a4a")
    ctx.rectangle(0, 1400, W, H - 1400)
    ctx.fill()
    setc(ctx, "#9b6a3e")
    ctx.set_line_width(4)
    for y in range(1460, H, 90):
        ctx.move_to(0, y)
        ctx.line_to(W, y)
    ctx.stroke()
    ell(ctx, 540, 1760, 470, 110)
    fill_ol(ctx, "#c8553d")
    ell(ctx, 540, 1760, 380, 80)
    setc(ctx, "#e9a23b", 0.7)
    ctx.fill()
    if tint:
        setc(ctx, tint, 0.15)
        ctx.paint()
    if soft:
        setc(ctx, "#fff8ec", soft)
        ctx.paint()


def leo_bg(ctx):
    setc(ctx, "#7fb3e6")
    ctx.paint()
    setc(ctx, "#ffffff", 0.1)
    for y in range(0, H, 140):
        ctx.rectangle(0, y, W, 50)
    ctx.fill()
    ctx.save()
    ctx.translate(200, 460)
    ctx.rotate(-0.08)
    rrect(ctx, -140, -190, 280, 380, 10)
    fill_ol(ctx, "#ffd23f")
    star4(ctx, 0, -30, 110, "#ff4d8d", 0.2)
    text(ctx, "GAME ON", 0, 130, 46, "#2b2f36")
    ctx.restore()
    rrect(ctx, 720, 330, 300, 380, 14)
    fill_ol(ctx, "#ffffff")
    ctx.rectangle(740, 350, 260, 340)
    setc(ctx, "#1d2b53")
    ctx.fill()
    for x, y in ((790, 420), (900, 390), (960, 520), (820, 600), (930, 640)):
        star4(ctx, x, y, 14, "#ffffff")
    ell(ctx, 950, 440, 34, 34)
    setc(ctx, "#fff3b0")
    ctx.fill()
    rrect(ctx, 0, 1500, W, 420, 0)
    setc(ctx, "#5b84b8")
    ctx.fill()


def armchair(ctx, x, y, s, part):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if part == "back":
        rrect(ctx, -270, -900, 540, 720, 130)
        fill_ol(ctx, "#b5483b")
        rrect(ctx, -200, -820, 400, 520, 90)
        setc(ctx, "#c9594b")
        ctx.fill()
    else:
        rrect(ctx, -250, -430, 500, 150, 50)
        fill_ol(ctx, "#c9594b")
        for sd in (-1, 1):
            rrect(ctx, sd * 270 - 70, -580, 140, 440, 60)
            fill_ol(ctx, "#a23d32")
        rrect(ctx, -300, -300, 600, 260, 34)
        fill_ol(ctx, "#b5483b")
        for sd in (-1, 1):
            rrect(ctx, sd * 240 - 20, -50, 40, 50, 8)
            fill_ol(ctx, "#5a3a22")
    ctx.restore()


# ---------------------------------------------------------------- props
def phone_screen(ctx, kind, t):
    rrect(ctx, -70, -135, 140, 270, 18)
    ctx.save()
    ctx.clip_preserve()
    if kind == "ring":
        g = cairo.LinearGradient(0, -135, 0, 135)
        g.add_color_stop_rgb(0, *C("#2d4b73")[:3])
        g.add_color_stop_rgb(1, *C("#141e30")[:3])
        ctx.set_source(g)
        ctx.fill()
        for k in range(3):
            ph = (t * 1.5 + k / 3) % 1
            ell(ctx, 0, -62, 30 + ph * 40, 30 + ph * 40)
            setc(ctx, "#ffffff", 0.35 * (1 - ph))
            ctx.set_line_width(3)
            ctx.stroke()
        face(ctx, 0, -62, 24, "happy", LEO)
        text(ctx, "Leo", 0, -12, 24, "#ffffff")
        text(ctx, "Video call", 0, 14, 13, "#cfd8e3")
        for sx, col in ((-36, "#e53935"), (36, "#43a047")):
            ell(ctx, sx, 92, 19, 19)
            fill_ol(ctx, col, 3)
        rrect(ctx, 26, 88, 20, 9, 4)
        setc(ctx, "#ffffff")
        ctx.fill()
        rrect(ctx, -46, 88, 20, 9, 4)
        ctx.fill()
    elif kind == "call":
        setc(ctx, "#7fb3e6")
        ctx.fill()
        face(ctx, 0, -5, 52, "happy", LEO)
        rrect(ctx, 22, -122, 40, 58, 6)
        fill_ol(ctx, "#efcf9c", 2)
    elif kind == "magic":
        setc(ctx, "#2b1d4a")
        ctx.fill()
        for i in range(7):
            ell(ctx, 0, 0, 30 + i * 22, 30 + i * 22)
            setc(ctx, ["#ff4d8d", "#ffd23f", "#25c486", "#2fb7ff", "#9b6bff", "#ff7a3d", "#ffffff"][i], 0.5)
            ctx.set_line_width(8)
            ctx.stroke()
        star4(ctx, 0, 0, 40 + 10 * math.sin(t * 20), "#ffffff", t)
    elif kind == "menu":
        setc(ctx, "#1f2430")
        ctx.fill()
        for i, col in enumerate(("#ff4d8d", "#ffd23f", "#25c486", "#2fb7ff")):
            ell(ctx, -36 + (i % 2) * 72, -50 + (i // 2) * 80, 26, 26)
            fill_ol(ctx, col, 3)
    else:
        setc(ctx, "#101216")
        ctx.fill()
    poly(ctx, [(-10, -135), (30, -135), (-30, 135), (-70, 135)], close=True)
    setc(ctx, "#ffffff", 0.08)
    ctx.fill()
    ctx.restore()


def phone(ctx, x, y, s, rot=0.0, screen="dark", t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -80, -150, 160, 300, 26)
    fill_ol(ctx, "#22252c", 6)
    phone_screen(ctx, screen, t)
    rrect(ctx, -18, -146, 36, 8, 4)
    setc(ctx, "#000000")
    ctx.fill()
    ctx.restore()


def finger(ctx, x, y, s, rot, P):
    """Pointing finger whose tip is at (x, y); the arm comes from below."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    rrect(ctx, -150, 380, 300, 500, 60)
    fill_ol(ctx, P["sleeve"], 8)
    ell(ctx, 0, 330, 140, 120)
    fill_ol(ctx, P["skin"], 8)
    rrect(ctx, -44, 0, 88, 330, 44)
    fill_ol(ctx, P["skin"], 8)
    rrect(ctx, -28, 12, 56, 70, 26)
    setc(ctx, "#ffd9d0")
    ctx.fill()
    for k in (230, 120):
        stroke_line(ctx, [(-22, k), (22, k)], 5, darker(P["skin"], 0.8))
    ctx.restore()


def hand_at(x, y, s, side, a1, a2, wide=1.0):
    """Global hand position for person(x, y, s) with lean=0, bob=0 (mirrors episode 1's arm maths)."""
    r = math.radians
    sx, sy = side * 125 * wide, -690
    ex, ey = sx + math.sin(r(a1)) * 165, sy + math.cos(r(a1)) * 165
    return x + s * (ex + math.sin(r(a2)) * 155), y + s * (ey + math.cos(r(a2)) * 155)


def cat_filter(ctx, x, y, r, t, pop=1.0):
    """Video-call cat filter: ears, pink nose, whiskers."""
    k = eback(clamp(pop))
    if k < 0.02:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    wob = 0.04 * math.sin(t * 9)
    for sd in (-1, 1):
        ctx.save()
        ctx.translate(sd * 0.55 * r, -0.9 * r)
        ctx.rotate(sd * (0.25 + wob))
        poly(ctx, [(-0.32 * r, 0.12 * r), (0.32 * r, 0.12 * r), (0, -0.62 * r)], close=True)
        fill_ol(ctx, "#a7a7b3", r * 0.035)
        poly(ctx, [(-0.18 * r, 0.06 * r), (0.18 * r, 0.06 * r), (0, -0.4 * r)], close=True)
        setc(ctx, "#ff9ec4")
        ctx.fill()
        ctx.restore()
    poly(ctx, [(-0.13 * r, 0.1 * r), (0.13 * r, 0.1 * r), (0, 0.24 * r)], close=True)
    fill_ol(ctx, "#ff7fb0", r * 0.025)
    for sd in (-1, 1):
        for k2, dy in enumerate((-0.06, 0.04, 0.14)):
            stroke_line(ctx, [(sd * 0.32 * r, 0.3 * r + dy * r * 0.3),
                              (sd * 1.15 * r, 0.22 * r + dy * r * 1.4 + 0.02 * r * math.sin(t * 6 + k2))],
                        r * 0.022)
    ctx.restore()
    for i in range(4):
        ph = (t * 0.9 + i / 4) % 1
        star4(ctx, x + math.cos(i * 1.7) * r * 1.25, y - r * 0.4 + math.sin(i * 2.3) * r * 0.9,
              r * 0.09 * math.sin(PI * ph), "#ffffff", t)


# ---------------------------------------------------------------- what the phone camera sees
def v_leo(ctx, t, expr="happy", laugh=False, pose=None, look=(0, 0.1)):
    leo_bg(ctx)
    bob = 14 * abs(math.sin(t * 14)) if laugh else 0
    cu(ctx, LEO, expr, t, hx=540, hy=1060 - bob, s=2.1, look=look, pose=pose)
    if laugh:
        for i, (hx, hy) in enumerate(((210, 760), (880, 700), (850, 980))):
            ph = (t * 1.4 + i * 0.3) % 1
            ctx.save()
            ctx.translate(hx, hy - ph * 60)
            ctx.rotate(-0.2 + i * 0.2)
            text(ctx, "HA", 0, 0, 80, "#ffd23f", ol=14)
            ctx.restore()


def v_nose(ctx, t, expr="neutral"):
    living_bg(ctx, soft=0.2)
    hx = 540 + 12 * math.sin(t * 3)
    r = 190 * 7
    cu(ctx, GRANDPA, expr, t, hx=hx, hy=734, s=7, look=(0, 0.2))
    nx, ny = hx, 734 + 0.2 * r
    for sd in (-1, 1):
        ell(ctx, nx + sd * 0.075 * r, ny + 0.07 * r, 0.04 * r, 0.026 * r)
        setc(ctx, "#5a2a1e")
        ctx.fill()
        for k in range(3):
            stroke_line(ctx, [(nx + sd * (0.06 + 0.012 * k) * r, ny + 0.08 * r),
                              (nx + sd * (0.05 + 0.02 * k) * r, ny + 0.115 * r)], 7, "#f4f3ee")
    ell(ctx, nx - 0.06 * r, ny - 0.05 * r, 0.05 * r, 0.03 * r)
    setc(ctx, "#ffffff", 0.45)
    ctx.fill()


def v_forehead(ctx, t):
    living_bg(ctx, soft=0.15)
    stroke_line(ctx, [(540, 0), (540, 230)], 8, "#4a3a2a")
    glow(ctx, 540, 320, 380, "#fff3b0", 0.7)
    poly(ctx, [(430, 330), (650, 330), (600, 220), (480, 220)], close=True)
    fill_ol(ctx, "#ffd76a")
    r = 190 * 4.5
    cu(ctx, GRANDPA, "neutral", t, hx=540, hy=1990, s=4.5, look=(0, -0.6))
    k = max(0.0, math.sin(clamp((t - 0.3) / 0.8) * PI))
    star4(ctx, 540 - 0.32 * r, 1990 - 0.72 * r, 30 + 110 * k, "#ffffff", t)


def v_cat(ctx, t, P=GRANDPA, expr="shock", pop=1.0):
    living_bg(ctx, soft=0.1)
    s = 2.0
    cu(ctx, P, expr, t, hx=540, hy=1000, s=s, look=(0, 0.1))
    cat_filter(ctx, 540, 1000, 190 * s, t, pop)


def v_ear(ctx, t):
    living_bg(ctx)
    r = 190 * 6
    cu(ctx, GRANDPA, "neutral", t, hx=-560, hy=860, s=6)
    ex, ey = -560 + 0.97 * r, 860 + 0.08 * r
    for k in range(6):
        stroke_line(ctx, [(ex - 40 + k * 14, ey + 30), (ex - 70 + k * 22, ey - 60 - 10 * (k % 2))], 8, "#f4f3ee")
    setc(ctx, "#000000", 0.35)
    ctx.paint()


def v_grandma(ctx, t, expr="happy"):
    living_bg(ctx, soft=0.1)
    cu(ctx, GRANDMA, expr, t, hx=540, hy=1020, s=2.0, look=(0, 0.1))


VIEWS = {"leo": v_leo, "nose": v_nose, "forehead": v_forehead, "cat": v_cat, "ear": v_ear, "grandma": v_grandma}


def draw_view(ctx, name, t, rect=None, **kw):
    ctx.save()
    if rect:
        x, y, w, h = rect
        rrect(ctx, x, y, w, h, 26)
        ctx.clip()
        k = max(w / W, h / H)
        ctx.translate(x + w / 2, y + h / 2)
        ctx.scale(k, k)
        ctx.translate(-W / 2, -H / 2)
    VIEWS[name](ctx, t, **kw)
    ctx.restore()


PIP = (700, 190, 330, 480)


def call_ui(ctx, t, main, pip, main_kw=None, pip_kw=None, name="Leo"):
    """Full-frame video call: the frame IS the phone screen."""
    draw_view(ctx, main, t, None, **(main_kw or {}))
    g = cairo.LinearGradient(0, 0, 0, 320)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.55)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, 320)
    ctx.fill()
    text(ctx, name, 220, 110, 56, "#ffffff", align="c")
    text(ctx, f"00:{int(now()) + 3:02d}", 220, 175, 34, (1, 1, 1, 0.8), align="c")
    x, y, w, h = PIP
    rrect(ctx, x + 8, y + 12, w, h, 26)
    setc(ctx, "#000000", 0.35)
    ctx.fill()
    draw_view(ctx, pip, t, PIP, **(pip_kw or {}))
    rrect(ctx, x, y, w, h, 26)
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.set_line_width(7)
    ctx.stroke()
    g = cairo.LinearGradient(0, 1560, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.6)
    ctx.set_source(g)
    ctx.rectangle(0, 1560, W, H - 1560)
    ctx.fill()
    for bx, col, r in ((300, (1, 1, 1, 0.28), 62), (540, "#e53935", 74), (780, (1, 1, 1, 0.28), 62)):
        ell(ctx, bx, 1760, r, r)
        setc(ctx, col)
        ctx.fill()
    ctx.save()
    ctx.translate(540, 1760)
    ctx.rotate(2.36)
    rrect(ctx, -36, -12, 72, 24, 12)
    setc(ctx, "#ffffff")
    ctx.fill()
    ctx.restore()
    rrect(ctx, 288, 1725, 24, 44, 12)
    setc(ctx, "#ffffff")
    ctx.fill()
    stroke_line(ctx, [(300, 1772), (300, 1792)], 6, "#ffffff")
    rrect(ctx, 750, 1738, 60, 44, 8)
    ctx.set_line_width(6)
    ctx.stroke()


# ---------------------------------------------------------------- shots
def zoom_in(ctx, t, z0=1.25, dur=0.25):
    ctx.translate(W / 2, H / 2)
    z = lerp(z0, 1.0, eout(clamp(t / dur)))
    ctx.scale(z, z)
    ctx.translate(-W / 2, -H / 2)


def sh_hook_nose(ctx, t, d, g):
    ctx.save()
    zoom_in(ctx, t, 1.35, 0.3)
    call_ui(ctx, t, "nose", "leo", pip_kw=dict(expr="shock"))
    ctx.restore()


def sh_living_wide(ctx, t, d, g):
    living_bg(ctx)
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.06, t / d), 600, 1250)
    armchair(ctx, 400, 1720, 0.95, "back")
    sp = 0.8
    person(ctx, 400, 1720 - 420 * 0.95 + 330 * sp + 6 * math.sin(t * 2.5), sp, GRANDPA, expr="neutral",
           t=t, blink=True, pose=dict(lean=-5, la1=20, la2=60, ra1=-20, ra2=-60))
    armchair(ctx, 400, 1720, 0.95, "front")
    ell(ctx, 860, 1340, 120, 26)
    fill_ol(ctx, "#8a5a33")
    stroke_line(ctx, [(860, 1350), (860, 1640)], 18, "#6b4423")
    ringing = t > 0.4
    jit = 5 * math.sin(t * 70) if ringing and (t * 2) % 1 < 0.7 else 0
    phone(ctx, 860 + jit, 1230, 0.62, rot=0.02 * jit, screen="ring" if ringing else "dark", t=t)
    if ringing:
        for k in range(3):
            ph = (t * 2 + k / 3) % 1
            for sd in (-1, 1):
                ctx.new_path()
                ctx.arc(860, 1230, 120 + ph * 120, -0.5 if sd > 0 else PI - 0.5, 0.5 if sd > 0 else PI + 0.5)
                setc(ctx, "#ffd23f", 1 - ph)
                ctx.set_line_width(10)
                ctx.stroke()
    for i in range(3):
        ph = (t * 0.6 + i / 3) % 1
        text(ctx, "Z", 470 + ph * 140, 760 - ph * 260, 50 + 50 * ph, (1, 1, 1, 1 - ph), ol=8)
    ctx.restore()


def sh_grandpa_wake(ctx, t, d, g):
    living_bg(ctx, soft=0.3)
    ctx.save()
    mv.cam(ctx, 1.0, shake_amp=shake(t, 0.0, 20, 9), seed=g)
    jolt = t < 0.45
    cu(ctx, GRANDPA, "shock" if jolt else "happy", t, hy=1000 - (40 if jolt else 0), s=2.0,
       glasses_y=None, look=(0.6, 0))
    ctx.restore()
    if jolt:
        text(ctx, "!", 870, 520, 220, "#ff3b3b", ol=20)
    else:
        mv.sparkles(ctx, t, seed=4, n=6, col="#ffd23f", area=(120, 500, 960, 900))


def sh_answer(ctx, t, d, g):
    living_bg(ctx, soft=0.2)
    setc(ctx, "#1b1b24", 0.45)
    ctx.paint()
    s = 4.6
    phone(ctx, 540, 980, s, screen="ring" if t < 0.6 else "call", t=t)
    tip_x, tip_y = 540 + 36 * s, 980 + 92 * s
    k = eout(clamp(t / 0.5))
    fx = lerp(1200, tip_x, k)
    fy = lerp(2100, tip_y, k) + (25 if 0.5 < t < 0.7 else 0)
    finger(ctx, fx, fy, 1.1, -0.35, GRANDPA)
    if t > 0.6:
        k2 = clamp((t - 0.6) / 0.4)
        ell(ctx, tip_x, tip_y, 60 + 200 * k2, 60 + 200 * k2)
        setc(ctx, "#43a047", 1 - k2)
        ctx.set_line_width(14)
        ctx.stroke()


def sh_too_close(ctx, t, d, g):
    living_bg(ctx, soft=0.25)
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.08, t / d))
    cu(ctx, GRANDPA, "suspicious" if mv.talk_amp("grandpa") is None else "furious", t, hx=420, hy=1000, s=2.0,
       look=(1, 0.1))
    glow(ctx, 760, 1080, 420, "#bfe3ff", 0.35)
    phone(ctx, 760, 1080, 1.7, rot=-0.18, screen="call", t=t)
    ell(ctx, 830, 1330, 70, 60)
    fill_ol(ctx, GRANDPA["skin"])
    limb(ctx, [(1100, 1700), (860, 1360)], 110, GRANDPA["sleeve"])
    ctx.restore()
    for i in range(3):
        a = -0.6 + i * 0.6
        stroke_line(ctx, [(990 + math.cos(a) * 140, 820 + math.sin(a) * 140),
                          (990 + math.cos(a) * 200, 820 + math.sin(a) * 200)], 12)


def sh_view_nose(ctx, t, d, g):
    call_ui(ctx, t, "nose", "leo", pip_kw=dict(laugh=True))


def sh_grandpa_raise(ctx, t, d, g):
    living_bg(ctx)
    k = eout(clamp(t / 0.45))
    a1, a2 = lerp(40, 168, k), lerp(150, 178, k)
    x, y, s = 540, 2350, 1.3
    person(ctx, x, y, s, GRANDPA, expr="suspicious", t=t, look=(0.5, -0.9), pose=dict(ra1=a1, ra2=a2))
    hx, hy = hand_at(x, y, s, 1, a1, a2)
    phone(ctx, hx, hy - 120, 0.9, rot=0.1, screen="call", t=t)
    ell(ctx, hx, hy, 40 * s, 40 * s)
    fill_ol(ctx, GRANDPA["skin"])
    if t < 0.4:
        for i in range(4):
            stroke_line(ctx, [(hx - 120 + i * 60, hy + 200), (hx - 120 + i * 60, hy + 420)], 8, (1, 1, 1, 0.8))


def sh_view_forehead(ctx, t, d, g):
    call_ui(ctx, t, "forehead", "leo", pip_kw=dict(laugh=True))


def sh_grandpa_suspicious(ctx, t, d, g):
    living_bg(ctx, soft=0.35)
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.06, t / d))
    cu(ctx, GRANDPA, "suspicious", t, hx=480, hy=980, s=2.0, look=(0.8, 0.5))
    phone(ctx, 880, 1480, 1.5, rot=0.25, screen="call", t=t)
    ell(ctx, 900, 1680, 80, 70)
    fill_ol(ctx, GRANDPA["skin"])
    ctx.restore()
    for i in range(3):
        ph = (t * 0.8 + i / 3) % 1
        text(ctx, "?", 160 + i * 330, 520 - ph * 120, 110, (1, 1, 1, 1 - ph * 0.7), ol=14)


def sh_poke(ctx, t, d, g):
    setc(ctx, "#1b1b24")
    ctx.paint()
    s = 5.4
    magic = t > 1.0
    phone(ctx, 540, 960, s, screen="magic" if magic else "menu", t=t)
    pokes = (0.15, 0.4, 0.65, 0.9)
    near = min(abs(t - p) for p in pokes)
    dip = 40 * max(0.0, 1 - near / 0.1) if t < 1.0 else 0
    finger(ctx, 600 + 30 * math.sin(t * 9), 1000 + dip - (0 if t < 1.0 else 300 * eout(clamp((t - 1.0) / 0.3))),
           1.25, -0.25, GRANDPA)
    for p in pokes:
        if t > p:
            k = clamp((t - p) / 0.3)
            ell(ctx, 600, 1000, 30 + 150 * k, 30 + 150 * k)
            setc(ctx, "#ffffff", 0.8 * (1 - k))
            ctx.set_line_width(10)
            ctx.stroke()
    if magic:
        mv.sparkles(ctx, t, seed=7, n=14, col="#ffd23f")
        k = flash(t, [1.0], 6)
        setc(ctx, "#ffffff", 0.7 * k)
        ctx.paint()


def sh_view_cat(ctx, t, d, g):
    call_ui(ctx, t, "cat", "leo", main_kw=dict(expr="shock" if t < 1.6 else "suspicious", pop=t / 0.35),
            pip_kw=dict(laugh=True))


def sh_grandpa_wipe(ctx, t, d, g):
    radial_bg(ctx, "#ff7a5c", "#8a1020", cy=900)
    speed_lines(ctx, W / 2, 900, C("#4a0008", 0.35), seed=g // 3)
    hx = 540 + 6 * math.sin(t * 40)
    cu(ctx, GRANDPA, "furious", t, hx=hx, hy=860, s=1.9, look=(0, 0.8))
    for sd in (-1, 1):
        steam(ctx, hx + sd * 380, 780, t, sd)
    rub = math.sin(t * 2 * PI / 0.44)
    phone(ctx, 540 + 10 * rub, 1500, 2.4, rot=0.05 * rub, screen="call", t=t)
    px = 540 + 200 * rub
    limb(ctx, [(-150, 2050), (px - 120, 1520)], 120, GRANDPA["sleeve"])
    rrect(ctx, px - 190, 1440, 200, 170, 60)
    fill_ol(ctx, GRANDPA["sleeve"])
    stroke_line(ctx, [(px + 60, 1400), (px + 130, 1360)], 10, (1, 1, 1, 0.9))
    stroke_line(ctx, [(px + 70, 1460), (px + 150, 1450)], 10, (1, 1, 1, 0.9))


def sh_view_cat2(ctx, t, d, g):
    call_ui(ctx, t, "cat", "leo", main_kw=dict(expr="furious"), pip_kw=dict(laugh=True))
    k = eback(clamp((t - 0.1) / 0.3))
    if t > 0.1:
        ctx.save()
        ctx.translate(300, 1300)
        ctx.rotate(-0.15)
        ctx.scale(k, k)
        text(ctx, "MEOW!", 0, 0, 130, "#ff7fb0", ol=22)
        ctx.restore()


def sh_ear_call(ctx, t, d, g):
    living_bg(ctx)
    x, y, s = 540, 1880, 1.0
    shout = mv.talk_amp("grandpa") is not None
    a1, a2 = 130, -143
    person(ctx, x + (4 * math.sin(t * 40) if shout else 0), y, s, GRANDPA, expr="furious" if shout else "suspicious",
           t=t, look=(-0.6, 0), pose=dict(ra1=a1, ra2=a2, la1=-30, la2=-70))
    hx, hy = hand_at(x, y, s, 1, a1, a2)
    phone(ctx, hx + 50, hy - 20, 0.55, rot=0.3, screen="call", t=t)
    ell(ctx, hx, hy, 40, 40)
    fill_ol(ctx, GRANDPA["skin"])
    if shout:
        for i in range(3):
            a = -2.5 + i * 0.35
            stroke_line(ctx, [(x - 140 + math.cos(a) * 200, y - 900 + math.sin(a) * 200),
                              (x - 140 + math.cos(a) * 300, y - 900 + math.sin(a) * 300)], 12)


def sh_leo_facepalm(ctx, t, d, g):
    k = eout(clamp(t / 0.2))
    call_ui(ctx, t, "leo", "ear",
            main_kw=dict(expr="nervous", pose=dict(ra1=lerp(10, 150, k), ra2=lerp(10, -120, k)), look=(0, 0.3)))


def sh_grandma_enter(ctx, t, d, g):
    living_bg(ctx)
    a1, a2 = 130, -143
    person(ctx, 300 + 3 * math.sin(t * 40), 1820, 0.85, GRANDPA, expr="furious", t=t, look=(-0.6, 0),
           pose=dict(ra1=a1, ra2=a2, la1=-30, la2=-70))
    hx, hy = hand_at(300, 1820, 0.85, 1, a1, a2)
    phone(ctx, hx + 42, hy - 17, 0.47, rot=0.3, screen="call", t=t)
    p = clamp(t / 1.6)
    reach = eout(clamp((t - 1.6) / 0.4))
    person(ctx, lerp(1350, 780, p), 1830, 0.82, GRANDMA, expr="smug" if t > 1.7 else "neutral", t=t,
           look=(-1, 0), pose=walk_pose(t * 7, 16) if p < 1 else dict(la1=lerp(-8, -75, reach), la2=lerp(-4, -95, reach)))


def sh_grandma_tap(ctx, t, d, g):
    living_bg(ctx, soft=0.2)
    setc(ctx, "#b78ad8", 0.25)
    ctx.paint()
    s = 4.6
    phone(ctx, 540, 980, s, screen="call" if t < 0.55 else "dark", t=t)
    if t >= 0.55:
        draw_view(ctx, "grandma", t, (540 - 70 * s, 980 - 135 * s, 140 * s, 270 * s), expr="happy")
    tip_x, tip_y = 540 - 20, 980 + 40
    k = eout(clamp(t / 0.45))
    fy = lerp(2200, tip_y, k) + (22 if 0.5 < t < 0.65 else 0)
    finger(ctx, lerp(-100, tip_x, k), fy, 1.1, 0.35, GRANDMA)
    if t > 0.55:
        mv.sparkles(ctx, t, seed=9, n=8, col="#ffffff", area=(200, 400, 880, 1600))


def sh_view_grandma(ctx, t, d, g):
    call_ui(ctx, t, "grandma", "leo", main_kw=dict(expr="happy"), pip_kw=dict(expr="happy"))
    for i in range(5):
        ph = (t * 0.6 + i * 0.2) % 1
        heart(ctx, 160 + i * 190, 1500 - ph * 700, 34)
        setc(ctx, "#ff4d8d", 1 - ph)
        ctx.fill()


def sh_grandma_smug(ctx, t, d, g):
    living_bg(ctx, soft=0.3, tint="#b78ad8")
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.05, t / d))
    cu(ctx, GRANDMA, "smug", t, hx=500, hy=980, s=2.0, look=(0.8, 0.2))
    phone(ctx, 880, 1500, 1.5, rot=-0.2, screen="call", t=t)
    ell(ctx, 900, 1700, 80, 70)
    fill_ol(ctx, GRANDMA["skin"])
    tap = t > 1.2
    ctx.restore()
    if tap:
        k = clamp((t - 1.25) / 0.3)
        ell(ctx, 880, 1500, 40 + 120 * k, 40 + 120 * k)
        setc(ctx, "#ffffff", 1 - k)
        ctx.set_line_width(10)
        ctx.stroke()


def sh_grandpa_grumpy(ctx, t, d, g):
    living_bg(ctx, soft=0.35)
    setc(ctx, "#ff3b3b", 0.12)
    ctx.paint()
    person(ctx, 540, 2600, 1.75, GRANDPA, expr="suspicious", t=t, look=(-0.8, 0),
           pose=dict(la1=30, la2=95, ra1=-30, ra2=-95))
    steam(ctx, 540 - 330, 900, t, -1)
    steam(ctx, 540 + 330, 900, t, 1)


def sh_view_grandma_cat(ctx, t, d, g):
    call_ui(ctx, t, "cat", "leo", main_kw=dict(P=GRANDMA, expr="happy" if t < 1.6 else "shock", pop=(t - 0.2) / 0.35),
            pip_kw=dict(laugh=True))


def sh_grandma_shock(ctx, t, d, g):
    mv.halftone(ctx, "#b78ad8", "#9b6bc4", W / 2, 1000)
    speed_lines(ctx, W / 2, 1000, C("#ffffff", 0.35), seed=g // 2)
    ctx.save()
    mv.cam(ctx, lerp(1.4, 1.0, eout(clamp(t / 0.2))), shake_amp=shake(t, 0.05, 16, 8), seed=g)
    cu(ctx, GRANDMA, "shock", t, s=2.1, look=(0, 0.3))
    ctx.restore()


def sh_grandpa_laugh(ctx, t, d, g):
    radial_bg(ctx, "#fff1a8", "#ffb000", cy=1000)
    mv.rays(ctx, W / 2, 1000, t, "#ffffff", 0.25)
    bob = 18 * abs(math.sin(t * 12))
    cu(ctx, GRANDPA, "victory", t, hy=1000 - bob, s=2.0, pose=dict(ra1=150, ra2=170))
    for i, (hx, hy) in enumerate(((180, 600), (900, 560), (880, 1380))):
        ph = (t * 1.3 + i * 0.3) % 1
        ctx.save()
        ctx.translate(hx, hy - ph * 60)
        ctx.rotate(-0.2 + i * 0.2)
        text(ctx, "HA", 0, 0, 90, "#ff4d8d", ol=14)
        ctx.restore()


def sh_final_nose(ctx, t, d, g):
    if t < 1.0:
        living_bg(ctx, soft=0.2)
        k = eio(clamp(t / 1.0))
        cu(ctx, GRANDPA, "happy", t, hx=lerp(540, 520, k), hy=lerp(1000, 760, k), s=lerp(2.0, 5.5, k), look=(0, 0.2))
        glow(ctx, 540, 1900, 900 * (0.5 + k), "#bfe3ff", 0.25 + 0.4 * k)
        return
    ctx.save()
    zoom_in(ctx, t - 1.0, 1.4, 0.25)
    call_ui(ctx, t, "nose", "leo", main_kw=dict(expr="happy"), pip_kw=dict(expr="neutral", look=(0, 0)))
    ctx.restore()
    k = flash(t, [1.0], 5)
    setc(ctx, "#ffffff", 0.6 * k)
    ctx.paint()


SHOT_FUNCS = {
    "hook_nose": sh_hook_nose, "living_wide": sh_living_wide, "grandpa_wake": sh_grandpa_wake,
    "answer": sh_answer, "too_close": sh_too_close, "view_nose": sh_view_nose,
    "grandpa_raise": sh_grandpa_raise, "view_forehead": sh_view_forehead,
    "grandpa_suspicious": sh_grandpa_suspicious, "poke": sh_poke, "view_cat": sh_view_cat,
    "grandpa_wipe": sh_grandpa_wipe, "view_cat2": sh_view_cat2, "ear_call": sh_ear_call,
    "leo_facepalm": sh_leo_facepalm, "grandma_enter": sh_grandma_enter, "grandma_tap": sh_grandma_tap,
    "view_grandma": sh_view_grandma, "grandma_smug": sh_grandma_smug, "grandpa_grumpy": sh_grandpa_grumpy,
    "view_grandma_cat": sh_view_grandma_cat, "grandma_shock": sh_grandma_shock,
    "grandpa_laugh": sh_grandpa_laugh, "final_nose": sh_final_nose,
}


# ---------------------------------------------------------------- render
def draw(ctx, name, t, d, g):
    ctx.save()
    SHOT_FUNCS[name](ctx, t, d, g)
    ctx.restore()
    vignette(ctx, 0.25)
    mv.caption(ctx)


def render_frame(fi):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    mv.set_time(fi / FPS)
    name, t, d = mv.locate(fi / FPS)
    draw(ctx, name, t, d, fi)
    surf.flush()
    return bytes(surf.get_data())


def main():
    # checked here, not at import, so later episodes can import this module's sets and props
    assert set(SHOT_FUNCS) == {n for n, _, _ in SHOTS}
    if len(sys.argv) >= 3 and sys.argv[1] == "--stills":
        out = sys.argv[2]
        os.makedirs(out, exist_ok=True)
        acc = 0.0
        for i, (name, dur, _) in enumerate(SHOTS):
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
            ctx = cairo.Context(surf)
            mv.set_time(acc + dur * 0.6)
            draw(ctx, name, dur * 0.6, dur, int((acc + dur * 0.6) * FPS))
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
    random.seed(0)
    main()
