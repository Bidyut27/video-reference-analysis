#!/usr/bin/env python3
"""Render the picture for "Grandma vs. the Robot Vacuum" (Laughing Box, episode 3).

Characters come from episode 1 and the living room, Leo and the armchair from
episode 2. Drawing is in a 1080x1920 canvas and rendered at SCALE (default 2,
i.e. 2160x3840 4K); everything is vector, so it stays sharp at any scale.

  python make_video.py --stills out_dir   # one PNG per shot at 1080x1920 (for review)
  python make_video.py picture.mp4        # full render, silent H.264
  SCALE=1 python make_video.py preview.mp4
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
e2 = ep1.ep2_video()
from ep1_video import (GRANDMA, GRANDPA, INK, PI, C, clamp, cu, eback, eio, eout, ell, fill_ol,  # noqa: E402
                       flash, glow, heart, impact_star, lerp, limb, person, poly, radial_bg, rrect,
                       setc, shake, speed_lines, star4, stroke_line, text, vignette, walk_pose)

LEO, living_bg, armchair, hand_at = e2.LEO, e2.living_bg, e2.armchair, e2.hand_at
SCALE = float(os.environ.get("SCALE", "2"))

TRACK_PATH = os.environ.get("VOICE_TRACK", os.path.join(ep1.HERE, "voice_track.json"))
if os.path.exists(TRACK_PATH):
    with open(TRACK_PATH) as _f:
        mv.TRACK = json.load(_f)["lines"]

PINK, BLUE = "#ff4d8d", "#2fb7ff"


# ---------------------------------------------------------------- props
def bow(ctx, x, y, r, col):
    for sd in (-1, 1):
        poly(ctx, [(x, y), (x + sd * r, y - 0.6 * r), (x + sd * r, y + 0.6 * r)], close=True)
        fill_ol(ctx, col, 5)
    ell(ctx, x, y, 0.28 * r, 0.28 * r)
    fill_ol(ctx, col, 5)


def vacuum(ctx, x, y, s=1.0, t=0.0, face=1, bow_col=None, led="#4fd1ff", heart_led=False, moving=False,
           hop=0.0, tilt=0.0):
    """Robot vacuum; (x, y) is the floor contact point, s=1 -> 240 px wide."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ell(ctx, 0, 4, 135, 20)
    setc(ctx, "#000000", 0.22)
    ctx.fill()
    ctx.translate(0, -hop)
    ctx.rotate(tilt)
    rrect(ctx, -120, -52, 240, 52, 24)
    fill_ol(ctx, "#2a2e36", 7)
    ell(ctx, 0, -52, 120, 34)
    fill_ol(ctx, "#3d4350", 7)
    ell(ctx, 0, -56, 82, 22)
    setc(ctx, "#4e5666")
    ctx.fill()
    ell(ctx, -18, -64, 34, 7)
    setc(ctx, "#ffffff", 0.18)
    ctx.fill()
    ell(ctx, 0, -57, 17, 7)
    fill_ol(ctx, "#cfd6e0", 4)
    # bumper strip along the front edge of the side band
    ctx.save()
    ctx.translate(0, -30)
    ctx.scale(1, 0.28)
    ctx.new_path()
    ctx.arc(0, 0, 120, PI * (-0.05 if face > 0 else 0.7), PI * (0.3 if face > 0 else 1.05))
    ctx.restore()
    setc(ctx, "#5b6273")
    ctx.set_line_width(9)
    ctx.stroke()
    lx = face * 90
    glow(ctx, lx, -34, 40, led, 0.5)
    if heart_led:
        heart(ctx, lx, -32, 15)
        setc(ctx, PINK)
        ctx.fill()
    else:
        ell(ctx, lx, -34, 10, 10)
        fill_ol(ctx, led, 3)
    if moving:
        for k in range(3):
            a = t * 40 + k * 2.1
            stroke_line(ctx, [(face * 104, -6), (face * 104 + math.cos(a) * 22, -6 + math.sin(a) * 9)], 5, "#c9c9c9")
    if bow_col:
        bow(ctx, -30, -80, 34, bow_col)
    ctx.restore()


def dust(ctx, x, y, t, face=1, n=4):
    for k in range(n):
        ph = (t * 3 + k / n) % 1
        ell(ctx, x - face * (30 + ph * 140), y - 20 - ph * 50, 16 + ph * 30, 14 + ph * 26)
        setc(ctx, "#ffffff", 0.6 * (1 - ph))
        ctx.fill()


def yarn_path(ctx, pts, col="#e53935", w=7):
    if len(pts) < 2:
        return
    ctx.new_path()
    ctx.move_to(*pts[0])
    for i in range(1, len(pts) - 1):
        mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
        ctx.curve_to(pts[i][0], pts[i][1], pts[i][0], pts[i][1], mx, my)
    ctx.line_to(*pts[-1])
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(w + 6)
    ctx.stroke_preserve()
    setc(ctx, col)
    ctx.set_line_width(w)
    ctx.stroke()


def yarn_ball(ctx, x, y, r, rot=0.0, col="#e53935"):
    ell(ctx, x, y, r, r)
    fill_ol(ctx, col, 6)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    for k in range(4):
        ctx.new_path()
        ctx.arc(0, 0, r * (0.35 + 0.15 * k), PI * (0.1 + 0.2 * k), PI * (0.9 + 0.2 * k))
        setc(ctx, "#a31f1f")
        ctx.set_line_width(4)
        ctx.stroke()
    ctx.restore()


def basket(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    poly(ctx, [(-110, -110), (110, -110), (90, 0), (-90, 0)], close=True)
    fill_ol(ctx, "#c9894b", 7)
    for k in range(1, 4):
        stroke_line(ctx, [(-110 + k * 4, -110 + k * 27), (110 - k * 4, -110 + k * 27)], 5, "#9b6334")
    stroke_line(ctx, [(-40, -110), (-60, -190)], 10, "#d6a26a")
    stroke_line(ctx, [(-30, -110), (-20, -200)], 10, "#d6a26a")
    ctx.restore()


def hearts_up(ctx, t, x0, x1, y0, n=5, col=PINK, rise=600):
    for i in range(n):
        ph = (t * 0.7 + i / n) % 1
        heart(ctx, lerp(x0, x1, (i + 0.5) / n) + 30 * math.sin(t * 3 + i), y0 - ph * rise, 30)
        setc(ctx, col, 1 - ph)
        ctx.fill()


def streaks(ctx, t, col=(1, 1, 1, 0.55), n=26, seed=3, speed=2600, dirn=-1):
    rnd = random.Random(seed)
    for _ in range(n):
        y, ln, sp = rnd.uniform(0, H), rnd.uniform(160, 520), rnd.uniform(0.7, 1.3)
        x = (rnd.uniform(0, W + 600) + dirn * t * speed * sp) % (W + 800) - 400
        stroke_line(ctx, [(x, y), (x - dirn * ln, y)], rnd.uniform(4, 12), col)


def question(ctx, x, y, t, t0, size=120):
    if t < t0:
        return
    k = eback(clamp((t - t0) / 0.25))
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    text(ctx, "?", 0, 0, size, "#ffffff", ol=16)
    ctx.restore()


# ---------------------------------------------------------------- shots
def sh_hook_zoom(ctx, t, d, g):
    living_bg(ctx)
    ctx.save()
    mv.cam(ctx, 1.55, 560, 1560, shake_amp=shake(t, 1.5, 10, 8), seed=g)
    armchair(ctx, 780, 1800, 0.95, "back")
    k = eout(clamp(t / 1.5)) ** 1.6
    vx = lerp(-200, 780, k)
    if vx < 740:
        for i in range(5):
            y = 1730 + i * 18
            stroke_line(ctx, [(vx - 130, y), (vx - 330 - 60 * (i % 2), y)], 6, (1, 1, 1, 0.75))
        dust(ctx, vx, 1800, t)
        vacuum(ctx, vx, 1800, 0.75, t, moving=True, tilt=-0.03)
    jig = 6 * math.sin(t * 50) * shake(t, 1.5, 1, 4)
    armchair(ctx, 780 + jig, 1800, 0.95, "front")
    ctx.restore()
    question(ctx, 800, 1180, t, 1.7)


def sh_grandma_eyes(ctx, t, d, g):
    mv.halftone(ctx, "#b78ad8", "#9b6bc4", W / 2, 1000)
    speed_lines(ctx, W / 2, 1000, C("#ffffff", 0.35), seed=g // 3)
    ctx.save()
    mv.cam(ctx, lerp(1.35, 1.0, eout(clamp(t / 0.2))), shake_amp=shake(t, 0.05, 18, 7), seed=g)
    cu(ctx, GRANDMA, "shock", t, s=2.1, look=(0.6, 0.6))
    ctx.restore()


def sh_leo_explain(ctx, t, d, g):
    living_bg(ctx)
    armchair(ctx, 880, 1760, 0.8, "back")
    armchair(ctx, 880, 1760, 0.8, "front")
    person(ctx, 210, 1800, 0.78, GRANDMA, expr="nervous", t=t, look=(1, 0.5), pose=dict(la1=-40, la2=-150,
                                                                                         ra1=40, ra2=150))
    k = eout(clamp((t - 0.2) / 1.0))
    vx = lerp(880, 640, k)
    vacuum(ctx, vx, 1860, 0.72, t, face=-1, moving=k < 1)
    person(ctx, 480, 1810, 0.68, LEO, expr="happy", t=t, look=(0.5, 0.6), pose=dict(ra1=55, ra2=85))
    if t > 1.2:
        mv.sparkles(ctx, t, seed=2, n=4, col="#ffd23f", area=(560, 1680, 760, 1860))


def sh_grandma_squint(ctx, t, d, g):
    living_bg(ctx, soft=0.35)
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.06, t / d))
    cu(ctx, GRANDMA, "suspicious", t, hx=520, s=2.0, look=(0.6, 0.7))
    ctx.restore()


def sh_bump(ctx, t, d, g):
    living_bg(ctx)
    happy = t > 0.95
    person(ctx, 430, 1800, 1.0, GRANDMA, expr="happy" if happy else "shock", t=t, look=(0.7, 0.9),
           pose=dict(la1=-30, la2=-60, ra1=50, ra2=120) if happy else {})
    bumps = (0.35, 0.85, 1.35)
    off = min(1.0, min(abs(t - b) for b in bumps) / 0.25) if t < 1.6 else 1.0
    vx = 720 + 80 * off
    vacuum(ctx, vx, 1830, 0.95, t, face=-1, moving=t < 1.6, hop=8 * (1 - off), heart_led=t > 1.9)
    for b in bumps:
        if b < t < b + 0.3:
            text(ctx, "BONK", 640, 1560 - (t - b) * 200, 64, "#ffd23f", ol=12)
    if happy:
        hearts_up(ctx, t, 300, 800, 1200, n=4)


def sh_milk(ctx, t, d, g):
    living_bg(ctx)
    ctx.save()
    mv.cam(ctx, 2.0, 560, 1640)
    sx, sy = 520, 1790
    ell(ctx, sx, sy, 120, 30)
    fill_ol(ctx, "#ffffff", 6)
    lvl = 1 - clamp((t - 2.0) / 0.7)
    if lvl > 0.02:
        ell(ctx, sx, sy - 4, 90 * lvl, 18 * lvl)
        setc(ctx, "#f4f8ff")
        ctx.fill()
        ell(ctx, sx, sy - 4, 90 * lvl, 18 * lvl)
        setc(ctx, "#c9d6ea")
        ctx.set_line_width(3)
        ctx.stroke()
    if t < 1.0:
        k = 1 - abs(1 - 2 * clamp(t / 1.0))
        hx, hy = lerp(200, sx - 60, k), lerp(1300, 1740, k)
        limb(ctx, [(-100, 1200), (hx, hy)], 70, GRANDMA["sleeve"])
        ell(ctx, hx, hy, 42, 40)
        fill_ol(ctx, GRANDMA["skin"])
    k = eout(clamp((t - 1.3) / 0.6))
    hop = 40 * math.sin(PI * clamp((t - 2.8) / 0.35)) if t > 2.8 else 0
    vacuum(ctx, lerp(1000, sx + 170, k), 1800, 0.62, t, face=-1, moving=1.3 < t < 2.7, hop=hop,
           tilt=0.1 * math.sin(PI * clamp((t - 2.8) / 0.35)))
    if 2.0 < t < 2.7:
        for i in range(3):
            ph = (t * 4 + i / 3) % 1
            ell(ctx, lerp(sx, sx + 110, ph), sy - 20 - 20 * math.sin(PI * ph), 7, 7)
            setc(ctx, "#ffffff")
            ctx.fill()
    ctx.restore()
    if t > 2.85:
        k = eback(clamp((t - 2.85) / 0.25))
        ctx.save()
        ctx.translate(820, 1260)
        ctx.scale(k, k)
        ell(ctx, 0, 0, 130, 90)
        fill_ol(ctx, "#ffffff", 8)
        text(ctx, "hic!", 0, 0, 70, "#2b2f36")
        ctx.restore()


def sh_bow(ctx, t, d, g):
    living_bg(ctx, soft=0.25)
    setc(ctx, "#ff9ec4", 0.15)
    ctx.paint()
    ctx.save()
    mv.cam(ctx, 2.4, 540, 1600)
    on = t > 0.6
    vacuum(ctx, 540, 1720, 0.9, t, heart_led=on)
    if on:
        k = eback(clamp((t - 0.6) / 0.3))
        ctx.save()
        ctx.translate(540 - 27, 1720 - 72)
        ctx.scale(k, k)
        bow(ctx, 0, 0, 31, PINK)
        ctx.restore()
    for sd in (-1, 1):
        k = eout(clamp(t / 0.5)) if t < 0.7 else 1 - eout(clamp((t - 0.7) / 0.4))
        hx = 540 + sd * lerp(380, 60, k)
        hy = 1600 - 20 * k
        limb(ctx, [(540 + sd * 600, 1400), (hx, hy)], 60, GRANDMA["sleeve"])
        ell(ctx, hx, hy, 38, 36)
        fill_ol(ctx, GRANDMA["skin"])
    ctx.restore()
    if on:
        mv.sparkles(ctx, t, seed=5, n=8, col="#ffffff", area=(200, 900, 880, 1500))


def sh_grandma_love(ctx, t, d, g):
    radial_bg(ctx, "#ffe3f0", "#ff9ec4", cy=1000)
    hearts_up(ctx, t, 120, 960, 1700, n=7, rise=1300)
    cu(ctx, GRANDMA, "happy", t, s=2.0, hy=1000 + 10 * math.sin(t * 6), pose=dict(la1=-10, la2=-150, ra1=10, ra2=150))


def sh_leo_facepalm(ctx, t, d, g):
    living_bg(ctx, soft=0.3)
    k = eout(clamp(t / 0.2))
    cu(ctx, LEO, "nervous", t, s=2.1, look=(0, 0.3), pose=dict(ra1=lerp(10, 150, k), ra2=lerp(10, -120, k)))


def yarn_from(ctx, bx, by, vx, vy, t, sag=40):
    pts = [(bx, by)]
    for i in range(1, 8):
        u = i / 8
        pts.append((lerp(bx, vx, u), lerp(by, vy, u) + sag * math.sin(PI * u) * 0.3 + 6 * math.sin(t * 9 + i)))
    pts.append((vx, vy))
    yarn_path(ctx, pts)


def sh_yarn_grab(ctx, t, d, g):
    living_bg(ctx)
    armchair(ctx, 330, 1760, 0.8, "back")
    armchair(ctx, 330, 1760, 0.8, "front")
    person(ctx, 150, 1830, 0.7, GRANDMA, expr="shock" if t > 1.1 else "happy", t=t, look=(1, 0.4))
    grabbed = t > 0.9
    k = eio(clamp((t - 0.1) / 0.8)) if not grabbed else 1.0
    vx = lerp(-150, 690, k) if not grabbed else 690 + 700 * eout(clamp((t - 1.0) / 1.6))
    bxk = eout(clamp((t - 1.1) / 1.5))
    bx, by, br = 760 + 340 * bxk, 1690 + 160 * min(1.0, bxk * 3), 46 * (1 - 0.45 * bxk)
    basket(ctx, 760, 1830, 0.9)
    if grabbed:
        yarn_from(ctx, bx, by, vx - 60, 1820, t)
    yarn_ball(ctx, bx, by, br, rot=bxk * 12)
    vacuum(ctx, vx, 1850, 0.75, t, moving=True, bow_col=PINK)
    dust(ctx, vx, 1850, t)


def sh_chase_a(ctx, t, d, g):
    living_bg(ctx)
    vx = lerp(-200, 1400, t / d)
    gx = vx - 620 + 60 * math.sin(t * 3)
    pts = [(x, 1860 + 10 * math.sin(x / 70 + t * 4)) for x in range(-120, int(vx) - 40, 60)]
    yarn_path(ctx, pts + [(vx - 60, 1850)])
    vacuum(ctx, vx, 1860, 0.8, t, moving=True, bow_col=PINK)
    dust(ctx, vx, 1860, t)
    pz = walk_pose(t * 16, 34)
    pz.update(ra1=150, ra2=175, lean=10)
    person(ctx, gx, 1830, 0.85, GRANDMA, expr="furious", t=t, look=(1, 0.3), pose=pz)


def sh_chase_b(ctx, t, d, g):
    living_bg(ctx)
    cx, cy = 540, 1830
    loops = int(t / 0.55)
    wob = 6 * math.sin(t * 9) * min(1.0, loops / 3)
    a = t * 2 * PI / 0.55
    vx, vy = cx + 300 * math.cos(a), cy + 50 * math.sin(a)
    front = math.sin(a) > 0
    if not front:
        vacuum(ctx, vx, vy, 0.65, t, face=-1 if math.sin(a) < 0 else 1, moving=True, bow_col=PINK)
    person(ctx, cx, cy - 10, 0.85, LEO, expr="shock", t=t, look=(0.6 * math.cos(a), 0.6),
           pose=dict(lean=wob, la1=-60, la2=-150, ra1=60, ra2=150))
    for k in range(min(loops, 4)):
        y = cy - 70 - k * 55
        ell(ctx, cx, y, 105, 22)
        ctx.set_source_rgba(*INK)
        ctx.set_line_width(13)
        ctx.stroke()
        ell(ctx, cx, y, 105, 22)
        setc(ctx, "#e53935")
        ctx.set_line_width(7)
        ctx.stroke()
    if front:
        vacuum(ctx, vx, vy, 0.65, t, face=1 if math.cos(a) < 0 else -1, moving=True, bow_col=PINK)
    if t > 2.0:
        text(ctx, "TANGLED!", 540, 640, 110, "#ffd23f", ol=18)


def sh_grandpa_enter(ctx, t, d, g):
    radial_bg(ctx, "#ffd76a", "#e3a72f", cy=1000)
    mv.rays(ctx, W / 2, 1000, t, "#ffffff", 0.2)
    k = eback(clamp(t / 0.35))
    cu(ctx, GRANDPA, "smug", t, hy=lerp(1400, 1000, k), s=2.0, look=(0.3, 0.1),
       pose=dict(la1=-80, la2=-170, ra1=80, ra2=170))
    mv.sparkles(ctx, t, seed=8, n=5, col="#ffffff", area=(100, 400, 980, 900))


def sh_grandpa_step(ctx, t, d, g):
    living_bg(ctx)
    k = eout(clamp(t / 0.8))
    vx = lerp(1250, 600, k)
    if t < 1.0:
        lift = clamp((t - 0.6) / 0.3)
        person(ctx, 450, 1830, 0.95, GRANDPA, expr="smug", t=t, look=(0.6, 0.8),
               pose=dict(rl=-35 * lift, la1=-30, la2=-40))
        vacuum(ctx, vx, 1850, 0.85, t, face=-1, moving=True, bow_col=PINK)
    else:
        vacuum(ctx, 560, 1850, 0.85, t, face=-1, bow_col=PINK)
        person(ctx, 545, 1850 - 74, 0.95, GRANDPA, expr="shock", t=t, look=(0, 0.6),
               pose=dict(la1=-100, la2=-160, ra1=100, ra2=160, ll=-6, rl=6))
        if t > 1.15:
            text(ctx, "!", 820, 760, 200, "#ff3b3b", ol=20)


def sh_grandpa_ride(ctx, t, d, g):
    radial_bg(ctx, "#fff1a8", "#ff8a2e", cx=W / 2, cy=1300)
    streaks(ctx, t, seed=g // 6)
    ctx.save()
    mv.cam(ctx, 1.0, shake_amp=6, seed=g)
    ctx.translate(540, 1500)
    ctx.rotate(0.08 * math.sin(t * 7))
    ctx.translate(-540, -1500)
    flail = math.sin(t * 14)
    vacuum(ctx, 560, 1700, 1.05, t, face=-1, moving=True, bow_col=PINK)
    dust(ctx, 560, 1700, t, face=-1, n=6)
    person(ctx, 545, 1700 - 90, 0.95, GRANDPA, expr="shock", t=t, look=(-0.8, 0),
           pose=dict(lean=-12 + 6 * flail, la1=-120 + 40 * flail, la2=-170 + 30 * flail,
                     ra1=120 - 40 * flail, ra2=170 - 30 * flail, ll=-8, rl=8))
    ctx.restore()


def sh_crash(ctx, t, d, g):
    if t < 0.45:
        setc(ctx, "#ffffff")
        ctx.paint()
        impact_star(ctx, 540, 1000, 520 + 120 * t, seed=4)
        ctx.save()
        ctx.translate(540, 1000)
        ctx.rotate(-0.12)
        ctx.scale(eback(clamp(t / 0.15)), eback(clamp(t / 0.15)))
        text(ctx, "CRASH!", 0, 0, 190, "#ff3b3b", ol=24)
        ctx.restore()
        return
    living_bg(ctx, soft=0.25)
    tt = t - 0.45
    cu(ctx, GRANDPA, "shock", t, hx=540, hy=1060, s=1.9, look=(math.cos(tt * 12), math.sin(tt * 12)),
       pose=dict(lean=8 * math.sin(tt * 4)))
    for i in range(5):
        a = tt * 5 + i * 2 * PI / 5
        star4(ctx, 540 + 330 * math.cos(a), 640 + 70 * math.sin(a), 34, "#ffd23f", a)


def held_vacuum(ctx, cx, y, s, t, P, bow_col=PINK):
    vacuum(ctx, cx, y, s, t, bow_col=bow_col, heart_led=True)
    for sd in (-1, 1):
        limb(ctx, [(cx + sd * 340, y + 300), (cx + sd * 125 * s, y - 20 * s)], 80, P["sleeve"])
        ell(ctx, cx + sd * 120 * s, y - 24 * s, 50, 46)
        fill_ol(ctx, P["skin"])


def sh_grandma_proud(ctx, t, d, g):
    radial_bg(ctx, "#fff1a8", "#ffb000", cy=900)
    mv.rays(ctx, W / 2, 900, t, "#ffffff", 0.25)
    cu(ctx, GRANDMA, "smug", t, hy=860 + 6 * math.sin(t * 4), s=1.8, look=(0, 0.4))
    held_vacuum(ctx, 540, 1600, 1.3, t, GRANDMA)
    mv.sparkles(ctx, t, seed=12, n=8, col="#ffffff", area=(80, 300, 1000, 1700))


def sh_next_day(ctx, t, d, g):
    if t < 0.75:
        setc(ctx, "#1d2b53")
        ctx.paint()
        k = eback(clamp(t / 0.25))
        ctx.save()
        ctx.translate(540, 960)
        ctx.scale(k, k)
        text(ctx, "NEXT DAY...", 0, 0, 130, "#ffd23f", ol=18)
        ctx.restore()
        return
    living_bg(ctx)
    tt = t - 0.75
    person(ctx, 540, 1700, 0.95, GRANDMA, expr="happy", t=t, look=(0, 0.3),
           pose=dict(la1=-100, la2=-150, ra1=100, ra2=150))
    pop = eback(clamp((tt - 0.05) / 0.3))
    vacuum(ctx, 280, 1840, 0.8, t, face=1, bow_col=PINK, heart_led=True, hop=4 * abs(math.sin(t * 6)))
    if pop > 0.02:
        ctx.save()
        ctx.translate(790, 1840)
        ctx.scale(pop, pop)
        vacuum(ctx, 0, 0, 0.8, t, face=-1, bow_col=BLUE, heart_led=True, hop=4 * abs(math.sin(t * 6 + 1)))
        ctx.restore()
    hearts_up(ctx, tt, 200, 880, 1500, n=4)


def sh_grandpa_shock(ctx, t, d, g):
    mv.halftone(ctx, "#ff5a36", "#d93a1a", W / 2, 1000)
    speed_lines(ctx, W / 2, 1000, C("#ffffff", 0.35), seed=g // 2)
    ctx.save()
    mv.cam(ctx, lerp(1.4, 1.0, eout(clamp((t - 0.3) / 0.2))), shake_amp=shake(t, 0.35, 18, 7), seed=g)
    cu(ctx, GRANDPA, "shock", t, s=2.1, look=(0, 0.3))
    ctx.restore()


def sh_double_chase(ctx, t, d, g):
    living_bg(ctx)
    armchair(ctx, 540, 1690, 0.75, "back")
    armchair(ctx, 540, 1690, 0.75, "front")
    items = []
    a0 = t * 2 * PI / 2.4
    for lag, kind in ((0.0, "gp"), (0.55, PINK), (0.95, BLUE)):
        a = a0 - lag
        x, y = 540 + 390 * math.cos(a), 1800 + 90 * math.sin(a)
        items.append((y, kind, x, a))
    items.append((1760, "leo", 985, 0))
    items.append((1760, "gm", 120, 0))
    for y, kind, x, a in sorted(items, key=lambda it: it[0]):
        face = 1 if -math.sin(a) > 0 else -1
        if kind == "gp":
            pz = walk_pose(t * 18, 34)
            pz.update(la1=-150, la2=-170, ra1=150, ra2=170)
            person(ctx, x, y, 0.62 + 0.08 * math.sin(a), GRANDPA, expr="shock", t=t, look=(-face, 0), pose=pz)
        elif kind == "leo":
            person(ctx, x, y, 0.6, LEO, expr="happy", t=t, look=(-1, 0),
                   pose=dict(bob=12 * abs(math.sin(t * 10)), ra1=150, ra2=175))
        elif kind == "gm":
            clap = abs(math.sin(t * 9))
            person(ctx, x, y, 0.62, GRANDMA, expr="happy", t=t, look=(1, 0),
                   pose=dict(la1=25, la2=20 - 32 * clap, ra1=-25, ra2=-(20 - 32 * clap)))
        else:
            vacuum(ctx, x, y, 0.6 + 0.06 * math.sin(a), t, face=face, bow_col=kind, moving=True,
                   led="#ff3b3b")


def sh_final(ctx, t, d, g):
    living_bg(ctx)
    setc(ctx, "#1d2b53", 0.15)
    ctx.paint()
    armchair(ctx, 540, 1720, 0.95, "back")
    shout = mv.talk_amp("grandpa") is not None
    person(ctx, 540 + (4 * math.sin(t * 40) if shout else 0), 1720 - 400, 0.72, GRANDPA,
           expr="furious" if shout else "nervous", t=t, look=(0, 0.8),
           pose=dict(la1=-60, la2=-120, ra1=60, ra2=120))
    armchair(ctx, 540, 1720, 0.95, "front")
    zoom = eio(clamp((t - 2.0) / 0.6))
    for lag, col in ((0.0, PINK), (PI, BLUE)):
        a = t * 2.6 + lag
        x, y = 540 + 430 * math.cos(a) * (1 - zoom), 1840 + 40 * math.sin(a) - 60 * zoom
        if zoom < 0.95:
            vacuum(ctx, x, y, 0.68 * (1 - 0.4 * zoom), t, face=1 if math.sin(a) < 0 else -1, bow_col=col,
                   moving=True, led="#ff3b3b")
    if t > 2.6:
        k = clamp((t - 2.6) / 0.6)
        for i in range(2):
            ell(ctx, 470 + i * 140, 1660, 22, 14 * (1 - abs(math.sin(t * 6)) * 0.3))
            setc(ctx, "#ff3b3b", 0.8 * k)
            ctx.fill()
    question(ctx, 860, 1000, t, 3.0)


SHOT_FUNCS = {
    "hook_zoom": sh_hook_zoom, "grandma_eyes": sh_grandma_eyes, "leo_explain": sh_leo_explain,
    "grandma_squint": sh_grandma_squint, "bump": sh_bump, "milk": sh_milk, "bow": sh_bow,
    "grandma_love": sh_grandma_love, "leo_facepalm": sh_leo_facepalm, "yarn_grab": sh_yarn_grab,
    "chase_a": sh_chase_a, "chase_b": sh_chase_b, "grandpa_enter": sh_grandpa_enter,
    "grandpa_step": sh_grandpa_step, "grandpa_ride": sh_grandpa_ride, "crash": sh_crash,
    "grandma_proud": sh_grandma_proud, "next_day": sh_next_day, "grandpa_shock": sh_grandpa_shock,
    "double_chase": sh_double_chase, "final": sh_final,
}


# ---------------------------------------------------------------- render
def draw(ctx, name, t, d, g):
    ctx.save()
    SHOT_FUNCS[name](ctx, t, d, g)
    ctx.restore()
    vignette(ctx, 0.25)
    mv.caption(ctx)


def render_frame(fi):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, int(W * SCALE), int(H * SCALE))
    ctx = cairo.Context(surf)
    ctx.scale(SCALE, SCALE)
    mv.set_time(fi / FPS)
    name, t, d = mv.locate(fi / FPS)
    draw(ctx, name, t, d, fi)
    surf.flush()
    return bytes(surf.get_data())


def main():
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
    ow, oh = int(W * SCALE), int(H * SCALE)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{ow}x{oh}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for i, buf in enumerate(pool.imap(render_frame, range(n), chunksize=2)):
            ff.stdin.write(buf)
            if i % 240 == 0:
                print(f"frame {i}/{n}", flush=True)
    ff.stdin.close()
    sys.exit(ff.wait())


if __name__ == "__main__":
    main()
