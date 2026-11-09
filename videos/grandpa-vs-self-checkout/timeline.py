"""Shot list shared by the picture and sound renderers.

Each shot: (name, duration_seconds, [(local_time, sfx_name), ...]).
Structure follows production/blueprint.md: hook -> setup -> escalation ->
breather -> new character -> face-off -> twist 1 -> twist 2 -> button/loop.
"""

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
