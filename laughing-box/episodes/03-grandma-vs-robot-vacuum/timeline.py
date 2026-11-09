"""Shot list and script for "Grandma vs. the Robot Vacuum" (Laughing Box, episode 3).

Each shot: (name, duration_seconds, [(local_time, sfx_name), ...]).
Coordinates are a 1080x1920 canvas; make_video.py renders it at SCALE (2 = 4K).
"""

W, H, FPS = 1080, 1920, 24

SHOTS = [
    # 0. Hook: something zooms under the chair
    ("hook_zoom", 2.4, [(0.0, "motor"), (0.3, "whoosh"), (1.5, "bonk"), (1.9, "squeak")]),
    ("grandma_eyes", 2.6, [(0.0, "zoom"), (0.05, "taiko")]),
    # 1. Setup
    ("leo_explain", 3.4, [(0.2, "motor"), (1.2, "pop")]),
    ("grandma_squint", 2.6, [(0.1, "squeak")]),
    # 2. Escalation A: it's a lost pet
    ("bump", 3.2, [(0.2, "motor")] + [(0.35 + k * 0.5, "bonk") for k in range(3)] + [(1.9, "sparkle")]),
    ("milk", 3.4, [(0.4, "step"), (1.5, "motor"), (2.0, "slurp"), (2.9, "hiccup")]),
    # 3. Escalation B: she adopts it
    ("bow", 2.8, [(0.6, "pop"), (0.65, "sparkle"), (1.1, "ding")]),
    ("grandma_love", 2.4, [(0.1, "sparkle")]),
    ("leo_facepalm", 2.2, [(0.15, "slap")]),
    # 4. Escalation C: the yarn
    ("yarn_grab", 2.8, [(0.2, "motor"), (0.9, "slurp"), (1.2, "whoosh")]),
    ("chase_a", 2.6, [(0.0, "motor")] + [(0.2 + k * 0.3, "step") for k in range(7)]),
    ("chase_b", 2.6, [(0.0, "motor"), (0.4, "whoosh"), (1.2, "whoosh"), (2.0, "boing")]),
    # 5. New challenger
    ("grandpa_enter", 2.6, [(0.0, "stamp")]),
    ("grandpa_step", 2.0, [(0.1, "motor"), (1.0, "stamp"), (1.15, "squeak")]),
    ("grandpa_ride", 3.2, [(0.0, "motor"), (0.0, "whoosh"), (1.0, "whoosh"), (2.0, "whoosh")]),
    ("crash", 2.0, [(0.0, "impact_big"), (0.5, "sparkle")]),
    # 6. Twist 1: Biscuit wins
    ("grandma_proud", 2.6, [(0.1, "fanfare")]),
    # 7. Twist 2: a second robot
    ("next_day", 3.6, [(0.0, "tick"), (0.8, "pop"), (1.0, "chime_ok")]),
    ("grandpa_shock", 1.8, [(0.0, "scratch"), (0.3, "zoom"), (0.35, "taiko")]),
    ("double_chase", 3.6, [(0.0, "motor"), (1.2, "motor")] + [(0.1 + k * 0.25, "step") for k in range(13)]),
    # 8. Button: both zoom under the chair (loops to the hook)
    ("final", 3.6, [(0.0, "motor"), (2.1, "whoosh"), (2.6, "bonk"), (3.0, "squeak")]),
]


def shot_starts():
    out, acc = {}, 0.0
    for name, dur, _ in SHOTS:
        out[name] = acc
        acc += dur
    return out


TOTAL = sum(d for _, d, _ in SHOTS)

# (shot, local_start_seconds, speaker, line). Speakers map to VOICES in make_voice.py.
LINES = [
    ("grandma_eyes", 0.3, "grandma", "Something is living under my chair!"),
    ("leo_explain", 0.3, "leo", "Relax, Grandma! It's a robot. It cleans by itself!"),
    ("grandma_squint", 0.3, "grandma", "By itself? Nothing cleans by itself."),
    ("bump", 1.0, "grandma", "Aww. Are you lost, little one?"),
    ("milk", 0.2, "grandma", "Here you go. Drink your milk."),
    ("bow", 1.0, "grandma", "I'll call you Biscuit."),
    ("grandma_love", 0.3, "grandma", "Who's a good Biscuit?"),
    ("leo_facepalm", 0.3, "leo", "Grandma, it's a machine!"),
    ("yarn_grab", 1.2, "grandma", "Biscuit! My knitting!"),
    ("chase_a", 0.4, "grandma", "Come back here!"),
    ("chase_b", 0.5, "leo", "Whoa, whoa, whoa!"),
    ("grandpa_enter", 0.3, "grandpa", "Stand back. I'll handle this."),
    ("grandpa_ride", 0.5, "grandpa", "Whoa! Whoa! WHOA!"),
    ("grandma_proud", 0.6, "grandma", "Good boy, Biscuit."),
    ("next_day", 1.0, "grandma", "Biscuit was lonely. Meet Cookie!"),
    ("grandpa_shock", 0.4, "grandpa", "Two of them?!"),
    ("double_chase", 1.0, "leo", "Run, Grandpa, run!"),
    ("final", 0.4, "grandpa", "This is MY chair!"),
]


# Same API as episode 1's timeline so its voice and audio helpers can be reused.
def shots(voice=False):
    return SHOTS


def starts(voice=False):
    return shot_starts()


def total(voice=False):
    return TOTAL
