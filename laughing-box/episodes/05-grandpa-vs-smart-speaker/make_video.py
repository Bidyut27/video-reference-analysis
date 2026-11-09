#!/usr/bin/env python3
"""Render the picture for "Grandpa vs. the Smart Speaker" (Laughing Box, episode 5).

Characters come from episode 1, the living room and armchair from episode 2,
small helpers from episode 3, and Mittens and the clock from episode 4. New here:
the smart speaker, side table, delivery box, feathers, disco lights and the 3 a.m.
scene. Drawing is in a 1080x1920 canvas rendered at SCALE (default 2 = 4K).

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
e3 = ep1.ep3_video()
e4 = ep1.ep4_video()
from ep1_video import (GRANDMA, GRANDPA, INK, PI, C, clamp, cu, eback, eio, eout, ell, fill_ol,  # noqa: E402
                       flash, glow, heart, impact_star, lerp, person, poly, radial_bg, rrect, setc, shake,
                       speed_lines, star4, steam, stroke_line, text, vignette, walk_pose)

LEO, living_bg, armchair = e2.LEO, e2.living_bg, e2.armchair
question, hearts_up = e3.question, e3.hearts_up
cat, clock = e4.cat, e4.clock


def pop_text(ctx, s, x, y, size, col, t, t0, rot=0.0, ol=None):
    # episode 4's pop_text scales from exactly 0 at t == t0, which Cairo rejects
    if t > t0:
        e4.pop_text(ctx, s, x, y, size, col, t, t0, rot, ol)


SCALE = float(os.environ.get("SCALE", "2"))

TRACK_PATH = os.environ.get("VOICE_TRACK", os.path.join(ep1.HERE, "voice_track.json"))
if os.path.exists(TRACK_PATH):
    with open(TRACK_PATH) as _f:
        mv.TRACK = json.load(_f)["lines"]

RING = {"idle": "#2fb7ff", "talk": "#2fb7ff", "party": None, "love": "#ff4d8d", "alarm": "#ff2a2a"}
DISCO = ["#ff4d8d", "#ffd23f", "#25c486", "#2fb7ff", "#9b6bff", "#ff7a3d"]


# ---------------------------------------------------------------- props
def speaker(ctx, x, y, s, t=0.0, state="idle", face=True):
    """Smart speaker: (x, y) is the bottom centre; s=1 -> 160 px wide."""
    amp = mv.talk_amp("kiosk") or 0.0
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if state == "party":
        col = DISCO[int(t * 8) % len(DISCO)]
    else:
        col = RING[state]
    pulse = amp if state in ("idle", "talk") else (0.7 + 0.3 * math.sin(t * (30 if state == "alarm" else 6)))
    if state != "idle" or amp > 0:
        glow(ctx, 0, -190, 170 + 60 * pulse, col, 0.35 + 0.35 * pulse)
    rrect(ctx, -80, -190, 160, 190, 36)
    fill_ol(ctx, "#4a4f5c", 7)
    # fabric dots
    setc(ctx, "#3b404b")
    for r in range(5):
        for c in range(-3, 4):
            ell(ctx, c * 20 + (10 if r % 2 else 0), -150 + r * 28, 4.5, 4.5)
    ctx.fill()
    ell(ctx, 0, -190, 80, 20)
    fill_ol(ctx, "#5b6273", 7)
    ell(ctx, 0, -192, 64, 14)
    ctx.set_source_rgba(*C(col if (state != "idle" or amp > 0) else "#2a2e36"))
    ctx.set_line_width(9 + 6 * pulse)
    ctx.stroke()
    if face:
        # two little LED eyes that "blink" while talking
        for sd in (-1, 1):
            h = 14 * (1 - 0.7 * amp) if state != "alarm" else 6
            rrect(ctx, sd * 30 - 7, -112 - h / 2, 14, h, 6)
            setc(ctx, col if (state != "idle" or amp > 0) else "#8fd3ff")
            ctx.fill()
    ctx.restore()
    if amp > 0.05 or state in ("party", "alarm"):
        for sd in (-1, 1):
            for k in range(3):
                ctx.new_path()
                a0 = -0.55 if sd > 0 else PI - 0.55
                ctx.arc(x, y - 190 * s, (110 + k * 45) * s, a0, a0 + 1.1)
                setc(ctx, col, clamp(max(amp, 0.6 if state != "idle" else 0) * 1.4 - k * 0.3))
                ctx.set_line_width(10 * s)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.stroke()


def side_table(ctx, x, top, s=1.0):
    ell(ctx, x, top, 150 * s, 30 * s)
    fill_ol(ctx, "#8a5a33")
    stroke_line(ctx, [(x, top + 12 * s), (x, top + 330 * s)], 22 * s, "#6b4423")
    ell(ctx, x, top + 330 * s, 90 * s, 18 * s)
    fill_ol(ctx, "#6b4423")


def seated(ctx, P, x, chair_y, cs, s, expr, t, look=(0, 0), pose=None, **kw):
    armchair(ctx, x, chair_y, cs, "back")
    person(ctx, x, chair_y - 420 * cs + 330 * s, s, P, expr=expr, t=t, look=look, pose=pose or {}, **kw)
    armchair(ctx, x, chair_y, cs, "front")


def feather(ctx, x, y, r, rot, col="#ffffff"):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.new_path()
    ctx.move_to(0, -r)
    ctx.curve_to(r * 0.45, -r * 0.4, r * 0.4, r * 0.5, 0, r)
    ctx.curve_to(-r * 0.4, r * 0.5, -r * 0.45, -r * 0.4, 0, -r)
    ctx.close_path()
    fill_ol(ctx, col, max(3, r * 0.08))
    stroke_line(ctx, [(0, -r * 0.8), (0, r * 1.15)], max(2.5, r * 0.06), "#c9c9c9")
    ctx.restore()


def feathers(ctx, t, n=36, seed=2, area=(0, 0, W, H), speed=160):
    rnd = random.Random(seed)
    for _ in range(n):
        x0, y0 = rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3])
        r, ph, sp = rnd.uniform(18, 44), rnd.uniform(0, 2 * PI), rnd.uniform(0.6, 1.4)
        y = (y0 + t * speed * sp - area[1]) % (area[3] - area[1]) + area[1]
        x = x0 + 50 * math.sin(t * 2.2 * sp + ph)
        feather(ctx, x, y, r, 0.6 * math.sin(t * 3 * sp + ph), rnd.choice(["#ffffff", "#ffffff", "#fff3c4"]))


def box(ctx, x, y, s, open_k=0.0):
    """Delivery box; (x, y) bottom centre, s=1 -> 300 px wide. open_k 0..1 flings the flaps."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for sd in (-1, 1):
        a = sd * lerp(0, 2.2, eout(open_k))
        ctx.save()
        ctx.translate(sd * 150, -220)
        ctx.rotate(-a)
        poly(ctx, [(0, 0), (-sd * 150, 0), (-sd * 150, -70), (0, -70)], close=True)
        fill_ol(ctx, "#d6a26a", 7)
        ctx.restore()
    rrect(ctx, -150, -220, 300, 220, 10)
    fill_ol(ctx, "#c9894b", 7)
    ctx.rectangle(-26, -220, 52, 220)
    setc(ctx, "#e9c79a")
    ctx.fill()
    rrect(ctx, 40, -150, 90, 60, 6)
    fill_ol(ctx, "#ffffff", 4)
    for k in range(3):
        stroke_line(ctx, [(52, -136 + k * 15), (118, -136 + k * 15)], 3, "#9a9a9a")
    ctx.restore()


def disco_lights(ctx, t, a=1.0):
    setc(ctx, "#140a2a", 0.6 * a)
    ctx.paint()
    for i in range(6):
        ang = t * (1.2 + 0.25 * i) + i * 1.05
        cx = 540 + 600 * math.cos(ang)
        g = cairo.LinearGradient(540, 120, cx, 1900)
        c = C(DISCO[i])
        g.add_color_stop_rgba(0, c[0], c[1], c[2], 0.55 * a)
        g.add_color_stop_rgba(1, c[0], c[1], c[2], 0.0)
        ctx.set_source(g)
        poly(ctx, [(540, 120), (cx - 170, 1920), (cx + 170, 1920)], close=True)
        ctx.fill()
    # mirror ball
    stroke_line(ctx, [(540, 0), (540, 70)], 6, "#cfd6e0")
    ell(ctx, 540, 130, 62, 62)
    fill_ol(ctx, "#cfd6e0", 6)
    for r in range(-2, 3):
        for c in range(-2, 3):
            if r * r + c * c <= 5:
                rrect(ctx, 540 + c * 22 - 9, 130 + r * 22 - 9, 18, 18, 3)
                setc(ctx, DISCO[(r * 3 + c + int(t * 10)) % 6] if (r + c + int(t * 6)) % 2 else "#ffffff")
                ctx.fill()


def night_overlay(ctx, a=0.62):
    setc(ctx, "#0b1033", a)
    ctx.paint()


def zzz(ctx, x, y, t, col=(1, 1, 1)):
    for i in range(3):
        ph = (t * 0.6 + i / 3) % 1
        text(ctx, "Z", x + ph * 120, y - ph * 220, 40 + 46 * ph, (*col, 1 - ph), ol=7)


def room_with_speaker(ctx, t, state="idle", soft=0.0):
    living_bg(ctx, soft=soft)
    side_table(ctx, 820, 1330)
    speaker(ctx, 820, 1330, 0.85, t, state)


# ---------------------------------------------------------------- shots
def sh_hook_shout(ctx, t, d, g):
    living_bg(ctx, soft=0.2)
    ctx.save()
    mv.cam(ctx, lerp(1.25, 1.0, eout(clamp(t / 0.25))), shake_amp=shake(t, 0.0, 14, 6), seed=g)
    cu(ctx, GRANDPA, "furious", t, hx=360, hy=880, s=1.7, look=(1, 0.4), pose=dict(ra1=80, ra2=60))
    side_table(ctx, 830, 1520, 0.9)
    speaker(ctx, 830, 1520, 0.9, t, "idle")
    ctx.restore()
    for i in range(3):
        a = -0.35 + i * 0.35
        stroke_line(ctx, [(560 + math.cos(a) * 60, 1000 + math.sin(a) * 60),
                          (560 + math.cos(a) * 150, 1000 + math.sin(a) * 150)], 12)


def sh_speaker_reply(ctx, t, d, g):
    radial_bg(ctx, "#3a3f8f", "#14183a", cy=1050)
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.08, t / d))
    speaker(ctx, 540, 1880, 2.2, t, "talk")
    ctx.restore()
    if t > 1.4:
        k = eback(clamp((t - 1.4) / 0.3))
        for i, (x, y) in enumerate(((220, 520), (860, 470), (540, 360))):
            ctx.save()
            ctx.translate(x, y + 20 * math.sin(t * 6 + i))
            ctx.scale(max(k, 1e-3), max(k, 1e-3))
            ctx.rotate(-0.15 + 0.15 * i)
            duck(ctx, 0, 0, 1.0, t + i)
            ctx.restore()


def duck(ctx, x, y, s, t):
    """Little rubber duck for the 'Baby Duck Disco' gag."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ell(ctx, 0, 30, 90, 56)
    fill_ol(ctx, "#ffd23f", 6)
    ell(ctx, 50, -40, 50, 48)
    fill_ol(ctx, "#ffd23f", 6)
    poly(ctx, [(92, -42), (130, -30), (92, -22)], close=True)
    fill_ol(ctx, "#ff7a3d", 5)
    ell(ctx, 62, -54, 9, 11)
    setc(ctx, INK)
    ctx.fill()
    ctx.new_path()
    ctx.arc(-10, 20, 40, 0.3 + 0.2 * math.sin(t * 9), 2.4)
    setc(ctx, "#e0a800")
    ctx.set_line_width(7)
    ctx.stroke()
    ctx.restore()


def sh_grandpa_horror(ctx, t, d, g):
    mv.halftone(ctx, "#ff5a36", "#d93a1a", W / 2, 1000)
    speed_lines(ctx, W / 2, 1000, C("#ffffff", 0.35), seed=g // 2)
    ctx.save()
    mv.cam(ctx, lerp(1.35, 1.0, eout(clamp(t / 0.2))), shake_amp=shake(t, 0.05, 18, 7), seed=g)
    cu(ctx, GRANDPA, "shock", t, s=2.1, look=(0, 0.2))
    ctx.restore()


def sh_leo_gift(ctx, t, d, g):
    living_bg(ctx)
    seated(ctx, GRANDPA, 300, 1760, 0.85, 0.75, "suspicious", t, look=(1, 0.3))
    person(ctx, 770, 1840, 0.8, LEO, expr="happy", t=t, look=(-1, 0.2), pose=dict(la1=-60, la2=-95))
    hx, hy = e2.hand_at(770, 1840, 0.8, -1, -60, -95)
    k = eback(clamp((t - 0.1) / 0.3))
    ctx.save()
    ctx.translate(hx - 20, hy + 10)
    ctx.scale(max(k, 1e-3), max(k, 1e-3))
    speaker(ctx, 0, 0, 0.95, t, "idle")
    rrect(ctx, -14, -190 * 0.95 + 15, 28, 30, 6)
    fill_ol(ctx, "#ff4d8d", 4)
    e3.bow(ctx, 0, -190 * 0.95 + 10, 44, "#ff4d8d")
    ctx.restore()
    if t > 0.15:
        mv.sparkles(ctx, t, seed=3, n=5, col="#ffd23f", area=(500, 1000, 800, 1300))


def sh_grandpa_doubt(ctx, t, d, g):
    living_bg(ctx, soft=0.35)
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.06, t / d))
    cu(ctx, GRANDPA, "suspicious", t, hx=440, s=2.0, look=(1, 0.6))
    speaker(ctx, 900, 1560, 0.9, t, "idle")
    ctx.restore()


def sh_ask_weather(ctx, t, d, g):
    room_with_speaker(ctx, t)
    k = eout(clamp(t / 0.6))
    person(ctx, lerp(380, 520, k), 1880, 0.92, GRANDPA, expr="suspicious", t=t, look=(1, 0.6),
           pose=dict(lean=lerp(0, 16, k), la1=30, la2=80, ra1=-30, ra2=-80))
    question(ctx, 330, 700, t, 1.2)


def sh_speaker_order(ctx, t, d, g):
    radial_bg(ctx, "#3a3f8f", "#14183a", cy=1050)
    speaker(ctx, 540, 1880, 2.2, t, "talk")
    if t > 1.4:
        k = eback(clamp((t - 1.4) / 0.25))
        ctx.save()
        ctx.translate(540, 520)
        ctx.scale(max(k, 1e-3), max(k, 1e-3))
        rrect(ctx, -330, -90, 660, 180, 40)
        fill_ol(ctx, "#ffffff", 8)
        feather(ctx, -240, 0, 50, 0.5)
        text(ctx, "ORDER PLACED", 50, -22, 56, "#25c486")
        text(ctx, "40 x feathers", 50, 38, 40, "#2b2f36")
        ctx.restore()


def sh_delivery(ctx, t, d, g):
    living_bg(ctx)
    person(ctx, 300, 1860, 0.9, GRANDPA, expr="suspicious" if t < 1.6 else "shock", t=t, look=(1, 0.8))
    land = eout(clamp((t - 0.6) / 0.4))
    open_k = clamp((t - 1.6) / 0.25)
    bx = lerp(1300, 700, land)
    box(ctx, bx, 1880, 0.9, open_k)
    if t < 1.0:
        text(ctx, "DING DONG!", 540, 420, 110, "#ffd23f", ol=18)
    if t > 1.6:
        tt = t - 1.6
        rnd = random.Random(7)
        for _ in range(40):
            a, sp, r = rnd.uniform(-PI * 0.95, -PI * 0.05), rnd.uniform(500, 1400), rnd.uniform(18, 40)
            x = bx + math.cos(a) * sp * tt
            y = 1700 + math.sin(a) * sp * tt + 500 * tt * tt
            feather(ctx, x, y, r, tt * rnd.uniform(-6, 6))
        pop_text(ctx, "POOF!", 700, 820, 160, "#ffffff", t, 1.6, rot=0.08)


def sh_feather_face(ctx, t, d, g):
    radial_bg(ctx, "#fff6d6", "#f2d38a", cy=1000)
    feathers(ctx, t, n=30, seed=4)
    sneeze = t > 1.4
    ctx.save()
    mv.cam(ctx, 1.0, shake_amp=shake(t, 1.4, 22, 8), seed=g)
    cu(ctx, GRANDPA, "shock" if sneeze else "nervous", t, hy=1000 - (40 if sneeze else 0), s=2.0, look=(0, -0.6))
    r = 380
    for i, (dx, dy, rot) in enumerate(((-0.75, -0.9, -0.5), (0.6, -1.05, 0.3), (0.95, -0.2, 0.9), (-0.05, -1.25, 0.1))):
        if not (sneeze and i % 2):
            feather(ctx, 540 + dx * r, 1000 + dy * r, 60, rot)
    ctx.restore()
    if sneeze:
        pop_text(ctx, "ACHOO!", 540, 420, 170, "#ffd23f", t, 1.4, rot=-0.1)


def sh_lights(ctx, t, d, g):
    room_with_speaker(ctx, t, soft=0.1)
    setc(ctx, "#0b1033", 0.35)
    ctx.paint()
    person(ctx, 420, 1880, 0.92, GRANDPA, expr="furious", t=t, look=(1, 0.5),
           pose=dict(la1=-150, la2=-170, ra1=60, ra2=80))
    text(ctx, "click?", 600, 640, 70, (1, 1, 1, 0.7), ol=10)


def sh_disco(ctx, t, d, g):
    living_bg(ctx)
    disco_lights(ctx, t)
    bob = abs(math.sin(t * 8))
    side_table(ctx, 860, 1330)
    speaker(ctx, 860, 1330, 0.85, t, "party")
    ctx.save()
    ctx.translate(560, 1850)
    ctx.rotate(0.12 * math.sin(t * 8))
    ctx.translate(-560, -1850)
    cat(ctx, 560, 1850 - 30 * bob, 0.85, "happy", t, jump=False)
    ctx.restore()
    person(ctx, 230, 1880, 0.85, GRANDPA, expr="furious", t=t, look=(1, 0.4),
           pose=dict(la1=30, la2=95, ra1=-30, ra2=-95))
    for i in range(4):
        ph = (t * 1.2 + i / 4) % 1
        x = 460 + i * 70 + 40 * math.sin(t * 4 + i)
        y = 1400 - ph * 500
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(0.9, 0.9)
        ell(ctx, 0, 0, 22, 17)
        setc(ctx, DISCO[i], 1 - ph)
        ctx.fill()
        stroke_line(ctx, [(20, 0), (20, -70)], 7, (*C(DISCO[i])[:3], 1 - ph))
        ctx.restore()


def sh_shout_slow(ctx, t, d, g):
    living_bg(ctx, soft=0.25)
    beats = (0.1, 0.7, 1.3)
    near = min(abs(t - b) for b in beats)
    lean = 14 * max(0.0, 1 - near / 0.2) if t < 1.6 else 0
    ctx.save()
    mv.cam(ctx, 1.0, shake_amp=shake(t, max(b for b in beats if b <= t) if t > 0.1 else 0, 10, 10), seed=g)
    cu(ctx, GRANDPA, "furious", t, hx=380, hy=990 + lean, s=1.8, look=(1, 0.5))
    speaker(ctx, 860, 1560, 1.0, t, "talk")
    ctx.restore()
    for i, (b, word) in enumerate(zip(beats, ("STOP.", "THE.", "MUSIC."))):
        if t > b:
            pop_text(ctx, word, 540, 250 + i * 105, 96, "#ffffff", t, b)
    if t > 2.9:
        ctx.save()
        ctx.translate(820, 1180)
        rrect(ctx, -170, -60, 340, 120, 30)
        fill_ol(ctx, "#25c486", 6)
        text(ctx, "Calling...", 0, -18, 40, "#ffffff")
        text(ctx, "PICKLE MART", 0, 28, 38, "#ffffff")
        ctx.restore()


def sh_polite(ctx, t, d, g):
    living_bg(ctx, soft=0.25)
    setc(ctx, "#ffe3f0", 0.25)
    ctx.paint()
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.05, t / d))
    cu(ctx, GRANDPA, "happy" if t < 1.7 else "shock", t, hx=380, hy=920, s=1.8, look=(1, 0.5),
       pose=dict(la1=-20, la2=-100, ra1=20, ra2=100))
    speaker(ctx, 860, 1560, 1.0, t, "talk")
    ctx.restore()
    if t < 1.4:
        hearts_up(ctx, t, 180, 600, 700, n=3, rise=300)
    if t > 2.9:
        clock(ctx, 820, 1050, 120, 180)
        pop_text(ctx, "3:00 AM", 820, 1230, 64, "#ff3b3b", t, 2.9)


def sh_grandpa_furious(ctx, t, d, g):
    radial_bg(ctx, "#ff3b3b", "#7a0010", cy=1000)
    speed_lines(ctx, W / 2, 1000, C("#4a0008", 0.55), seed=g // 2)
    hx = 540 + 8 * math.sin(t * 45)
    cu(ctx, GRANDPA, "furious", t, hx=hx, look=(0, 0.1))
    for sd in (-1, 1):
        steam(ctx, hx + sd * 400, 960, t, sd)


def sh_grandma_enter(ctx, t, d, g):
    room_with_speaker(ctx, t)
    person(ctx, 560, 1880, 0.9, GRANDPA, expr="furious", t=t, look=(1, 0.5),
           pose=dict(la1=30, la2=95, ra1=-30, ra2=-95))
    p = clamp(t / 1.5)
    person(ctx, lerp(-250, 230, p), 1880, 0.85, GRANDMA, expr="smug" if t > 1.6 else "neutral", t=t,
           look=(1, 0), pose=walk_pose(t * 7, 16) if p < 1 else {})


def sh_grandma_whisper(ctx, t, d, g):
    living_bg(ctx, soft=0.3)
    setc(ctx, "#b78ad8", 0.18)
    ctx.paint()
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.06, t / d))
    cu(ctx, GRANDMA, "smug", t, hx=420, hy=920, s=1.8, look=(1, 0.5))
    speaker(ctx, 880, 1560, 1.0, t, "idle")
    ctx.restore()
    text(ctx, "psst...", 700, 700, 64, (1, 1, 1, 0.85), ol=10)


def sh_love_song(ctx, t, d, g):
    living_bg(ctx, tint="#ff9ec4")
    setc(ctx, "#ff9ec4", 0.18)
    ctx.paint()
    side_table(ctx, 880, 1330)
    speaker(ctx, 880, 1330, 0.85, t, "love")
    sway = 6 * math.sin(t * 2.5)
    person(ctx, 240, 1880, 0.88, GRANDMA, expr="happy", t=t, look=(1, 0),
           pose=dict(lean=sway, la1=-30, la2=-150, ra1=30, ra2=150))
    person(ctx, 570, 1880, 0.88, GRANDPA, expr="shock", t=t, look=(-1, 0))
    hearts_up(ctx, t, 160, 960, 1300, n=6, rise=700)
    for i in range(3):
        ph = (t * 0.8 + i / 3) % 1
        x, y = 880 + 60 * math.sin(t * 3 + i), 1100 - ph * 500
        ell(ctx, x, y, 20, 15)
        setc(ctx, "#ffffff", 1 - ph)
        ctx.fill()
        stroke_line(ctx, [(x + 18, y), (x + 18, y - 64)], 7, (1, 1, 1, 1 - ph))


def sh_grandpa_defeated(ctx, t, d, g):
    living_bg(ctx, soft=0.3)
    setc(ctx, "#1b2a5a", 0.25)
    ctx.paint()
    seated(ctx, GRANDPA, 540, 1820, 1.0, 0.9, "cry", t, look=(0, 0.4), pose=dict(lean=-4))
    for i in range(7):
        ph = (t * 2 + i / 7) % 1
        x = 420 + i * 40
        stroke_line(ctx, [(x, 420 + ph * 200), (x - 8, 450 + ph * 200)], 7, (0.55, 0.8, 1, 1 - ph))
    for i, (cx, cy, r) in enumerate(((440, 380, 90), (540, 340, 110), (650, 380, 90))):
        ell(ctx, cx, cy, r, r * 0.8)
        fill_ol(ctx, "#6b7a90", 6)


def night_room(ctx, t, state="idle"):
    living_bg(ctx)
    night_overlay(ctx)
    glow(ctx, 230, 600, 300, "#fff3b0", 0.12)
    side_table(ctx, 540, 1400, 0.8)
    speaker(ctx, 540, 1400, 0.72, t, state)
    clock(ctx, 540, 250, 85, 180)


def sh_night(ctx, t, d, g):
    if t < 0.8:
        setc(ctx, "#0b1033")
        ctx.paint()
        k = eback(clamp(t / 0.25))
        ctx.save()
        ctx.translate(540, 960)
        ctx.scale(max(k, 1e-3), max(k, 1e-3))
        text(ctx, "3:00 AM", 0, 0, 170, "#ff3b3b", ol=20)
        ctx.restore()
        return
    night_room(ctx, t)
    seated(ctx, GRANDPA, 230, 1820, 0.82, 0.72, "yawn", t, pose=dict(lean=-6, la1=20, la2=60, ra1=-20, ra2=-60),
           blink=True)
    seated(ctx, GRANDMA, 850, 1820, 0.82, 0.72, "neutral", t, blink=True,
           pose=dict(lean=5, la1=20, la2=60, ra1=-20, ra2=-60))
    zzz(ctx, 280, 1000, t)
    zzz(ctx, 880, 1000, t + 0.4)


def sh_alarm(ctx, t, d, g):
    radial_bg(ctx, "#ff3b3b", "#3a0010", cy=1000)
    ctx.save()
    mv.cam(ctx, lerp(1.2, 1.0, eout(clamp(t / 0.2))), shake_amp=8, seed=g)
    speaker(ctx, 540, 1550, 2.6, t, "alarm")
    ctx.restore()
    if (t * 4) % 1 < 0.6:
        text(ctx, "BEEP! BEEP!", 540, 420, 130, "#ffffff", ol=20)


def sh_grandma_awake(ctx, t, d, g):
    night_room(ctx, t, "alarm")
    flash_a = 0.18 * (0.5 + 0.5 * math.sin(t * 25))
    setc(ctx, "#ff2a2a", flash_a)
    ctx.paint()
    seated(ctx, GRANDPA, 230, 1820, 0.82, 0.72, "yawn", t, pose=dict(lean=-6, la1=20, la2=60, ra1=-20, ra2=-60),
           blink=True)
    jolt = eback(clamp(t / 0.25))
    seated(ctx, GRANDMA, 850, 1820, 0.82, 0.72, "furious", t, look=(-1, 0),
           pose=dict(la1=lerp(20, -120, jolt), la2=lerp(60, -170, jolt), ra1=lerp(-20, 120, jolt),
                     ra2=lerp(-60, 170, jolt)))
    zzz(ctx, 280, 1000, t)
    if t > 0.05:
        text(ctx, "!", 960, 900, 160, "#ffd23f", ol=18)


def sh_final(ctx, t, d, g):
    if t < 1.8:
        night_room(ctx, t, "idle")
        cu_x = 380
        cu(ctx, GRANDPA, "yawn" if t < 0.2 else "furious", t, hx=cu_x, hy=980, s=1.8, look=(1, 0.5), blink=t < 0.2)
        return
    tt = t - 1.8
    radial_bg(ctx, "#3a3f8f", "#14183a", cy=1050)
    ctx.save()
    mv.cam(ctx, lerp(1.3, 1.0, eout(clamp(tt / 0.25))))
    speaker(ctx, 540, 1880, 2.2, t, "talk" if tt < 1.3 else "party")
    ctx.restore()
    if tt > 1.3:
        k = eback(clamp((tt - 1.3) / 0.3))
        for i, (x, y) in enumerate(((220, 520), (860, 470), (540, 360))):
            ctx.save()
            ctx.translate(x, y + 20 * math.sin(t * 6 + i))
            ctx.scale(max(k, 1e-3), max(k, 1e-3))
            ctx.rotate(-0.15 + 0.15 * i)
            duck(ctx, 0, 0, 1.0, t + i)
            ctx.restore()
    k2 = flash(t, [1.8], 6)
    setc(ctx, "#ffffff", 0.5 * k2)
    ctx.paint()


SHOT_FUNCS = {
    "hook_shout": sh_hook_shout, "speaker_reply": sh_speaker_reply, "grandpa_horror": sh_grandpa_horror,
    "leo_gift": sh_leo_gift, "grandpa_doubt": sh_grandpa_doubt, "ask_weather": sh_ask_weather,
    "speaker_order": sh_speaker_order, "delivery": sh_delivery, "feather_face": sh_feather_face,
    "lights": sh_lights, "disco": sh_disco, "shout_slow": sh_shout_slow, "polite": sh_polite,
    "grandpa_furious": sh_grandpa_furious, "grandma_enter": sh_grandma_enter,
    "grandma_whisper": sh_grandma_whisper, "love_song": sh_love_song,
    "grandpa_defeated": sh_grandpa_defeated, "night": sh_night, "alarm": sh_alarm,
    "grandma_awake": sh_grandma_awake, "final": sh_final,
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
        frac = float(os.environ.get("STILL_AT", "0.6"))
        acc = 0.0
        for i, (name, dur, _) in enumerate(SHOTS):
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
            ctx = cairo.Context(surf)
            mv.set_time(acc + dur * frac)
            draw(ctx, name, dur * frac, dur, int((acc + dur * frac) * FPS))
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
