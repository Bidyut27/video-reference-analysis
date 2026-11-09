#!/usr/bin/env python3
"""Render the picture for "Leo vs. Homework" (Laughing Box, episode 4).

Characters come from episode 1, Leo and his room from episode 2, and small
helpers from episode 3. New here: the desk, books, clock, pencil, sharpener,
crayon and Mittens the cat. Drawing is in a 1080x1920 canvas rendered at SCALE
(default 2 = 2160x3840 4K).

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
from ep1_video import (GRANDMA, GRANDPA, INK, PI, C, clamp, cu, darker, eback, eio, eout, ell,  # noqa: E402
                       fill_ol, flash, glow, impact_star, lerp, limb, person, poly, radial_bg, rrect,
                       setc, shake, speed_lines, star4, steam, stroke_line, text, vignette, walk_pose)

LEO, hand_at = e2.LEO, e2.hand_at
question = e3.question
SCALE = float(os.environ.get("SCALE", "2"))
DESK_Y = 1450

TRACK_PATH = os.environ.get("VOICE_TRACK", os.path.join(ep1.HERE, "voice_track.json"))
if os.path.exists(TRACK_PATH):
    with open(TRACK_PATH) as _f:
        mv.TRACK = json.load(_f)["lines"]

SCRIBBLES = ["2+2=5", "7x8=78", "π=3", "x=YES!", "100%", "∞+1", "=42", "1+1=11"]


def mixc(a, b, k):
    ca, cb = C(a), C(b)
    return tuple(lerp(ca[i], cb[i], k) for i in range(4))


def pop_text(ctx, s, x, y, size, col, t, t0, rot=0.0, ol=None):
    if t < t0:
        return
    k = eback(clamp((t - t0) / 0.2))
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(k, k)
    text(ctx, s, 0, 0, size, col, ol=ol or size * 0.16)
    ctx.restore()


# ---------------------------------------------------------------- sets
def room_bg(ctx, night=0.0):
    """Leo's room (episode 2) with a window that goes from day to night."""
    e2.leo_bg(ctx)
    rrect(ctx, 700, 300, 340, 440, 14)
    fill_ol(ctx, "#ffffff")
    g = cairo.LinearGradient(0, 322, 0, 718)
    g.add_color_stop_rgb(0, *mixc("#8fd0ff", "#0f1840", night)[:3])
    g.add_color_stop_rgb(1, *mixc("#d8f1ff", "#2b3a78", night)[:3])
    ctx.set_source(g)
    ctx.rectangle(722, 322, 296, 396)
    ctx.fill()
    ctx.save()
    ctx.rectangle(722, 322, 296, 396)
    ctx.clip()
    sy = lerp(420, 760, night)
    ell(ctx, 950, sy, 42, 42)
    setc(ctx, "#ffd23f", 1 - night)
    ctx.fill()
    if night > 0.3:
        a = clamp((night - 0.3) / 0.5)
        my = lerp(780, 420, a)
        ell(ctx, 800, my, 36, 36)
        setc(ctx, "#fff6c8", a)
        ctx.fill()
        ell(ctx, 815, my - 10, 32, 32)
        setc(ctx, mixc("#8fd0ff", "#0f1840", night))
        ctx.fill()
        for x, y in ((760, 360), (900, 400), (980, 560), (850, 640), (760, 520), (960, 350)):
            star4(ctx, x, y, 12, (1, 1, 1, a))
    ell(ctx, 780, 690, 140, 40)
    setc(ctx, mixc("#8ccf6a", "#1c3a2a", night))
    ctx.fill()
    ctx.restore()
    stroke_line(ctx, [(870, 322), (870, 718)], 10, "#ffffff")
    stroke_line(ctx, [(722, 520), (1018, 520)], 10, "#ffffff")
    if night > 0:
        setc(ctx, "#0b1033", 0.42 * night)
        ctx.rectangle(0, 0, W, H)
        ctx.fill()


def desk(ctx, night=0.0, lamp=True):
    y = DESK_Y
    if lamp:
        glow(ctx, 260, y - 240, 520, "#fff3b0", 0.12 + 0.45 * night)
    rrect(ctx, -20, y, W + 40, 50, 12)
    fill_ol(ctx, "#c98b55")
    ctx.rectangle(-10, y + 50, W + 20, H - y)
    fill_ol(ctx, "#9b6334")
    for x in (70, 640):
        rrect(ctx, x, y + 120, 370, 170, 14)
        fill_ol(ctx, "#b07a4a", 6)
        rrect(ctx, x + 145, y + 190, 80, 24, 12)
        fill_ol(ctx, "#e9c46a", 5)
    if lamp:
        ell(ctx, 130, y - 8, 75, 18)
        fill_ol(ctx, "#2fb7ff", 6)
        stroke_line(ctx, [(130, y - 10), (170, y - 250), (300, y - 320)], 22, INK)
        stroke_line(ctx, [(130, y - 10), (170, y - 250), (300, y - 320)], 12, "#2b2f36")
        poly(ctx, [(250, y - 360), (360, y - 300), (330, y - 230), (210, y - 290)], close=True)
        fill_ol(ctx, "#2fb7ff", 6)


def clock(ctx, x, y, r, minutes, sec=None):
    ell(ctx, x, y, r, r)
    fill_ol(ctx, "#e94f37", max(6, r * 0.04))
    ell(ctx, x, y, r * 0.86, r * 0.86)
    fill_ol(ctx, "#ffffff", max(4, r * 0.025))
    for i in range(12):
        a = i * PI / 6
        stroke_line(ctx, [(x + math.cos(a) * r * 0.68, y + math.sin(a) * r * 0.68),
                          (x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78)], r * 0.04)
    ha = (minutes / 720.0) * 2 * PI
    ma = (minutes / 60.0) * 2 * PI
    stroke_line(ctx, [(x, y), (x + math.sin(ha) * r * 0.42, y - math.cos(ha) * r * 0.42)], r * 0.07)
    stroke_line(ctx, [(x, y), (x + math.sin(ma) * r * 0.64, y - math.cos(ma) * r * 0.64)], r * 0.045)
    if sec is not None:
        sa = sec / 60.0 * 2 * PI
        stroke_line(ctx, [(x, y), (x + math.sin(sa) * r * 0.7, y - math.cos(sa) * r * 0.7)], r * 0.018, "#e94f37")
    ell(ctx, x, y, r * 0.06, r * 0.06)
    setc(ctx, INK)
    ctx.fill()


def book(ctx, cx, bottom, w, h, col, title, tilt=0.0):
    ctx.save()
    ctx.translate(cx, bottom)
    ctx.rotate(tilt)
    rrect(ctx, -w / 2, -h, w, h, 18)
    fill_ol(ctx, col, max(6, h * 0.025))
    ctx.rectangle(w / 2 - 70, -h + 18, 48, h - 36)
    fill_ol(ctx, "#fff8ea", 5)
    for k in range(1, 6):
        yy = -h + 18 + k * (h - 36) / 6
        stroke_line(ctx, [(w / 2 - 66, yy), (w / 2 - 26, yy)], 3, "#d8cbb0")
    ctx.rectangle(-w / 2 + 28, -h + 20, 20, h - 40)
    setc(ctx, darker(col, 0.8))
    ctx.fill()
    text(ctx, title, -30, -h / 2, min(h * 0.45, (w - 160) / max(1, len(title)) * 1.45), "#ffffff", ol=h * 0.05)
    ctx.restore()


def notebook(ctx, cx, y=DESK_Y + 2, w=380):
    poly(ctx, [(cx - w / 2, y), (cx + w / 2, y), (cx + w / 2 - 40, y - 56), (cx - w / 2 + 40, y - 56)], close=True)
    fill_ol(ctx, "#ffffff", 6)
    for k in range(1, 4):
        yy = y - k * 14
        dx = 40 * k * 14 / 56
        stroke_line(ctx, [(cx - w / 2 + dx + 20, yy), (cx + w / 2 - dx - 20, yy)], 2.5, "#9cc3f0")
    rrect(ctx, cx - w / 2, y - 4, w, 14, 5)
    fill_ol(ctx, "#2b6cd8", 5)


def phone_flat(ctx, x, y, s, rot=0.0, mode="play", t=0.0):
    e2.phone(ctx, x, y, s, rot, screen="dark", t=t)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    if mode == "play":
        rrect(ctx, -58, -40, 116, 80, 18)
        setc(ctx, "#ff2a2a")
        ctx.fill()
        poly(ctx, [(-16, -22), (-16, 22), (24, 0)], close=True)
        setc(ctx, "#ffffff")
        ctx.fill()
    elif mode == "back":
        rrect(ctx, -80, -150, 160, 300, 26)
        fill_ol(ctx, "#2f3440", 6)
        for dy in (0, 34):
            ell(ctx, -40, -110 + dy, 13, 13)
            fill_ol(ctx, "#111111", 3)
    ctx.restore()


def cat(ctx, x, y, s, expr="neutral", t=0.0, look=(0, 0), jump=False):
    """Mittens: orange tabby sitting; (x, y) is the floor contact point; s=1 -> ~240 px wide."""
    col, dk, ol = "#f2a541", "#d9822b", 7
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if jump:
        ctx.rotate(-0.25)
    # tail
    sw = 25 * math.sin(t * 3)
    ctx.new_path()
    ctx.move_to(70, -30)
    ctx.curve_to(210, -30, 200 + sw, -200, 130 + sw, -250)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(50)
    ctx.stroke_preserve()
    setc(ctx, col)
    ctx.set_line_width(34)
    ctx.stroke()
    ell(ctx, 0, -120, 112, 122)
    fill_ol(ctx, col, ol)
    ell(ctx, 0, -95, 60, 80)
    setc(ctx, "#fde2b8")
    ctx.fill()
    for k in range(3):
        ctx.new_path()
        ctx.arc(-70, -150 + k * 40, 30, -0.6, 0.6)
        setc(ctx, dk)
        ctx.set_line_width(9)
        ctx.stroke()
    for sd in (-1, 1):
        ell(ctx, sd * 45, -14, 40, 22)
        fill_ol(ctx, col, ol)
    # head
    for sd in (-1, 1):
        poly(ctx, [(sd * 88, -300), (sd * 72, -395), (sd * 22, -350)], close=True)
        fill_ol(ctx, col, ol)
        poly(ctx, [(sd * 74, -315), (sd * 66, -372), (sd * 36, -345)], close=True)
        setc(ctx, "#ff9ec4")
        ctx.fill()
    ell(ctx, 0, -282, 98, 86)
    fill_ol(ctx, col, ol)
    for k in (-1, 0, 1):
        stroke_line(ctx, [(k * 22, -360), (k * 18, -330)], 8, dk)
    for sd in (-1, 1):
        ex, ey = sd * 40, -292
        if expr == "happy":
            ctx.new_path()
            ctx.arc(ex, ey + 8, 16, PI * 1.15, PI * 1.85)
            ctx.set_source_rgba(*INK)
            ctx.set_line_width(7)
            ctx.stroke()
            continue
        ell(ctx, ex, ey, 21, 24)
        fill_ol(ctx, "#b8e986", 5)
        ell(ctx, ex + look[0] * 7, ey + look[1] * 6, 6, 17)
        setc(ctx, INK)
        ctx.fill()
        if expr == "smug":
            ctx.save()
            ell(ctx, ex, ey, 21, 24)
            ctx.clip()
            ctx.rectangle(ex - 30, ey - 30, 60, 30)
            setc(ctx, col)
            ctx.fill()
            ctx.restore()
            stroke_line(ctx, [(ex - 22, ey), (ex + 22, ey)], 6)
    poly(ctx, [(-12, -262), (12, -262), (0, -250)], close=True)
    fill_ol(ctx, "#ff7fb0", 4)
    ctx.new_path()
    if expr == "smug":
        ctx.move_to(-22, -238)
        ctx.curve_to(-8, -228, 14, -232, 30, -250)
    else:
        ctx.arc(-11, -244, 11, 0.2, PI - 0.2)
        ctx.new_sub_path()
        ctx.arc(11, -244, 11, 0.2, PI - 0.2)
    ctx.set_source_rgba(*INK)
    ctx.set_line_width(5)
    ctx.stroke()
    for sd in (-1, 1):
        for dy in (-8, 8):
            stroke_line(ctx, [(sd * 40, -248 + dy * 0.4), (sd * 120, -256 + dy * 1.6)], 3.5)
    ctx.restore()


def pencil(ctx, tx, ty, ang, L=520, broken=False, phase=0.0):
    """Yellow pencil with its tip at (tx, ty); the body extends along `ang`."""
    ctx.save()
    ctx.translate(tx, ty)
    ctx.rotate(ang)
    if broken:
        poly(ctx, [(70, -22), (88, -6), (76, 4), (92, 20), (110, 32), (110, -32)], close=True)
        fill_ol(ctx, "#f3d2a2", 6)
    else:
        poly(ctx, [(0, 0), (40, -11), (40, 11)], close=True)
        fill_ol(ctx, "#3a3a3a", 5)
        poly(ctx, [(40, -11), (110, -32), (110, 32), (40, 11)], close=True)
        fill_ol(ctx, "#f3d2a2", 6)
    body = max(0.0, L - 180)
    if body > 0:
        ctx.rectangle(110, -32, body, 64)
        fill_ol(ctx, "#ffcf33", 6)
        for k in range(2):
            off = ((phase + k * 0.5) % 1) * 64 - 32
            stroke_line(ctx, [(112, off), (110 + body - 2, off)], 4, "#e0a800")
        ctx.rectangle(110 + body, -34, 30, 68)
        fill_ol(ctx, "#c0c0c0", 6)
        rrect(ctx, 140 + body, -32, 46, 64, 14)
        fill_ol(ctx, "#ff8fab", 6)
    ctx.restore()


def hand(ctx, x, y, P, ang=0.6, r=46):
    """Fist at (x, y) with the sleeve leaving the frame along `ang` (radians, 0 = right)."""
    limb(ctx, [(x + math.cos(ang) * 1400, y + math.sin(ang) * 1400), (x, y)], 120, P["sleeve"])
    ell(ctx, x, y, r * 1.1, r)
    fill_ol(ctx, P["skin"])


def page_bg(ctx, rot=-0.04, title=None):
    setc(ctx, "#c98b55")
    ctx.paint()
    ctx.save()
    ctx.translate(540, 980)
    ctx.rotate(rot)
    rrect(ctx, -440, -760, 880, 1520, 16)
    fill_ol(ctx, "#fffdf6", 8)
    for k in range(-13, 15):
        stroke_line(ctx, [(-420, k * 52), (420, k * 52)], 3, "#b9d4f2")
    stroke_line(ctx, [(-330, -740), (-330, 740)], 4, "#ff8f8f")
    if title:
        text(ctx, title, 40, -690, 70, "#e53935")
    ctx.restore()


def scribble_pts(x0, y0, w, rows=3, row_h=104, n=60, seed=1):
    rnd = random.Random(seed)
    pts = []
    for r in range(rows):
        for i in range(n):
            u = i / (n - 1)
            pts.append((x0 + u * w, y0 + r * row_h + 18 * math.sin(u * 40 + r) + rnd.uniform(-6, 6)))
    return pts


def draw_partial(ctx, pts, k, col, w):
    m = int(len(pts) * clamp(k))
    if m < 2:
        return pts[0] if pts else (0, 0)
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:m]:
        ctx.line_to(*p)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    setc(ctx, col)
    ctx.set_line_width(w)
    ctx.stroke()
    return pts[m - 1]


def leo_seated(ctx, t, expr, look=(0, 0.6), pose=None, x=540, s=0.95):
    person(ctx, x, 1800, s, LEO, expr=expr, t=t, look=look, pose=pose or {})


def slam(ctx, t, title, col, w, h, t_land=0.4, expr_after="shock"):
    room_bg(ctx)
    k = clamp(t / t_land) ** 2
    ctx.save()
    mv.cam(ctx, 1.0, shake_amp=shake(t, t_land, 26, 8), seed=int(t * 100))
    leo_seated(ctx, t, "neutral" if t < t_land else expr_after, look=(0, -0.8) if t < t_land else (0, 0.2),
               pose=dict(la1=-60, la2=-150, ra1=60, ra2=150) if t >= t_land else None)
    desk(ctx)
    bottom = lerp(-80, DESK_Y + 2, k)
    book(ctx, 540, bottom, w, h, col, title, tilt=0.03 * (1 - k))
    ctx.restore()
    if t >= t_land:
        tt = t - t_land
        for sd in (-1, 1):
            for i in range(3):
                ph = clamp(tt / 0.6)
                ell(ctx, 540 + sd * (w / 2 + 40 + ph * 160 + i * 40), DESK_Y - 30 - ph * 60 - i * 20,
                    40 + 30 * ph, 30 + 20 * ph)
                setc(ctx, "#ffffff", 0.8 * (1 - ph))
                ctx.fill()
        pop_text(ctx, "SLAM!", 540, 360, 170, "#ffd23f", t, t_land, rot=-0.08)
        k2 = flash(t, [t_land], 7)
        setc(ctx, "#ffffff", 0.6 * k2)
        ctx.paint()


# ---------------------------------------------------------------- shots
def sh_hook_book(ctx, t, d, g):
    slam(ctx, t, "MATH", "#e53935", 760, 330)


def sh_leo_scream(ctx, t, d, g):
    mv.halftone(ctx, "#3a6fd8", "#2f5fbf", W / 2, 1000)
    speed_lines(ctx, W / 2, 1000, C("#ffffff", 0.35), seed=g // 2)
    ctx.save()
    mv.cam(ctx, lerp(1.35, 1.0, eout(clamp(t / 0.2))), shake_amp=shake(t, 0.05, 18, 7), seed=g)
    cu(ctx, LEO, "shock", t, s=2.1, look=(0, 0.3), pose=dict(la1=-60, la2=-160, ra1=60, ra2=160))
    ctx.restore()


def sh_setup_sit(ctx, t, d, g):
    room_bg(ctx)
    jit = 8 * (flash(t, [1.6, 2.0], 10))
    leo_seated(ctx, t, "smug", look=(0, 0.4),
               pose=dict(la1=35 + jit, la2=100, ra1=-35 - jit, ra2=-100, bob=4 * jit))
    desk(ctx)
    book(ctx, 230, DESK_Y + 2, 300, 140, "#e53935", "MATH")
    notebook(ctx, 640)
    for t0, x in ((1.6, 380), (2.0, 700)):
        if t0 < t < t0 + 0.45:
            pop_text(ctx, "CRACK!", x, 1230, 70, "#ffffff", t, t0, rot=-0.1 if x < 540 else 0.1)


def sh_clock_tick(ctx, t, d, g):
    radial_bg(ctx, "#a9d0f5", "#5b84b8", cy=900)
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.08, t / d))
    clock(ctx, 540, 900, 380, 240, sec=int(t * 2) * 5)
    ctx.restore()
    text(ctx, "4:00 PM", 540, 1450, 90, "#ffffff", ol=16)


def sh_phone_buzz(ctx, t, d, g):
    room_bg(ctx, 0.05)
    tempted = t > 0.85
    leo_seated(ctx, t, "happy" if tempted else "suspicious", look=(1, 0.5),
               pose=dict(ra1=60 if tempted else 10, ra2=110 if tempted else 10, lean=6 if tempted else 0))
    desk(ctx)
    notebook(ctx, 520)
    buzzing = t < 0.45 or 0.8 < t < 1.25
    jit = 6 * math.sin(t * 80) if buzzing else 0
    phone_flat(ctx, 860 + jit, 1330, 0.75, rot=0.12 + 0.02 * jit, mode="play", t=t)
    if buzzing:
        for k in range(2):
            ph = (t * 3 + k / 2) % 1
            for sd in (-1, 1):
                ctx.new_path()
                ctx.arc(860, 1330, 150 + ph * 90, -0.5 if sd > 0 else PI - 0.5, 0.5 if sd > 0 else PI + 0.5)
                setc(ctx, "#ffd23f", 1 - ph)
                ctx.set_line_width(10)
                ctx.stroke()


def sh_phone_watch(ctx, t, d, g):
    night = eio(clamp((t - 0.2) / (d - 0.5)))
    room_bg(ctx, night)
    clock(ctx, 190, 260, 110, 240 + night * 300)
    hx, hy, s = 470, 1000, 1.8
    pose = dict(la1=30, la2=150, ra1=-30, ra2=-150)
    glow(ctx, hx, hy, 520, "#9fd8ff", 0.25 + 0.25 * night + 0.06 * math.sin(t * 25))
    cu(ctx, LEO, "happy", t, hx=hx, hy=hy + 6 * math.sin(t * 9), s=s, pose=pose)
    px = (hand_at(hx, hy + 900 * s, s, -1, 30, 150)[0] + hand_at(hx, hy + 900 * s, s, 1, -30, -150)[0]) / 2
    py = hand_at(hx, hy + 900 * s, s, -1, 30, 150)[1]
    phone_flat(ctx, px, py - 120, 1.1, mode="back")
    for i in range(3):
        ph = (t * 1.2 + i / 3) % 1
        ctx.save()
        ctx.translate(180 + i * 360, 1250 - ph * 300)
        ctx.rotate(-0.2 + 0.2 * i)
        text(ctx, "HA", 0, 0, 70, (1, 0.85, 0.25, 1 - ph), ol=12)
        ctx.restore()


def sh_night_shock(ctx, t, d, g):
    room_bg(ctx, 1.0)
    ctx.save()
    mv.cam(ctx, lerp(1.25, 1.0, eout(clamp(t / 0.2))), shake_amp=shake(t, 0.05, 16, 7), seed=g)
    cu(ctx, LEO, "shock", t, hx=500, s=2.0, look=(1, -0.4))
    ctx.restore()
    pop_text(ctx, "!", 880, 520, 230, "#ff3b3b", t, 0.1)


def cat_scene(ctx, t, leo_expr, look=(0, 0.6)):
    room_bg(ctx, 1.0)
    leo_seated(ctx, t, leo_expr, look=look, pose=dict(la1=-30, la2=-110, ra1=30, ra2=110))
    desk(ctx, 1.0)
    notebook(ctx, 560)


def sh_cat_sit(ctx, t, d, g):
    cat_scene(ctx, t, "furious" if t > 0.9 else "shock")
    if t < 0.7:
        u = eio(t / 0.7)
        cat(ctx, lerp(-120, 560, u), lerp(1500, DESK_Y - 30, u) - 420 * math.sin(PI * u), 0.8, "neutral", t,
            jump=True)
    else:
        cat(ctx, 560, DESK_Y - 30, 0.8, "smug", t, look=(-0.6, 0))


def sh_cat_loop(ctx, t, d, g):
    cat_scene(ctx, t, "furious", look=(0, 0.7))
    p = 1.1
    n = int(t / p)
    u = (t % p) / p if n < 3 else 1.0
    nb, fl = (560, DESK_Y - 30), (190, 1880)
    if u < 0.3:
        k = eio(u / 0.3)
        x, y, jump = lerp(nb[0], fl[0], k), lerp(nb[1], fl[1], k) - 200 * math.sin(PI * k), True
        for i in range(4):
            stroke_line(ctx, [(x + 120 + i * 30, y - 150 + i * 40), (x + 260 + i * 30, y - 190 + i * 40)], 8,
                        (1, 1, 1, 0.7))
    elif u < 0.5:
        x, y, jump = fl[0], fl[1], False
    elif u < 0.68:
        k = eio((u - 0.5) / 0.18)
        x, y, jump = lerp(fl[0], nb[0], k), lerp(fl[1], nb[1], k) - 300 * math.sin(PI * k), True
    else:
        x, y, jump = nb[0], nb[1], False
    cat(ctx, x, y, 0.8, "smug" if not jump else "neutral", t, look=(-0.6, 0), jump=jump)
    for i in range(min(n + (1 if u > 0.68 else 0), 3)):
        pop_text(ctx, str(i + 1) + "!", 180 + i * 140, 420, 90, "#ffd23f", t, (i + 0.68) * p)


def sh_cat_smug(ctx, t, d, g):
    radial_bg(ctx, "#ffe3a8", "#f2a541", cy=1000)
    ctx.save()
    mv.cam(ctx, lerp(1.0, 1.06, t / d))
    cat(ctx, 540, 1900, 3.1, "smug", t, look=(-0.4, 0))
    ctx.restore()
    for i in range(3):
        ph = (t * 1.5 + i / 3) % 1
        ctx.new_path()
        ctx.arc(540, 960, 460 + ph * 160, PI * 1.15, PI * 1.85)
        setc(ctx, "#ffffff", 0.7 * (1 - ph))
        ctx.set_line_width(10)
        ctx.stroke()
    pop_text(ctx, "purr...", 540, 300, 100, "#ffffff", t, 0.2, ol=14)


def sh_pencil_snap(ctx, t, d, g):
    page_bg(ctx)
    pts = scribble_pts(260, 760, 560, rows=3, n=50, seed=4)
    snap = 0.7
    tip = draw_partial(ctx, pts, (min(t, snap) / snap) * 0.75, "#555555", 7)
    ang = -0.9
    if t < snap:
        pencil(ctx, tip[0], tip[1], ang)
        hand(ctx, tip[0] + math.cos(ang) * 260, tip[1] + math.sin(ang) * 260 + 60, LEO, ang=0.9)
    else:
        tt = t - snap
        pencil(ctx, tip[0], tip[1] - 40 * min(1, tt * 6), ang, broken=True)
        hand(ctx, tip[0] + math.cos(ang) * 260, tip[1] + math.sin(ang) * 260 + 60 - 40 * min(1, tt * 6), LEO,
             ang=0.9)
        ctx.save()
        ctx.translate(tip[0] - 300 * tt, tip[1] - 600 * tt + 900 * tt * tt)
        ctx.rotate(tt * 18)
        poly(ctx, [(0, 0), (40, -11), (80, -22), (80, 22), (40, 11)], close=True)
        fill_ol(ctx, "#f3d2a2", 5)
        ctx.restore()
        pop_text(ctx, "SNAP!", 540, 400, 180, "#ff3b3b", t, snap, rot=-0.1)


def sh_sharpener(ctx, t, d, g):
    setc(ctx, "#c98b55")
    ctx.paint()
    hx_hole, hy = 430, 1000
    rrect(ctx, hx_hole - 300, hy - 140, 320, 280, 30)
    fill_ol(ctx, "#3fa7d6", 9)
    rrect(ctx, hx_hole - 270, hy - 110, 120, 220, 20)
    setc(ctx, "#5fc0ea")
    ctx.fill()
    k = eio(clamp((t - 0.15) / 1.8))
    L = lerp(620, 0, k)
    shake_y = 4 * math.sin(t * 60) if 0.15 < t < 2.0 else 0
    if L > 30:
        ctx.save()
        ctx.rectangle(hx_hole, 0, W, H)
        ctx.clip()
        pencil(ctx, hx_hole - 70, hy + shake_y, 0.0, L=L + 70, phase=t * 6)
        ctx.restore()
        hand(ctx, hx_hole + L - 20, hy + shake_y, LEO, ang=0.15, r=60)
    else:
        hand(ctx, hx_hole + 60 + 40 * clamp((t - 2.0) / 0.3), hy, LEO, ang=0.15, r=60)
    ell(ctx, hx_hole, hy + shake_y, 22, 40)
    fill_ol(ctx, "#1d4f6b", 6)
    if 0.15 < t < 2.0:
        rnd = random.Random(int(t * 12))
        for _ in range(5):
            ph = rnd.uniform(0, 1)
            ctx.save()
            ctx.translate(hx_hole - 150 + rnd.uniform(-60, 60), hy - 160 - ph * 260)
            ctx.rotate(rnd.uniform(0, PI))
            ctx.new_path()
            ctx.arc(0, 0, 26, 0, 1.6 * PI)
            setc(ctx, "#f3d2a2")
            ctx.set_line_width(12)
            ctx.stroke()
            ctx.restore()
        for i in range(3):
            stroke_line(ctx, [(hx_hole - 330 - i * 30, hy - 60 + i * 60), (hx_hole - 400 - i * 30, hy - 60 + i * 60)],
                        8, (1, 1, 1, 0.8))
    pop_text(ctx, "GULP", 760, 600, 140, "#ffd23f", t, 2.05, rot=0.08)


def sh_crayon(ctx, t, d, g):
    room_bg(ctx, 1.0)
    cu(ctx, LEO, "nervous", t, hx=540 + 6 * math.sin(t * 30), hy=480, s=1.0, look=(0, 1))
    ctx.save()
    ctx.translate(0, 820)
    ctx.scale(1, 0.62)
    page_bg_part(ctx)
    ctx.restore()
    pts = scribble_pts(200, 1010, 680, rows=4, row_h=150, n=70, seed=9)
    tip = draw_partial(ctx, pts, t / d, "#ff4d8d", 16)
    ctx.save()
    ctx.translate(*tip)
    ctx.rotate(-0.9)
    rrect(ctx, 0, -26, 300, 52, 16)
    fill_ol(ctx, "#ff4d8d", 6)
    ctx.rectangle(70, -26, 150, 52)
    fill_ol(ctx, "#ffd23f", 5)
    poly(ctx, [(0, -26), (-50, 0), (0, 26)], close=True)
    fill_ol(ctx, "#ff4d8d", 6)
    ctx.restore()
    hand(ctx, tip[0] + math.cos(-0.9) * 200, tip[1] + math.sin(-0.9) * 200 + 30, LEO, ang=0.9)
    for i in range(4):
        stroke_line(ctx, [(60, 1150 + i * 140), (150, 1150 + i * 140)], 9, (1, 1, 1, 0.75))


def page_bg_part(ctx):
    rrect(ctx, 100, 0, 880, 1760, 16)
    fill_ol(ctx, "#fffdf6", 8)
    for k in range(1, 30):
        stroke_line(ctx, [(120, k * 60), (960, k * 60)], 3, "#b9d4f2")


def sh_leo_desperate(ctx, t, d, g):
    room_bg(ctx, 1.0)
    clock(ctx, 190, 260, 110, 11 * 60)
    leo_seated(ctx, t, "cry", look=(0, 0.6), pose=dict(lean=-4, la1=40, la2=95, ra1=-40, ra2=-95))
    desk(ctx, 1.0)
    rnd = random.Random(3)
    for i in range(9):
        x, y, r = rnd.uniform(380, 980), DESK_Y - rnd.uniform(10, 120), rnd.uniform(38, 55)
        ell(ctx, x, y, r, r * 0.9)
        fill_ol(ctx, "#ffffff", 5)
        for k in range(3):
            stroke_line(ctx, [(x - r * 0.5, y - r * 0.3 + k * 18), (x + r * 0.4, y - r * 0.1 + k * 12)], 3, "#c9c9c9")
    for i, (cx, cy, r) in enumerate(((440, 560, 90), (540, 520, 110), (650, 560, 90))):
        ell(ctx, cx, cy, r, r * 0.8)
        fill_ol(ctx, "#6b7a90", 6)
    for i in range(7):
        ph = (t * 2 + i / 7) % 1
        x = 420 + i * 40
        stroke_line(ctx, [(x, 620 + ph * 200), (x - 8, 650 + ph * 200)], 7, (0.55, 0.8, 1, 1 - ph))


def sh_grandpa_enter(ctx, t, d, g):
    radial_bg(ctx, "#ffd76a", "#e3a72f", cy=1000)
    mv.rays(ctx, W / 2, 1000, t, "#ffffff", 0.2)
    k = eback(clamp(t / 0.35))
    cu(ctx, GRANDPA, "smug", t, hy=lerp(1400, 1000, k), s=2.0, look=(0.3, 0.1),
       pose=dict(la1=-60, la2=40, ra1=60, ra2=-40))
    mv.sparkles(ctx, t, seed=8, n=5, col="#ffffff", area=(100, 400, 980, 900))


def sh_grandpa_writes(ctx, t, d, g):
    room_bg(ctx, 1.0)
    glow(ctx, 540, 1200, 700, "#fff3b0", 0.35)
    w = 10 * math.sin(t * 38)
    person(ctx, 900, 1860, 0.72, LEO, expr="shock", t=t, look=(-1, 0.3))
    person(ctx, 500, 1800, 0.95, GRANDPA, expr="smug" if t < 2.7 else "victory", t=t, look=(0.2, 0.9),
           pose=dict(ra1=-20 + w * 0.5, ra2=-80 + w, la1=30, la2=80))
    desk(ctx, 1.0)
    notebook(ctx, 520)
    for i, s in enumerate(SCRIBBLES):
        ph = (t * 0.55 + i / len(SCRIBBLES)) % 1
        x = 500 + (1 if i % 2 else -1) * (230 + 200 * ph) + 30 * math.sin(i * 2.3 + ph * 6)
        y = DESK_Y - 100 - ph * 1100
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(math.sin(i * 1.7) * 0.3)
        text(ctx, s, 0, 0, 64 + 20 * ph, (1, 1, 1, 1 - ph * 0.8), ol=10)
        ctx.restore()
    if t > 2.7:
        pop_text(ctx, "DONE!", 540, 380, 170, "#ffd23f", t, 2.7, rot=-0.08)


def sh_high_five(ctx, t, d, g):
    radial_bg(ctx, "#fff1a8", "#ffb000", cy=900)
    mv.rays(ctx, W / 2, 900, t, "#ffffff", 0.22)
    k = eout(clamp(t / 0.5))
    a1, a2 = lerp(60, 150, k), lerp(90, 170, k)
    person(ctx, 330, 1900, 1.0, LEO, expr="happy", t=t, look=(1, -0.4), pose=dict(ra1=a1, ra2=a2))
    person(ctx, 760, 1900, 1.0, GRANDPA, expr="victory", t=t, look=(-1, -0.4), pose=dict(la1=-a1, la2=-a2))
    if t >= 0.5:
        impact_star(ctx, 545, 915, 120 + 60 * clamp((t - 0.5) / 0.2), seed=2)
        mv.sparkles(ctx, t, seed=6, n=8, col="#ffffff", area=(150, 400, 930, 1300))


def sh_grandma_enter(ctx, t, d, g):
    room_bg(ctx, 1.0)
    person(ctx, 820, 1860, 0.8, LEO, expr="happy", t=t, look=(-1, 0))
    person(ctx, 560, 1800, 0.95, GRANDPA, expr="victory", t=t, look=(-1, 0),
           pose=dict(ra1=150, ra2=170))
    desk(ctx, 1.0)
    notebook(ctx, 560)
    p = clamp(t / 1.2)
    person(ctx, lerp(-260, 170, p), 1880, 0.85, GRANDMA, expr="suspicious", t=t, look=(1, 0),
           pose=walk_pose(t * 7, 16) if p < 1 else dict(la1=20, la2=80, ra1=-20, ra2=-80))


def homework_page(ctx, x, y, w, h, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rrect(ctx, -w / 2, -h / 2, w, h, 12)
    fill_ol(ctx, "#fffdf6", 8)
    for k in range(1, 9):
        stroke_line(ctx, [(-w / 2 + 20, -h / 2 + 90 + k * 52), (w / 2 - 20, -h / 2 + 90 + k * 52)], 3, "#b9d4f2")
    text(ctx, "HISTORY", 0, -h / 2 + 60, 74, "#e53935", ol=6)
    text(ctx, "Who built the pyramids?", -w / 2 + 30, -h / 2 + 130, 28, "#555555", align="l")
    for i, s in enumerate(("7x8=78", "2+2=5", "x=YES!")):
        ctx.save()
        ctx.translate(-w / 2 + 120 + i * 150, -h / 2 + 230 + i * 100)
        ctx.rotate(-0.1 + i * 0.08)
        text(ctx, s, 0, 0, 60, "#2b2f36")
        ctx.restore()
    ctx.restore()


def sh_grandma_read(ctx, t, d, g):
    radial_bg(ctx, "#e9d7f7", "#b78ad8", cy=800)
    gy = lerp(0.0, 0.28, eout(clamp((t - 0.25) / 0.4)))
    cu(ctx, GRANDMA, "neutral" if t < 0.6 else "suspicious", t, hy=760, s=1.6, glasses_y=gy, look=(0, 0.9))
    homework_page(ctx, 540, 1480, 760, 640, rot=-0.03)
    for sd in (-1, 1):
        ell(ctx, 540 + sd * 360, 1260, 50, 46)
        fill_ol(ctx, GRANDMA["skin"])
    if t > 0.6:
        k = clamp((t - 0.6) / 0.3)
        ctx.new_path()
        ctx.arc(540, 1200, 150, 0, 2 * PI)
        ell(ctx, 540, 1200, 170 + 20 * k, 70 + 10 * k)
        setc(ctx, "#ff3b3b", 0.9 * k)
        ctx.set_line_width(12)
        ctx.stroke()


def sh_both_shock(ctx, t, d, g):
    k = eout(clamp(t / 0.15))
    for side, P, base, dot in ((-1, LEO, "#3a6fd8", "#2f5fbf"), (1, GRANDPA, "#ff5a36", "#d93a1a")):
        ctx.save()
        if side < 0:
            poly(ctx, [(0, 0), (W * 0.62, 0), (W * 0.38, H), (0, H)], close=True)
        else:
            poly(ctx, [(W * 0.62, 0), (W, 0), (W, H), (W * 0.38, H)], close=True)
        ctx.clip()
        mv.halftone(ctx, base, dot, W / 2 + side * 300, 960)
        ctx.translate(side * (1 - k) * 600, 0)
        cu(ctx, P, "shock", t, hx=540 + side * 230, hy=960 + side * 120, s=1.5, look=(-side * 0.6, 0))
        ctx.restore()
    poly(ctx, [(W * 0.62 - 14, 0), (W * 0.62 + 14, 0), (W * 0.38 + 14, H), (W * 0.38 - 14, H)], close=True)
    setc(ctx, "#ffffff")
    ctx.fill()


def sh_grandpa_shrug(ctx, t, d, g):
    room_bg(ctx, 1.0)
    k = eout(clamp((t - 0.1) / 0.3))
    person(ctx, 400, 1880, 0.95, GRANDPA, expr="smug", t=t, look=(0.4, 0),
           pose=dict(la1=lerp(-8, -40, k), la2=lerp(-4, -95, k), ra1=lerp(8, 40, k), ra2=lerp(4, 95, k),
                     bob=10 * k * abs(math.sin(t * 4))))
    f = eout(clamp((t - 0.9) / 0.2))
    person(ctx, 850, 1880, 0.8, LEO, expr="nervous", t=t, look=(-0.5, 0.3),
           pose=dict(ra1=lerp(10, 150, f), ra2=lerp(10, -120, f)))
    question(ctx, 400, 560, t, 0.5)


def sh_final(ctx, t, d, g):
    slam(ctx, t, "HISTORY", "#9b6bff", 900, 400)


SHOT_FUNCS = {
    "hook_book": sh_hook_book, "leo_scream": sh_leo_scream, "setup_sit": sh_setup_sit,
    "clock_tick": sh_clock_tick, "phone_buzz": sh_phone_buzz, "phone_watch": sh_phone_watch,
    "night_shock": sh_night_shock, "cat_sit": sh_cat_sit, "cat_loop": sh_cat_loop, "cat_smug": sh_cat_smug,
    "pencil_snap": sh_pencil_snap, "sharpener": sh_sharpener, "crayon": sh_crayon,
    "leo_desperate": sh_leo_desperate, "grandpa_enter": sh_grandpa_enter, "grandpa_writes": sh_grandpa_writes,
    "high_five": sh_high_five, "grandma_enter": sh_grandma_enter, "grandma_read": sh_grandma_read,
    "both_shock": sh_both_shock, "grandpa_shrug": sh_grandpa_shrug, "final": sh_final,
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
