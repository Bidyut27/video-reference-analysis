#!/usr/bin/env python3
"""Render the Laughing Box character images from the same code the episodes use.

  python laughing-box/characters/make_characters.py [OUT_DIR]

Writes (default OUT_DIR = this folder):
  <name>.png                     one transparent PNG per character (2x resolution)
  cast-poster-3840x2160.png      the whole cast on a brand background (4K, 16:9)
  expressions-<name>.png         expression sheets for Grandpa, Grandma, Leo and Mittens
"""
import importlib.util
import math
import os
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
EP5 = os.path.join(HERE, "..", "episodes", "05-grandpa-vs-smart-speaker")

# episode 5's loader pulls in every earlier episode, so all characters and props are available
_spec = importlib.util.spec_from_file_location("ep1", os.path.join(EP5, "ep1.py"))
ep1 = importlib.util.module_from_spec(_spec)
sys.modules["ep1"] = ep1
_spec.loader.exec_module(ep1)
mv = ep1.video()
e2 = ep1.ep2_video()
e3 = ep1.ep3_video()
e4 = ep1.ep4_video()
e5 = ep1.load(os.path.join(EP5, "make_video.py"), "ep5_video")
mb = ep1.load(os.path.join(ep1.BRANDING, "make_branding.py"), "make_branding")
mv.TRACK = []  # no dialogue: mouths and speaker stay in their resting pose
mv.CUR_T = 0.0

S2 = 2  # render scale for the individual PNGs


def person_fn(P, expr="happy", pose=None, look=(0, 0.1)):
    def f(ctx, x, y, s):
        mv.person(ctx, x, y, s, P, expr=expr, t=0.0, look=look, pose=pose or {}, blink=False)
    return f


def cat_fn(expr="smug"):
    def f(ctx, x, y, s):
        e4.cat(ctx, x, y, s * 2.2, expr, 0.0, look=(-0.4, 0))
    return f


def vacuum_fn(bow):
    def f(ctx, x, y, s):
        e3.vacuum(ctx, x, y, s * 2.4, 0.0, face=1, bow_col=bow, heart_led=True)
    return f


def speaker_fn(ctx, x, y, s):
    # resting state: the party glow would be clipped by the canvas edge
    e5.speaker(ctx, x, y, s * 2.6, 0.0, "idle")


def kiosk_fn(ctx, x, y, s):
    mv.kiosk(ctx, x, y, s * 0.95, "x")


# (file name, display name, role, draw fn, canvas w, canvas h, scale, foot y fraction)
CAST = [
    ("grandpa-harold", "GRANDPA", "Harold · proud, stubborn, never gives up", person_fn(mv.GRANDPA, "victory",
                                                                                       dict(ra1=150, ra2=170)),
     900, 1300, 1.0, 0.95),
    ("grandma-margaret", "GRANDMA", "Margaret · calm, smug, secretly a tech pro", person_fn(mv.GRANDMA, "smug"),
     900, 1300, 1.0, 0.95),
    ("leo", "LEO", "The grandson · cheerful, facepalms a lot", person_fn(e2.LEO, "happy", dict(ra1=60, ra2=85)),
     900, 1300, 1.0, 0.95),
    ("mittens", "MITTENS", "Leo's cat · sits on homework", cat_fn("smug"), 900, 1100, 1.0, 0.92),
    ("biscuit", "BISCUIT", "Grandma's robot vacuum (pink bow)", vacuum_fn(e3.PINK), 900, 700, 1.0, 0.85),
    ("cookie", "COOKIE", "Biscuit's sibling (blue bow)", vacuum_fn(e3.BLUE), 900, 700, 1.0, 0.85),
    ("smart-speaker", "THE SPEAKER", "Mishears everything", speaker_fn, 800, 900, 1.0, 0.88),
    ("teen-staffer", "TEEN STAFFER", "Pickle Mart helper", person_fn(mv.TEEN, "nervous"), 900, 1300, 1.0, 0.95),
    ("big-shopper", "BIG SHOPPER", "Pickle Mart regular", person_fn(mv.SHOPPER, "wink", dict(thumb=True, ra1=120,
                                                                                            ra2=175)),
     1000, 1300, 1.0, 0.95),
    ("queue-woman", "QUEUE WOMAN", "Pickle Mart customer", person_fn(mv.Q_WOMAN, "suspicious"), 900, 1300, 1.0, 0.95),
    ("queue-grandad", "SLEEPY GRANDAD", "Pickle Mart customer", person_fn(mv.Q_OLDMAN, "yawn",
                                                                          dict(la1=-160, la2=-170, ra1=160, ra2=170)),
     900, 1300, 1.0, 0.95),
    ("queue-kid", "BALLOON KID", "Pickle Mart customer", person_fn(mv.Q_KID, "happy", dict(ra1=150, ra2=175)),
     900, 1700, 0.85, 0.96),
    ("self-checkout", "SELF-CHECKOUT", "Grandpa's first enemy", kiosk_fn, 800, 1300, 1.0, 0.95),
]


def render_single(out, key, fn, w, h, s, foot):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w * S2, h * S2)
    ctx = cairo.Context(surf)
    ctx.scale(S2, S2)
    if key == "queue-kid":
        mv.person(ctx, w / 2, h * foot, s, mv.Q_KID, expr="happy", t=0.0, look=(0, 0.1), blink=False,
                  pose=dict(ra1=150, ra2=175), hold={1: "balloon"})
    else:
        fn(ctx, w / 2, h * foot, s)
    surf.write_to_png(os.path.join(out, f"{key}.png"))


def name_tag(ctx, x, y, name, role, size=56):
    mb.pill(ctx, name, x, y, size)
    mv.text(ctx, role, x, y + size * 1.55, size * 0.5, "#2b2f36")


def cast_poster(out):
    W, H = 3840, 2160
    surf, ctx = mb.surface(W, H)
    mb.sunburst(ctx, W, H, W / 2, H * 0.45)
    mb.dots(ctx, W, H, a=0.1)
    mb.confetti(ctx, W, H, seed=21, n=90, avoid=[(0, 300, W, H)])
    mb.mascot(ctx, 560, 300, 0.42)
    mb.wordmark(ctx, 1500, 210, 170, "LAUGHING BOX")
    mb.pill(ctx, "MEET THE CAST", 1500, 370, 54)
    floor = 1660
    mb.ground(ctx, W, H, floor + 40)
    row = [
        (mv.GRANDPA, "GRANDPA", "Harold", "victory", dict(ra1=150, ra2=170), 620),
        (mv.GRANDMA, "GRANDMA", "Margaret", "smug", None, 1260),
        (e2.LEO, "LEO", "The grandson", "happy", dict(ra1=60, ra2=85), 1880),
    ]
    for P, name, role, expr, pose, x in row:
        mb.shadow(ctx, x, floor + 14, 170)
        mv.person(ctx, x, floor, 1.0, P, expr=expr, t=0.0, look=(0, 0.1), pose=pose or {}, blink=False)
        name_tag(ctx, x, floor + 170, name, role)
    e4.cat(ctx, 2480, floor, 1.25, "smug", 0.0, look=(-0.6, 0))
    name_tag(ctx, 2480, floor + 170, "MITTENS", "Leo's cat")
    for x, bow in ((2950, e3.PINK), (3330, e3.BLUE)):
        e3.vacuum(ctx, x, floor, 1.15, 0.0, bow_col=bow, heart_led=True, face=-1 if x < 3100 else 1)
    name_tag(ctx, 2950, floor + 170, "BISCUIT", "Robot vacuum")
    name_tag(ctx, 3330, floor + 170, "COOKIE", "Robot vacuum")
    mv.text(ctx, "+ the Smart Speaker", 3150, 1180, 54, "#ffffff", ol=10)
    e5.speaker(ctx, 3150, 1100, 1.2, 0.0, "party")
    surf.write_to_png(os.path.join(out, "cast-poster-3840x2160.png"))


EXPRS = ["happy", "wink", "smug", "suspicious", "furious", "shock", "nervous", "cry"]


def expression_sheet(out, key, title, P):
    cols, cell = 4, 520
    W, H = cols * cell, 2 * cell + 240
    surf, ctx = mb.surface(W, H)
    mb.sunburst(ctx, W, H, W / 2, H / 2, c1="#fff6d6", c2="#ffc66b")
    mv.text(ctx, title, W / 2, 110, 92, "#ffd23f", ol=18)
    for i, ex in enumerate(EXPRS):
        cx, cy = (i % cols) * cell + cell / 2, 240 + (i // cols) * cell + cell / 2 - 30
        mv.rrect(ctx, cx - cell / 2 + 20, cy - cell / 2 + 50, cell - 40, cell - 40, 40)
        mv.setc(ctx, "#ffffff", 0.55)
        ctx.fill()
        mv.face(ctx, cx, cy + 10, 150, ex, P, 0.0, (0, 0.1), None, False)
        mv.text(ctx, ex.upper(), cx, cy + cell / 2 - 10, 40, "#2b2f36")
    surf.write_to_png(os.path.join(out, f"expressions-{key}.png"))


def mittens_sheet(out):
    W, H = 1560, 760
    surf, ctx = mb.surface(W, H)
    mb.sunburst(ctx, W, H, W / 2, H / 2, c1="#fff6d6", c2="#ffc66b")
    mv.text(ctx, "MITTENS", W / 2, 90, 92, "#ffd23f", ol=18)
    for i, ex in enumerate(("neutral", "smug", "happy")):
        cx = 260 + i * 520
        e4.cat(ctx, cx, 640, 1.15, ex, 0.0, look=(-0.4, 0))
        mv.text(ctx, ex.upper(), cx, 700, 40, "#2b2f36")
    surf.write_to_png(os.path.join(out, "expressions-mittens.png"))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else HERE
    os.makedirs(out, exist_ok=True)
    for key, _name, _role, fn, w, h, s, foot in CAST:
        render_single(out, key, fn, w, h, s, foot)
    cast_poster(out)
    expression_sheet(out, "grandpa", "GRANDPA", mv.GRANDPA)
    expression_sheet(out, "grandma", "GRANDMA", mv.GRANDMA)
    expression_sheet(out, "leo", "LEO", e2.LEO)
    mittens_sheet(out)
    print("written to", out)


if __name__ == "__main__":
    main()
