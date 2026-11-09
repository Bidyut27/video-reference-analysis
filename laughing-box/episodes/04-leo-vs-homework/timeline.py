"""Shot list and script for "Leo vs. Homework" (Laughing Box, episode 4).

Each shot: (name, duration_seconds, [(local_time, sfx_name), ...]).
Coordinates are a 1080x1920 canvas; make_video.py renders it at SCALE (2 = 4K).
"""

W, H, FPS = 1080, 1920, 24

SHOTS = [
    # 0. Hook: the math book lands
    ("hook_book", 2.4, [(0.0, "whoosh"), (0.4, "impact_big"), (0.45, "stamp")]),
    ("leo_scream", 2.0, [(0.0, "zoom"), (0.05, "taiko")]),
    # 1. Setup
    ("setup_sit", 3.2, [(0.2, "pop"), (1.6, "crack"), (2.0, "crack")]),
    ("clock_tick", 1.6, [(0.1, "tick"), (0.6, "tick"), (1.1, "tick")]),
    # 2. Escalation A: the phone
    ("phone_buzz", 2.4, [(0.1, "vibrate"), (0.9, "vibrate"), (1.6, "ding")]),
    ("phone_watch", 3.4, [(0.0, "whoosh")] + [(0.3 + k * 0.15, "tick") for k in range(19)]),
    ("night_shock", 2.2, [(0.0, "zoom"), (0.05, "taiko")]),
    # 3. Escalation B: the cat
    ("cat_sit", 2.6, [(0.0, "meow"), (0.3, "whoosh"), (0.7, "pop")]),
    ("cat_loop", 3.4, [(0.1, "whoosh"), (0.75, "pop"), (1.2, "whoosh"), (1.85, "pop"), (2.3, "whoosh"),
                       (2.95, "pop")]),
    ("cat_smug", 1.6, [(0.1, "purr")]),
    # 4. Escalation C: the pencil
    ("pencil_snap", 2.0, [(0.0, "scribble"), (0.7, "snap")]),
    ("sharpener", 2.6, [(0.15, "grind"), (2.05, "gulp")]),
    ("crayon", 2.4, [(0.0, "scribble"), (0.8, "scribble"), (1.6, "scribble")]),
    ("leo_desperate", 2.4, [(0.1, "sadtrombone")]),
    # 5. New challenger
    ("grandpa_enter", 3.0, [(0.0, "stamp"), (0.2, "sparkle")]),
    ("grandpa_writes", 3.6, [(0.0, "scribble"), (0.9, "scribble"), (1.8, "scribble"), (2.7, "ding"),
                             (2.75, "sparkle")]),
    # 6. Twist 1: done!
    ("high_five", 2.6, [(0.5, "slap"), (0.55, "fanfare")]),
    # 7. Twist 2: wrong subject
    ("grandma_enter", 2.0, [(0.1 + k * 0.4, "step") for k in range(4)]),
    ("grandma_read", 3.4, [(0.25, "whoosh_s"), (0.6, "scratch")]),
    ("both_shock", 1.8, [(0.0, "whoosh"), (0.15, "taiko")]),
    ("grandpa_shrug", 2.6, [(0.2, "squeak")]),
    # 8. Button: an even bigger book lands (loops to the hook)
    ("final", 3.4, [(0.0, "whoosh"), (0.4, "impact_big"), (0.45, "stamp")]),
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
    ("leo_scream", 0.2, "leo", "Not the math book!"),
    ("setup_sit", 0.4, "leo", "Just one page. Easy."),
    ("phone_buzz", 0.9, "leo", "Just one video..."),
    ("night_shock", 0.3, "leo", "Wait... it's dark?!"),
    ("cat_sit", 1.0, "leo", "Mittens, move!"),
    ("cat_loop", 2.5, "leo", "Seriously?!"),
    ("pencil_snap", 0.9, "leo", "No, no, no!"),
    ("crayon", 0.3, "leo", "Crayon. Fine. FINE."),
    ("leo_desperate", 0.3, "leo", "I'll never finish!"),
    ("grandpa_enter", 0.3, "grandpa", "Let me help. I was great at math!"),
    ("grandpa_writes", 0.4, "grandpa", "Carry the seven... and done!"),
    ("high_five", 0.8, "leo", "Thanks, Grandpa!"),
    ("grandma_enter", 0.4, "grandma", "What are you two doing?"),
    ("grandma_read", 0.9, "grandma", "Harold... this is the history homework."),
    ("grandpa_shrug", 0.3, "grandpa", "History is just old math."),
    ("final", 1.0, "leo", "NOOO!"),
]


# Same API as episode 1's timeline so its voice and audio helpers can be reused.
def shots(voice=False):
    return SHOTS


def starts(voice=False):
    return shot_starts()


def total(voice=False):
    return TOTAL
