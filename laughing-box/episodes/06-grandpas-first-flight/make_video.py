#!/usr/bin/env python3
"""Render the picture for "Grandpa's First Flight" (Laughing Box, episode 6).

Characters come from episode 1, Leo and the pointing finger from episode 2, small
helpers from episodes 3-5. New here: the airplane cabin, seats, call-button panel,
life vest, window views, the plane exterior, and Rosa the flight attendant.
Drawing is in a 1080x1920 canvas rendered at SCALE (default 2 = 2160x3840 4K).

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
e5 = ep1.ep5_video()
from ep1_video import (GRANDMA, GRANDPA, INK, PI, C, clamp, cu, darker, eback, eio, eout, ell,  # noqa: E402
                       fill_ol, flash, glow, impact_star, lerp, limb, person, poly, radial_bg, rrect,
                       setc, shake, speed_lines, star4, steam, stroke_line, text, vignette, walk_pose)

LEO, finger, hand_at = e2.LEO, e2.finger, e2.hand_at
pop_text, zzz = e5.pop_text, e5.zzz
question = e3.question
SCALE = float(os.environ.get("SCALE", "2"))

ROSA = dict(skin="#c98e66", top="#1d3a6e", sleeve="#1d3a6e", style="plain", pants="#1d3a6e",
            shoe="#222222", hair="grey_bun", hair_c="#2b1d14", brow="#2b1d14", nose="small")
mv.SPEAKER_OF[id(ROSA)] = "rosa"
mv.SPEAKER_OF[id(LEO)] = "leo"
mv.CAPTION_COL["rosa"] = "#ffb3c7"
mv.CAPTION_COL["pilot"] = "#ffffff"

# loaded after the earlier episodes, which each load their own track at import
TRACK_PATH = os.environ.get("VOICE_TRACK", os.path.join(ep1.HERE, "voice_track.json"))
if os.path.exists(TRACK_PATH):
    with open(TRACK_PATH) as _f:
        mv.TRACK = json.load(_f)["lines"]

SEAT, SEAT_DK, HEAD = "#3f6fb5", "#2f5590", "#e8eef7"
VEST, VEST_DK = "#ff8c1a", "#e06a00"


# ---------------------------------------------------------------- props
def rosa_scarf(ctx, x, py, s):
    """Red scarf knot at Rosa's neck; (x, py) is her foot point."""
    ny = py - 735 * s
    poly(ctx, [(x - 60 * s, ny), (x + 60 * s, ny), (x, ny + 70 * s)], close=True)
    fill_ol(ctx, "#e53935", 5 * s + 2)
    for sd in (-1, 1):
        poly(ctx, [(x, ny + 40 * s), (x + sd * 50 * s, ny + 130 * s), (x + sd * 15 * s, ny + 120 * s)], close=True)
        fill_ol(ctx, "#e53935", 5 * s + 2)
    ell(ctx, x, ny + 40 * s, 16 * s, 14 * s)
    fill_ol(ctx, "#c62828", 4 * s + 2)
    # wing pin
    rrect(ctx, x - 140 * s, ny + 110 * s, 70 * s, 16 * s, 8 * s)
    fill_ol(ctx, "#ffd23f", 3 * s + 1)


def rosa(ctx, x, py, s, expr="happy", t=0.0, look=(0, 0), pose=None, vest_k=None):
    person(ctx, x, py, s, ROSA, expr=expr, t=t, look=look, pose=pose or {})
    rosa_scarf(ctx, x, py, s)
    if vest_k is not None:
        vest(ctx, x, py, s, vest_k, t, hands=False)


def cu_rosa(ctx, expr, t, hx=540, hy=1000, s=2.1, **kw):
    rosa(ctx, hx, hy + 900 * s, s, expr, t, **kw)


def vest(ctx, x, py, s, k, t=0.0, hands=True):
    """Life vest over a person whose foot point is (x, py); k = 0 flat, 1 fully inflated."""
    k = clamp(k)
    wob = 1 + 0.03 * math.sin(t * 9) * k
    cx, cy = x, py - 440 * s
    rx, ry = (140 + 300 * k) * s * wob, (190 + 90 * k) * s
    col = VEST if k > 0.05 else "#ffcf33"
    if hands:
        for sd in (-1, 1):
            hx = cx + sd * (rx * 0.98)
            limb(ctx, [(hx - sd * 30 * s, cy + 40 * s), (hx + sd * 30 * s, cy + 60 * s)], 50 * s, GRANDPA["sleeve"],
                 6 * s + 2)
            ell(ctx, hx + sd * 40 * s, cy + 64 * s, 34 * s, 32 * s)
            fill_ol(ctx, GRANDPA["skin"], 6 * s + 2)
    for sd in (-1, 1):
        ell(ctx, cx + sd * rx * 0.48, cy, rx * 0.55, ry)
        fill_ol(ctx, col, 8 * s + 2)
        ell(ctx, cx + sd * rx * 0.48 - rx * 0.18, cy - ry * 0.45, rx * 0.16, ry * 0.12)
        setc(ctx, "#ffffff", 0.45)
        ctx.fill()
    rrect(ctx, cx - rx * 0.95, cy + ry * 0.25, rx * 1.9, 26 * s, 10 * s)
    fill_ol(ctx, "#f5f5f5", 5 * s + 2)
    stroke_line(ctx, [(cx, cy + ry * 0.4), (cx, cy + ry * 0.4 + 70 * s)], 8 * s, "#e53935")
    ell(ctx, cx, cy + ry * 0.4 + 82 * s, 16 * s, 16 * s)
    fill_ol(ctx, "#e53935", 4 * s + 2)


def seat_back(ctx, x, yc, s=1.0):
    rrect(ctx, x - 150 * s, yc - 560 * s, 300 * s, 600 * s, 60 * s)
    fill_ol(ctx, SEAT, 7)
    rrect(ctx, x - 120 * s, yc - 520 * s, 240 * s, 420 * s, 40 * s)
    setc(ctx, "#4a7cc4")
    ctx.fill()
    rrect(ctx, x - 110 * s, yc - 545 * s, 220 * s, 120 * s, 30 * s)
    fill_ol(ctx, HEAD, 5)


def seat_front(ctx, x, yc, s=1.0):
    ctx.rectangle(x - 140 * s, yc + 60 * s, 280 * s, 400 * s)
    fill_ol(ctx, SEAT_DK, 7)
    rrect(ctx, x - 150 * s, yc - 30 * s, 300 * s, 120 * s, 34 * s)
    fill_ol(ctx, SEAT, 7)


def armrest(ctx, x, yc, s=1.0):
    rrect(ctx, x - 24 * s, yc - 170 * s, 48 * s, 210 * s, 18 * s)
    fill_ol(ctx, "#9aa5b5", 6)
    rrect(ctx, x - 30 * s, yc - 180 * s, 60 * s, 40 * s, 16 * s)
    fill_ol(ctx, "#7d8796", 6)


def lap_belt(ctx, x, yc, s, to=None):
    """Seat belt across the lap; `to` = (x, y) end point when Grandpa buckles the wrong one."""
    y = yc - 6 * s
    end = to or (x + 100 * s, y)
    stroke_line(ctx, [(x - 100 * s, y), end], 26 * s + 6, INK)
    stroke_line(ctx, [(x - 100 * s, y), end], 26 * s, "#5b6273")
    rrect(ctx, end[0] - 22 * s, end[1] - 18 * s, 44 * s, 36 * s, 8 * s)
    fill_ol(ctx, "#cfd6e0", 5)


def cloud(ctx, x, y, s, col="#ffffff", a=1.0):
    setc(ctx, col, a)
    for dx, dy, r in ((-60, 10, 50), (-10, -20, 70), (55, 0, 55), (100, 18, 38), (-100, 25, 34)):
        ell(ctx, x + dx * s, y + dy * s, r * s, r * s)
    ctx.fill()


def cabin_bg(ctx, soft=0.0, window_scene="clouds", t=0.0):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *C("#e9e4da")[:3])
    g.add_color_stop_rgb(1, *C("#d6cfc2")[:3])
    ctx.set_source(g)
    ctx.paint()
    # curved ceiling + overhead bins
    ctx.new_path()
    ctx.move_to(0, 0)
    ctx.line_to(W, 0)
    ctx.line_to(W, 260)
    ctx.curve_to(W * 0.7, 120, W * 0.3, 120, 0, 260)
    ctx.close_path()
    setc(ctx, "#f4f1ea")
    ctx.fill()
    for sd in (-1, 1):
        x0 = 0 if sd < 0 else W - 380
        poly(ctx, [(x0, 260 if sd < 0 else 160), (x0 + 380, 160 if sd < 0 else 260),
                   (x0 + 380, 470 if sd < 0 else 560), (x0, 560 if sd < 0 else 470)], close=True)
        fill_ol(ctx, "#ffffff", 6)
        bx = 190 if sd < 0 else W - 190
        rrect(ctx, bx - 60, (420 if sd < 0 else 420), 120, 22, 10)
        fill_ol(ctx, "#c9c9c9", 4)
    for k in range(4):
        ell(ctx, 540, 240 + k * 70, 90 - k * 12, 10)
        setc(ctx, "#fff6d6", 0.9)
        ctx.fill()
    # side wall with a window, left
    poly(ctx, [(0, 560), (150, 520), (150, 1500), (0, 1700)], close=True)
    setc(ctx, "#ece7dd")
    ctx.fill()
    window(ctx, 80, 900, 48, 82, window_scene, t, frame=14)
    # aisle carpet
    poly(ctx, [(380, 1500), (700, 1500), (900, H), (180, H)], close=True)
    setc(ctx, "#4a5f8f")
    ctx.fill()
    setc(ctx, "#5c73a6")
    for k in range(6):
        y = 1560 + k * 70
        ctx.rectangle(260 - k * 15, y, 560 + k * 30, 10)
    ctx.fill()
    if soft:
        setc(ctx, "#fff8ec", soft)
        ctx.paint()


def window(ctx, cx, cy, rx, ry, scene, t, frame=None, blind=0.0, lift=0.0):
    frame = frame or rx * 0.18
    ell(ctx, cx, cy, rx + frame, ry + frame)
    fill_ol(ctx, "#f4f1ea", max(4, frame * 0.25))
    ell(ctx, cx, cy, rx + frame * 0.35, ry + frame * 0.35)
    setc(ctx, "#bdb6a8")
    ctx.fill()
    ctx.save()
    ell(ctx, cx, cy, rx, ry)
    ctx.clip()
    k = max(rx, ry) / 520
    if scene == "sunset":
        g = cairo.LinearGradient(0, cy - ry, 0, cy + ry)
        for p, c in ((0, "#5b3fa6"), (0.45, "#ff6f91"), (0.75, "#ffb347"), (1, "#ffd76a")):
            g.add_color_stop_rgb(p, *C(c)[:3])
        ctx.set_source(g)
        ctx.paint()
        ell(ctx, cx, cy + ry * 0.35, 110 * k, 110 * k)
        setc(ctx, "#fff3b0")
        ctx.fill()
        glow(ctx, cx, cy + ry * 0.35, 320 * k, "#fff3b0", 0.6)
        for i in range(5):
            x = cx + ((i * 260 - t * 40) % 1300 - 650) * k
            cloud(ctx, x, cy + ry * (0.55 + 0.08 * (i % 2)), 1.3 * k, "#b56ab0", 0.85)
    elif scene == "runway":
        g = cairo.LinearGradient(0, cy - ry, 0, cy + ry)
        g.add_color_stop_rgb(0, *C("#5fb3ff")[:3])
        g.add_color_stop_rgb(1, *C("#cfeaff")[:3])
        ctx.set_source(g)
        ctx.paint()
        hy = cy + lift * ry * 1.9
        ctx.save()
        ctx.translate(cx, hy)
        ctx.rotate(-0.12 * lift)
        ctx.rectangle(-rx * 3, 0, rx * 6, ry * 4)
        setc(ctx, "#7fbf5a")
        ctx.fill()
        ctx.rectangle(-rx * 3, 0, rx * 6, 120 * k)
        setc(ctx, "#6b6f78")
        ctx.fill()
        sp = (t * 2600 * k) % (260 * k)
        for i in range(-12, 12):
            ctx.rectangle(i * 260 * k - sp, 50 * k, 130 * k, 18 * k)
        setc(ctx, "#ffffff")
        ctx.fill()
        for i in range(-6, 6):
            x = ((i * 380 - t * 1500) % 4560 - 2280) * k
            stroke_line(ctx, [(x, 0), (x, -90 * k)], 10 * k, "#6b4423")
            ell(ctx, x, -120 * k, 50 * k, 50 * k)
            setc(ctx, "#4f9a3a")
            ctx.fill()
        ctx.restore()
    else:
        g = cairo.LinearGradient(0, cy - ry, 0, cy + ry)
        g.add_color_stop_rgb(0, *C("#3f8fe6")[:3])
        g.add_color_stop_rgb(1, *C("#bfe3ff")[:3])
        ctx.set_source(g)
        ctx.paint()
        for i in range(6):
            x = cx + ((i * 300 - t * 260) % 1800 - 900) * k
            cloud(ctx, x, cy + ry * (-0.5 + 0.35 * (i % 3)), (1.0 + 0.3 * (i % 2)) * k)
    ctx.restore()
    ell(ctx, cx - rx * 0.35, cy - ry * 0.4, rx * 0.25, ry * 0.12)
    setc(ctx, "#ffffff", 0.25)
    ctx.fill()
    if blind > 0:
        ctx.save()
        ell(ctx, cx, cy, rx, ry)
        ctx.clip()
        ctx.rectangle(cx - rx, cy - ry, 2 * rx, 2 * ry * blind)
        fill_ol(ctx, "#f4f1ea", 4)
        ctx.restore()


def call_panel(ctx, cx, cy, s, lit=0.0, belt_sign=True, t=0.0):
    """Overhead passenger panel: reading light, air vent, call button."""
    rrect(ctx, cx - 420 * s, cy - 150 * s, 840 * s, 300 * s, 50 * s)
    fill_ol(ctx, "#d9dde3", 8)
    # air vent
    ell(ctx, cx - 270 * s, cy, 80 * s, 80 * s)
    fill_ol(ctx, "#bfc5cf", 6)
    ell(ctx, cx - 270 * s, cy, 40 * s, 40 * s)
    fill_ol(ctx, "#8b93a1", 5)
    # reading light
    ell(ctx, cx, cy, 70 * s, 70 * s)
    fill_ol(ctx, "#f4f4f4", 6)
    ctx.new_path()
    ctx.arc(cx, cy - 6 * s, 26 * s, PI * 0.9, PI * 2.1)
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(7 * s)
    ctx.stroke()
    stroke_line(ctx, [(cx - 12 * s, cy + 26 * s), (cx + 12 * s, cy + 26 * s)], 7 * s)
    # call button (person icon), glows when lit
    bx = cx + 270 * s
    if lit > 0:
        glow(ctx, bx, cy, 260 * s, "#ffb000", 0.7 * lit)
    ell(ctx, bx, cy, 75 * s, 75 * s)
    fill_ol(ctx, C("#ffb000") if lit > 0.3 else C("#f4f4f4"), 6)
    ell(ctx, bx, cy - 22 * s, 16 * s, 16 * s)
    setc(ctx, INK)
    ctx.fill()
    ctx.new_path()
    ctx.arc(bx, cy + 34 * s, 30 * s, PI, 2 * PI)
    ctx.close_path()
    ctx.fill()
    if belt_sign:
        rrect(ctx, cx - 160 * s, cy - 290 * s, 320 * s, 110 * s, 22 * s)
        fill_ol(ctx, "#2b2f36", 6)
        text(ctx, "FASTEN BELT", cx, cy - 235 * s, 40 * s, "#ffd23f" if (t * 2) % 1 < 0.75 else "#7a6a2a")


def eye_mask(ctx, x, y, r):
    rrect(ctx, x - r * 1.0, y - r * 0.28, r * 2.0, r * 0.38, r * 0.18)
    fill_ol(ctx, "#9b6bff", r * 0.03)
    stroke_line(ctx, [(x - r * 1.0, y - r * 0.12), (x - r * 1.05, y - r * 0.2)], r * 0.05, "#7a4fd6")
    for sd in (-1, 1):
        ctx.new_path()
        ctx.arc(x + sd * r * 0.38, y - r * 0.02, r * 0.14, PI * 1.15, PI * 1.85)
        setc(ctx, "#ffffff")
        ctx.set_line_width(r * 0.035)
        ctx.stroke()


def anger(ctx, x, y, r):
    ctx.save()
    ctx.translate(x, y)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(4):
        ctx.save()
        ctx.rotate(k * PI / 2)
        ctx.new_path()
        ctx.move_to(r * 0.25, -r)
        ctx.curve_to(r * 0.25, -r * 0.35, r * 0.35, -r * 0.25, r, -r * 0.25)
        ctx.set_source_rgba(*INK)
        ctx.set_line_width(r * 0.5)
        ctx.stroke_preserve()
        setc(ctx, "#ff2a2a")
        ctx.set_line_width(r * 0.28)
        ctx.stroke()
        ctx.restore()
    ctx.restore()


def plane(ctx, x, y, s, t):
    """Cartoon airliner flying right; (x, y) = fuselage centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rotate(-0.06 + 0.02 * math.sin(t * 2))
    poly(ctx, [(-60, 30), (180, 30), (40, 260), (-60, 260)], close=True)
    fill_ol(ctx, "#cfd6e0", 8)
    rrect(ctx, 40, 150, 120, 60, 30)
    fill_ol(ctx, "#9aa5b5", 7)
    poly(ctx, [(-430, -20), (-520, -230), (-420, -230), (-330, -20)], close=True)
    fill_ol(ctx, "#ff8c1a", 8)
    rrect(ctx, -480, -200, 70, 64, 10)
    fill_ol(ctx, "#f2a54a", 5)
    for sd in (-1, 1):
        ctx.new_path()
        ctx.arc(-445 + sd * 12, -172, 7, PI * 1.15, PI * 1.85)
        ctx.set_source_rgba(*INK)
        ctx.set_line_width(4)
        ctx.stroke()
    rrect(ctx, -520, -70, 900, 150, 75)
    fill_ol(ctx, "#ffffff", 8)
    ctx.new_path()
    ctx.move_to(330, -70)
    ctx.curve_to(440, -60, 470, 40, 330, 80)
    ctx.close_path()
    fill_ol(ctx, "#ffffff", 8)
    poly(ctx, [(360, -40), (420, -30), (430, 0), (360, 0)], close=True)
    fill_ol(ctx, "#2b3a5a", 5)
    ctx.rectangle(-500, 20, 860, 22)
    setc(ctx, "#2fb7ff")
    ctx.fill()
    for i in range(9):
        wx = -380 + i * 70
        ell(ctx, wx, -20, 18, 22)
        fill_ol(ctx, "#bfe3ff", 4)
    # Grandpa pressed against window 6
    mv.face(ctx, -380 + 5 * 70, -16, 22, "shock", GRANDPA, t, (0.6, 0), None, False)
    poly(ctx, [(-60, 30), (180, 30), (60, -170), (-20, -170)], close=True)
    fill_ol(ctx, "#e9eef4", 8)
    ctx.restore()


def cabin_row(ctx, t, people, yc=1500, xs=(250, 540, 830), ps=0.62, soft=0.0, scene="clouds", belts=True):
    """Front view of a row of three seats. `people`: list of dicts (P, expr, look, pose, vest, extra)."""
    cabin_bg(ctx, soft, scene, t)
    for x in xs:
        seat_back(ctx, x, yc)
    vests = []
    for x, p in zip(xs, people):
        if not p:
            continue
        py = yc + 330 * ps + p.get("dy", 0)
        P = p["P"]
        xx = x + p.get("dx", 0)
        if P is ROSA:
            rosa(ctx, xx, py, ps, p.get("expr", "happy"), t, p.get("look", (0, 0.2)), p.get("pose"))
        else:
            person(ctx, xx, py, ps, P, expr=p.get("expr", "neutral"), t=t, look=p.get("look", (0, 0.2)),
                   pose=p.get("pose") or {}, blink=p.get("blink"))
        if p.get("mask"):
            r = 190 * ps
            eye_mask(ctx, xx, py - 900 * ps - 0.06 * r, r)
        if p.get("vest") is not None:  # drawn last so the inflated vest bulges over the seat
            vests.append((xx, py, p["vest"], p.get("hands", True)))
    for x in xs:
        seat_front(ctx, x, yc)
        if belts:
            lap_belt(ctx, x, yc, 1.0)
    for ax in (xs[0] - 150, (xs[0] + xs[1]) / 2, (xs[1] + xs[2]) / 2, xs[2] + 150):
        armrest(ctx, ax, yc)
    for xx, py, k, hands in vests:
        vest(ctx, xx, py, ps, k, t, hands=hands)


# ---------------------------------------------------------------- shots
def sh_hook_button(ctx, t, d, g):
    setc(ctx, "#d6cfc2")
    ctx.paint()
    presses = (0.15, 0.55, 0.95, 1.35)
    near = min(abs(t - p) for p in presses)
    lit = flash(t, list(presses), 5)
    ctx.save()
    mv.cam(ctx, lerp(1.15, 1.0, eout(clamp(t / 0.3))), shake_amp=4 * lit, seed=g)
    call_panel(ctx, 540, 820, 1.15, lit=lit, t=t)
    ctx.restore()
    dip = 30 * max(0.0, 1 - near / 0.12)
    finger(ctx, 540 + 270 * 1.15 + 6, 820 + 70 + dip, 1.05, 0.15, GRANDPA)
    for i, p in enumerate(presses):
        if p < t < p + 0.4:
            pop_text(ctx, "DING!", 260 + (i % 2) * 520, 360 + (i % 2) * 40, 110, "#ffb000", t, p,
                     rot=-0.1 if i % 2 else 0.1)
    if t > 1.6:
        pop_text(ctx, "x 40", 270, 1250, 170, "#ff3b3b", t, 1.6, rot=-0.06)


def sh_attendant_sigh(ctx, t, d, g):
    cabin_bg(ctx, soft=0.35)
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.05, t / d))
    cu_rosa(ctx, "nervous", t, s=2.0, look=(-0.6, 0.2))
    ctx.restore()


def sh_cabin_wide(ctx, t, d, g):
    talk = mv.talk_amp("grandpa") is not None
    sh = 3 * math.sin(t * 40)
    cabin_row(ctx, t, [
        dict(P=GRANDPA, expr="furious" if talk else "nervous", look=(0.6, 0.2), dx=sh,
             pose=dict(la1=-40, la2=-10, ra1=40, ra2=10)),
        dict(P=GRANDMA, expr="smug", look=(-0.8, 0.1)),
        dict(P=LEO, expr="happy", look=(-0.8, 0.1)),
    ], scene="runway")
    for sd in (-1, 1):
        stroke_line(ctx, [(250 + sd * 150, 1310), (250 + sd * 190, 1290)], 8, (1, 1, 1, 0.8))


def sh_leo_relax(ctx, t, d, g):
    cabin_bg(ctx, soft=0.35)
    cu(ctx, LEO, "happy", t, s=2.1, look=(-0.4, 0.1), pose=dict(ra1=60, ra2=85))


def sh_belt_pull(ctx, t, d, g):
    cabin_bg(ctx, soft=0.15)
    yc, ss, ps = 1550, 1.4, 0.85
    xs = (320, 780)
    for x in xs:
        seat_back(ctx, x, yc, ss)
    py = yc + 330 * ps
    person(ctx, xs[1], py, ps, GRANDMA, expr="suspicious" if t > 2.2 else "neutral", t=t, look=(-0.8, 0.6))
    k = clamp(t / 1.8)
    reach = eout(clamp((t - 1.8) / 0.4))
    wig = 10 * math.sin(t * 20) * (1 - reach)
    buckle = (xs[1] + 90, yc - 8)
    # aim the arm at the buckle while reaching; the rest of the way is a cartoon stretch
    sh_x, sh_y = xs[0] + 125 * ps, py - 690 * ps
    aim = math.degrees(math.atan2(buckle[0] - sh_x, buckle[1] - sh_y))
    a1 = lerp(lerp(20, 95, k), aim, reach)
    a2 = lerp(lerp(40, 100, k) - wig, aim, reach)
    person(ctx, xs[0], py, ps, GRANDPA, expr="furious" if t < 2.2 else "smug", t=t, look=(1, 0.6),
           pose=dict(ra1=a1, ra2=a2))
    hx, hy = hand_at(xs[0], py, ps, 1, a1, a2)
    end = (lerp(hx, buckle[0], reach), lerp(hy, buckle[1], reach))
    for x in xs:
        seat_front(ctx, x, yc, ss)
    lap_belt(ctx, xs[1], yc, ss)
    stroke_line(ctx, [(xs[0] - 140, yc - 8), end], 30 + 6, INK)
    stroke_line(ctx, [(xs[0] - 140, yc - 8), end], 30, "#5b6273")
    rrect(ctx, end[0] - 26, end[1] - 20, 52, 40, 8)
    fill_ol(ctx, "#cfd6e0", 5)
    if reach > 0.01:
        limb(ctx, [(hx, hy), end], 58 * ps, GRANDPA["sleeve"])
    ell(ctx, end[0] - 20, end[1] + 4, 36, 34)
    fill_ol(ctx, GRANDPA["skin"])
    armrest(ctx, 550, yc, ss)
    if t > 2.2:
        pop_text(ctx, "CLICK!", 760, 1180, 90, "#ffffff", t, 2.2, rot=0.08)


def sh_belt_wrong(ctx, t, d, g):
    cabin_bg(ctx, soft=0.35)
    setc(ctx, "#b78ad8", 0.15)
    ctx.paint()
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.05, t / d))
    cu(ctx, GRANDMA, "suspicious", t, hx=560, s=2.0, look=(-0.3, 0.9))
    ctx.restore()
    stroke_line(ctx, [(-40, 1820), (1120, 1700)], 64 + 10, INK)
    stroke_line(ctx, [(-40, 1820), (1120, 1700)], 64, "#5b6273")


def sh_vest_demo(ctx, t, d, g):
    cabin_bg(ctx)
    for x in (-80, 1160):
        seat_back(ctx, x, 1560, 1.4)
    point = eout(clamp((t - 0.6) / 0.4))
    rosa(ctx, 540, 1880, 0.95, "happy", t, look=(0, 0.6),
         pose=dict(ra1=lerp(10, 60, point), ra2=lerp(10, 120, point)), vest_k=0.0)
    for x in (-80, 1160):
        seat_front(ctx, x, 1560, 1.4)
    if t > 1.6:
        ctx.save()
        ctx.translate(820, 900)
        rrect(ctx, -140, -60, 280, 120, 30)
        fill_ol(ctx, "#ffffff", 6)
        text(ctx, "DON'T", 0, -18, 44, "#e53935")
        text(ctx, "PULL!", 0, 30, 44, "#e53935")
        ctx.restore()


def sh_vest_pull(ctx, t, d, g):
    cabin_bg(ctx, soft=0.3)
    s = 1.8
    cu(ctx, GRANDPA, "suspicious", t, hx=540, hy=900, s=s, look=(0, 0.9))
    py = 900 + 900 * s
    vest(ctx, 540, py, s, 0.0, t, hands=False)
    tab_y = py - 440 * s + 190 * s * 0.4 + 82 * s
    pull = eout(clamp((t - 0.8) / 0.15)) * 50
    ell(ctx, 560, tab_y + pull + 20, 70, 60)
    fill_ol(ctx, GRANDPA["skin"])
    limb(ctx, [(980, 1980), (600, tab_y + pull + 40)], 120, GRANDPA["sleeve"])
    question(ctx, 860, 520, t, 0.3)




def sh_vest_poof(ctx, t, d, g):
    k = eback(clamp(t / 0.45))
    laugh = t > 0.9
    cabin_row(ctx, t, [
        dict(P=GRANDPA, expr="shock", look=(0, 0), vest=k),
        dict(P=GRANDMA, expr="shock", look=(-1, 0), dx=40 * k),
        dict(P=LEO, expr="happy" if laugh else "shock", look=(-1, 0), dy=-10 * abs(math.sin(t * 14)) if laugh else 0,
             pose=dict(la1=30, la2=100, ra1=-30, ra2=-100) if laugh else None),
    ], scene="runway")
    if 0.45 < t < 0.75:
        impact_star(ctx, 250, 1250, 260 * clamp((t - 0.45) / 0.15), seed=g)
    pop_text(ctx, "POOF!", 300, 620, 170, "#ff8c1a", t, 0.45, rot=-0.08)
    if laugh:
        for i in range(2):
            ph = (t * 1.4 + i / 2) % 1
            text(ctx, "HA", 860 + i * 90, 900 - ph * 160, 70, (1, 0.85, 0.25, 1 - ph), ol=12)


def sh_takeoff_window(ctx, t, d, g):
    setc(ctx, "#ece7dd")
    ctx.paint()
    lift = eio(clamp((t - 1.0) / 1.4))
    ctx.save()
    mv.cam(ctx, 1.0, shake_amp=6 + 6 * (1 - lift), seed=g)
    window(ctx, 540, 900, 400, 620, "runway", t, lift=lift)
    ctx.restore()
    if t < 1.2:
        pop_text(ctx, "VROOOM!", 540, 1690, 130, "#ffffff", t, 0.05)


def sh_takeoff_face(ctx, t, d, g):
    radial_bg(ctx, "#bfe3ff", "#3f8fe6", cy=900)
    speed_lines(ctx, W / 2, 900, C("#ffffff", 0.55), seed=g // 2)
    ctx.save()
    mv.cam(ctx, 1.0, shake_amp=14, seed=g)
    s = 1.9
    cu(ctx, GRANDPA, "shock", t, hy=880, s=s, look=(0, -0.3))
    vest(ctx, 540, 880 + 900 * s, s, 1.0, t)
    ctx.restore()
    for sd in (-1, 1):
        for i in range(3):
            y = 760 + i * 70
            stroke_line(ctx, [(540 + sd * 330, y), (540 + sd * (450 + 40 * math.sin(t * 30 + i)), y + 10)], 10,
                        (1, 1, 1, 0.9))


def sh_plane_exterior(ctx, t, d, g):
    g2 = cairo.LinearGradient(0, 0, 0, H)
    g2.add_color_stop_rgb(0, *C("#3f8fe6")[:3])
    g2.add_color_stop_rgb(1, *C("#cfeaff")[:3])
    ctx.set_source(g2)
    ctx.paint()
    for i in range(8):
        x = ((i * 330 - t * 420) % 1700) - 300
        cloud(ctx, x, 300 + (i * 233) % 1400, 1.4 + 0.5 * (i % 3), "#ffffff", 0.85)
    plane(ctx, lerp(470, 600, t / d), 1000 + 30 * math.sin(t * 2), 0.95, t)
    for i in range(4):
        x = ((i * 520 - t * 1400) % 1900) - 400
        cloud(ctx, x, 1500 + (i % 2) * 220, 2.4, "#ffffff", 0.95)


def call_cu(ctx, t, g, n, base, dot, expr):
    mv.halftone(ctx, base, dot, W / 2, 1000)
    s = 1.8
    cu(ctx, GRANDPA, expr, t, hx=500, hy=980, s=s, look=(0.6, -0.5), pose=dict(ra1=150, ra2=172))
    vest(ctx, 500, 980 + 900 * s, s, 1.0, t, hands=False)
    pop_text(ctx, "DING!", 820, 330, 120, "#ffb000", t, 0.1, rot=0.1)
    pop_text(ctx, f"x {n}", 820, 470, 100, "#ffffff", t, 0.15, rot=0.1)


def sh_call_a(ctx, t, d, g):
    call_cu(ctx, t, g, 38, "#ffd76a", "#f2b84a", "happy")


def sh_call_b(ctx, t, d, g):
    call_cu(ctx, t, g, 39, "#8fd3ff", "#5fb3e6", "shock")


def sh_call_c(ctx, t, d, g):
    call_cu(ctx, t, g, 40, "#ff9ec4", "#ff7fb0", "suspicious")


def sh_attendant_twitch(ctx, t, d, g):
    radial_bg(ctx, "#ff7a5c", "#8a1020", cy=1000)
    hx = 540 + (4 * math.sin(t * 60) if (t * 3) % 1 < 0.3 else 0)
    cu_rosa(ctx, "happy", t, hx=hx, s=2.0, look=(0, 0))
    r = 190 * 2.0
    anger(ctx, hx + 0.62 * r, 1000 - 0.75 * r, 46)
    if (t * 3) % 1 < 0.3:
        for i in range(3):
            stroke_line(ctx, [(hx - 0.34 * r - 90 - i * 18, 1000 - 0.3 * r + i * 30),
                              (hx - 0.34 * r - 140 - i * 18, 1000 - 0.3 * r + i * 30)], 9)
    for sd in (-1, 1):
        steam(ctx, hx + sd * 420, 980, t, sd)


def sh_grandma_sleep(ctx, t, d, g):
    cabin_bg(ctx, soft=0.3)
    setc(ctx, "#1b2a5a", 0.12 * clamp((t - 1.6) / 0.6))
    ctx.paint()
    s = 2.0
    mask = t > 1.6
    cu(ctx, GRANDMA, "smug", t, s=s, blink=mask, look=(0.4, 0))
    r = 190 * s
    k = eout(clamp((t - 1.5) / 0.3))
    if k > 0:
        eye_mask(ctx, 540, lerp(1000 - 0.9 * r, 1000 - 0.06 * r, k), r)
    if mask:
        zzz(ctx, 760, 520, t)


def sh_sunset(ctx, t, d, g):
    setc(ctx, "#2a1f3d")
    ctx.paint()
    window(ctx, 540, 720, 420, 560, "sunset", t)
    glow(ctx, 540, 1100, 700, "#ffb347", 0.35)
    s = 1.6
    happy = t > 0.9
    cu(ctx, GRANDPA, "victory" if happy else "shock", t, hx=540, hy=1380, s=s, look=(0, -0.8))
    vest(ctx, 540, 1380 + 900 * s, s, 1.0, t)
    if happy:
        mv.sparkles(ctx, t, seed=14, n=8, col="#fff3b0", area=(120, 300, 960, 1200))


def sh_pilot_pa(ctx, t, d, g):
    cabin_bg(ctx, soft=0.2)
    amp = mv.talk_amp("pilot") or 0.0
    ctx.save()
    mv.cam(ctx, 1.6, 540, 520)
    rrect(ctx, 300, 380, 480, 280, 40)
    fill_ol(ctx, "#d9dde3", 7)
    ell(ctx, 440, 520, 90, 90)
    fill_ol(ctx, "#bfc5cf", 6)
    setc(ctx, "#5b6273")
    for r in range(-3, 4):
        for c in range(-3, 4):
            if r * r + c * c <= 10:
                ell(ctx, 440 + c * 22, 520 + r * 22, 6, 6)
    ctx.fill()
    for k in range(3):
        ctx.new_path()
        ctx.arc(440, 520, 120 + k * 40, -0.5, 0.5)
        setc(ctx, "#2fb7ff", clamp(amp * 1.6 - k * 0.3))
        ctx.set_line_width(10)
        ctx.stroke()
    ell(ctx, 680, 520, 50, 50)
    fill_ol(ctx, "#ffd23f" if t < 0.6 else "#f4f4f4", 5)
    ctx.restore()
    pop_text(ctx, "DING-DONG", 540, 560, 110, "#ffffff", t, 0.02)
    ctx.save()
    ctx.translate(540, 1660)
    rrect(ctx, -300, -70, 600, 140, 36)
    fill_ol(ctx, "#2b2f36", 7)
    text(ctx, "LANDED", 0, 0, 80, "#25c486")
    ctx.restore()


def sh_grandpa_no(ctx, t, d, g):
    mv.halftone(ctx, "#ff5a36", "#d93a1a", W / 2, 1000)
    speed_lines(ctx, W / 2, 1000, C("#ffffff", 0.35), seed=g // 2)
    ctx.save()
    mv.cam(ctx, lerp(1.35, 1.0, eout(clamp(t / 0.2))), shake_amp=shake(t, 0.05, 16, 7), seed=g)
    s = 1.8
    cu(ctx, GRANDPA, "furious", t, hy=940, s=s, look=(0, 0.2))
    vest(ctx, 540, 940 + 900 * s, s, 1.0, t)
    ctx.restore()


def sh_stuck(ctx, t, d, g):
    cabin_bg(ctx, soft=0.1)
    yc, ss, ps = 1560, 1.3, 0.8
    sx = 300
    popped = t > 2.4
    seat_back(ctx, sx, yc, ss)
    tug = 18 * math.sin(t * 9) if not popped else 0
    py = yc + 330 * ps
    rx_lean = 18 + tug * 0.3
    rpose = dict(lean=rx_lean, la1=-100, la2=-95)
    rosa_x, rosa_y, rs = 830, 1890, 0.85
    if popped:
        tt = t - 2.4
        k = eout(clamp(tt / 0.5))
        rosa_x += 120 * k
        rpose = dict(lean=lerp(18, 40, k), la1=-150, la2=-170, ra1=150, ra2=170)
    lhx, lhy = hand_at(rosa_x, rosa_y, rs, -1, -100, -95)
    # hand_at ignores lean; rotate the hand about the hip like person() does
    hip_y, a = rosa_y - 330 * rs, math.radians(rpose.get("lean", 0))
    lhx, lhy = (rosa_x + (lhx - rosa_x) * math.cos(a) - (lhy - hip_y) * math.sin(a),
                hip_y + (lhx - rosa_x) * math.sin(a) + (lhy - hip_y) * math.cos(a))
    if not popped:
        person(ctx, sx + tug * 0.4, py, ps, GRANDPA, expr="furious", t=t, look=(1, 0),
               pose=dict(ra1=60, ra2=70, la1=-40, la2=-10))
        vest(ctx, sx + tug * 0.4, py, ps, 1.0, t)
        limb(ctx, [(sx + 360 * ps, py - 420 * ps), (lhx - 30, lhy)], 50, GRANDPA["sleeve"])
        ell(ctx, lhx - 30, lhy, 32, 30)
        fill_ol(ctx, GRANDPA["skin"])
    seat_front(ctx, sx, yc, ss)
    armrest(ctx, sx + 200, yc, ss)
    rosa(ctx, rosa_x, rosa_y, rs, "nervous" if not popped else "shock", t, look=(-1, 0), pose=rpose)
    person(ctx, rosa_x + 210, 1910, 0.72, LEO, expr="furious" if not popped else "shock", t=t, look=(-1, 0),
           pose=dict(lean=14 + tug * 0.2, la1=-95, la2=-90) if not popped else dict(lean=40, la1=-150, la2=-170))
    if popped:
        tt = t - 2.4
        fx = sx + 1600 * tt
        fy = py - 400 * ps - 500 * tt + 900 * tt * tt
        ctx.save()
        ctx.translate(fx, fy)
        ctx.rotate(tt * 5)
        ctx.translate(-fx, -fy)
        person(ctx, fx, fy + 400 * ps, ps, GRANDPA, expr="shock", t=t, look=(0, 0),
               pose=dict(la1=-150, la2=-170, ra1=150, ra2=170))
        vest(ctx, fx, fy + 400 * ps, ps, 1.0, t, hands=False)
        ctx.restore()
        pop_text(ctx, "POP!", sx + 40, 900, 190, "#ffd23f", t, 2.4, rot=-0.1)
        for i in range(5):
            stroke_line(ctx, [(fx - 260 - i * 30, fy - 120 + i * 60), (fx - 520 - i * 30, fy - 120 + i * 60)], 10,
                        (1, 1, 1, 0.8))
    else:
        for i in range(3):
            ph = (t * 1.5 + i / 3) % 1
            ell(ctx, 620 + i * 40, 1000 - ph * 120, 14, 18)
            setc(ctx, "#8fdcff", 1 - ph)
            ctx.fill()


def sh_final(ctx, t, d, g):
    if t < 1.5:
        setc(ctx, "#d6cfc2")
        ctx.paint()
        lit = flash(t, [0.15], 3) if t > 0.15 else 0
        call_panel(ctx, 540, 820, 1.15, lit=lit, belt_sign=False, t=t)
        dip = 30 * max(0.0, 1 - abs(t - 0.15) / 0.12)
        finger(ctx, 540 + 270 * 1.15 + 6, 820 + 70 + dip, 1.05, 0.15, GRANDPA)
        pop_text(ctx, "DING!", 300, 380, 120, "#ffb000", t, 0.15, rot=0.1)
        return
    tt = t - 1.5
    cabin_bg(ctx, soft=0.25)
    s = 1.8
    cu(ctx, GRANDPA, "victory", t, hy=980 - 10 * abs(math.sin(t * 6)), s=s, look=(0.6, -0.2),
       pose=dict(ra1=150, ra2=172))
    vest(ctx, 540, 980 + 900 * s, s, 0.25, t, hands=False)
    mv.sparkles(ctx, tt, seed=17, n=6, col="#ffd23f", area=(120, 400, 960, 1000))


SHOT_FUNCS = {
    "hook_button": sh_hook_button, "attendant_sigh": sh_attendant_sigh, "cabin_wide": sh_cabin_wide,
    "leo_relax": sh_leo_relax, "belt_pull": sh_belt_pull, "belt_wrong": sh_belt_wrong,
    "vest_demo": sh_vest_demo, "vest_pull": sh_vest_pull, "vest_poof": sh_vest_poof,
    "takeoff_window": sh_takeoff_window, "takeoff_face": sh_takeoff_face, "plane_exterior": sh_plane_exterior,
    "call_a": sh_call_a, "call_b": sh_call_b, "call_c": sh_call_c, "attendant_twitch": sh_attendant_twitch,
    "grandma_sleep": sh_grandma_sleep, "sunset": sh_sunset, "pilot_pa": sh_pilot_pa,
    "grandpa_no": sh_grandpa_no, "stuck": sh_stuck, "final": sh_final,
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
