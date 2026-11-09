"""Shot list shared by the picture and sound renderers.

Each shot: (name, duration_seconds, [(local_time, sfx_name), ...]).
Structure follows production/blueprint.md: hook -> setup -> escalation ->
breather -> new character -> face-off -> twist 1 -> twist 2 -> button/loop.
"""

import os

W, H, FPS = 1080, 1920, 24

_CLAPS = [(k * 0.25, "clap") for k in range(6)]

SHOTS = [
    # 0. Hook
    ("hook_eye", 2.5, [(0.15, "buzz"), (1.35, "buzz")]),
    # 1. Setup
    ("store_wide", 3.0, [(0.0, "door")] + [(0.45 + k * 0.42, "step") for k in range(5)]),
    ("teen_offer", 2.0, [(0.1, "pop"), (0.45, "sparkle")]),
    ("grandpa_no", 2.0, [(0.0, "whoosh"), (0.28, "stamp")]),
    ("grandpa_ready", 2.0, [(0.5, "pop")]),
    # 2. Escalation A (music enters on the first rejection)
    ("scan1", 1.8, [(0.6, "beep"), (0.75, "buzz")]),
    ("suspicious", 1.6, [(0.8, "squeak")]),
    ("scan2", 1.6, [(0.4, "whoosh"), (0.6, "impact"), (0.8, "buzz")]),
    ("teen_nervous", 1.5, [(0.3, "gulp")]),
    ("furious", 1.8, [(0.0, "steam")]),
    ("screen_x", 1.0, [(0.0, "zoom"), (0.05, "buzz")]),
    ("scan3", 1.6, [(0.15, "buzz"), (0.9, "buzz")]),
    # 3. Breather / world shot
    ("queue_track", 6.0, [(0.6 + k * 0.5, "tick") for k in range(10)] + [(3.2, "yawn")]),
    # 4. Escalation B: new character
    ("grandma_enter", 2.5, [(0.1 + k * 0.4, "step") for k in range(5)]),
    ("grandma_glasses", 2.0, [(0.25, "whoosh_s"), (0.9, "ding")]),
    ("split", 2.4, [(0.0, "whoosh"), (0.14, "whoosh"), (0.35, "taiko")]),
    ("rapid_a", 0.6, [(0.0, "taiko")]),
    ("rapid_b", 0.6, [(0.0, "taiko")]),
    ("rapid_c", 0.5, [(0.0, "taiko")]),
    ("rapid_d", 0.5, [(0.0, "taiko")]),
    ("chop", 1.8, [(0.3, "whoosh"), (0.55, "impact_big")]),
    # 5. Twist 1 (silence drop, then the win)
    ("glitch", 0.8, [(0.05, "glitch")]),
    ("ok", 1.4, [(0.0, "chime_ok"), (0.1, "sparkle")]),
    ("victory", 4.0, [(0.0, "fanfare"), (1.6, "sparkle"), (3.0, "sparkle")]),
    ("teen_clap", 1.5, _CLAPS),
    # 6. Twist 2
    ("shopper_pass", 3.0, [(0.0, "cart"), (1.35, "ding_wink")]),
    ("receipt", 3.0, [(0.0, "scratch"), (0.35, "printer"), (2.2, "dundun")]),
    ("gloom", 3.0, [(0.1, "sadtrombone")]),
    # 7. Button + loop back to the hook
    ("grandma_pays", 3.0, [(0.8, "tap"), (0.9, "chime_ok"), (1.0, "sparkle")] + [(1.0 + c[0], "clap") for c in _CLAPS]),
    ("final", 3.5, [(1.0, "buzz")]),
]


def shot_starts():
    out, acc = {}, 0.0
    for name, dur, _ in SHOTS:
        out[name] = acc
        acc += dur
    return out


TOTAL = sum(d for _, d, _ in SHOTS)


# ---------------------------------------------------------------- English voice version
# (shot, local_start_seconds, speaker, line). Speakers map to VOICES in make_voice.py.
LINES = [
    ("hook_eye", 0.3, "kiosk", "Unexpected item in the bagging area."),
    ("teen_offer", 0.2, "teen", "Need a hand, sir?"),
    ("grandpa_no", 0.3, "grandpa", "Help? I don't need help, kid!"),
    ("grandpa_ready", 0.3, "grandpa", "How hard can it be?"),
    ("scan1", 0.85, "kiosk", "Unexpected item."),
    ("suspicious", 0.2, "grandpa", "Unexpected? It's a melon!"),
    ("scan2", 0.85, "kiosk", "Please try again."),
    ("teen_nervous", 0.2, "teen", "Sir, I can really..."),
    ("furious", 0.2, "grandpa", "I've got this!"),
    ("scan3", 0.1, "kiosk", "Unexpected item. Unexpected item."),
    ("queue_track", 1.2, "woman", "Is it always this slow?"),
    ("queue_track", 3.6, "kid", "Mom, he's losing!"),
    ("grandma_enter", 1.0, "grandma", "Harold. What are you doing?"),
    ("grandma_glasses", 0.9, "grandma", "Let me see."),
    ("split", 0.6, "grandpa", "Stand back, Margaret. This is personal."),
    ("chop", 0.1, "grandpa", "Hi-YAH!"),
    ("ok", 0.15, "kiosk", "Payment approved."),
    ("victory", 1.9, "grandpa", "See? Easy!"),
    ("teen_clap", 0.3, "teen", "Wow. Okay."),
    ("shopper_pass", 1.0, "shopper", "Thanks for the groceries, grandpa!"),
    ("receipt", 0.9, "grandpa", "Groceries?"),
    ("gloom", 1.2, "grandpa", "My pension..."),
    ("grandma_pays", 0.15, "grandma", "Tap. Done."),
    ("grandma_pays", 1.3, "kiosk", "Thank you for shopping!"),
    ("final", 1.05, "kiosk", "Unexpected grandpa."),
]

# Shot lengths stretched in the voice version so every line fits.
VOICE_DURATIONS = {"grandpa_no": 2.3, "scan1": 2.3, "scan2": 2.1, "scan3": 2.8}


def shots(voice=False):
    if not voice:
        return SHOTS
    return [(n, VOICE_DURATIONS.get(n, d), c) for n, d, c in SHOTS]


def starts(voice=False):
    out, acc = {}, 0.0
    for name, dur, _ in shots(voice):
        out[name] = acc
        acc += dur
    return out


def total(voice=False):
    return sum(d for _, d, _ in shots(voice))


if os.environ.get("VOICE") == "1":
    SHOTS = shots(True)
    TOTAL = total(True)
