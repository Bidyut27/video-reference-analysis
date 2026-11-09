"""Shot list and script for "Grandpa vs. the Video Call" (Laughing Box, episode 2).

Each shot: (name, duration_seconds, [(local_time, sfx_name), ...]).
Structure follows production/blueprint.md: hook -> setup -> 3 escalations ->
new character -> twist 1 -> twist 2 -> button that loops back to the hook.
"""

W, H, FPS = 1080, 1920, 24

_RUB = [(0.2 + k * 0.22, "rub") for k in range(10)]

SHOTS = [
    # 0. Hook: what Leo sees
    ("hook_nose", 2.8, [(0.0, "zoom"), (0.05, "boing")]),
    # 1. Setup
    ("living_wide", 3.0, [(0.0, "snore"), (0.4, "ringtone"), (0.4, "vibrate"), (1.6, "vibrate")]),
    ("grandpa_wake", 2.2, [(0.0, "stamp"), (0.5, "pop")]),
    ("answer", 1.6, [(0.55, "tap"), (0.6, "pop"), (0.65, "sparkle")]),
    # 2. Escalation A: the nose
    ("too_close", 2.6, [(0.0, "whoosh")]),
    ("view_nose", 2.8, [(0.0, "boing")]),
    # 3. Escalation B: the forehead
    ("grandpa_raise", 1.8, [(0.05, "whoosh"), (0.6, "squeak")]),
    ("view_forehead", 2.8, [(0.35, "ding")]),
    ("grandpa_suspicious", 2.6, [(0.1, "squeak")]),
    # 4. Escalation C: the cat filter
    ("poke", 1.6, [(0.15, "tap"), (0.4, "tap"), (0.65, "tap"), (0.9, "tap"), (1.0, "sparkle")]),
    ("view_cat", 3.0, [(0.0, "pop"), (0.3, "meow")]),
    ("grandpa_wipe", 2.8, [(0.0, "steam")] + _RUB),
    ("view_cat2", 1.5, [(0.1, "meow")]),
    # 5. Breather gag: phone to the ear
    ("ear_call", 3.2, [(0.0, "whoosh")]),
    ("leo_facepalm", 2.2, [(0.15, "slap")]),
    # 6. New character + twist 1
    ("grandma_enter", 2.6, [(0.1 + k * 0.4, "step") for k in range(5)]),
    ("grandma_tap", 1.4, [(0.5, "tap"), (0.55, "chime_ok"), (0.6, "sparkle")]),
    ("view_grandma", 3.2, [(0.0, "sparkle")]),
    ("grandma_smug", 1.8, [(1.25, "tap"), (1.3, "pop")]),
    ("grandpa_grumpy", 2.0, [(0.0, "steam")]),
    # 7. Twist 2
    ("view_grandma_cat", 3.0, [(0.0, "scratch"), (0.25, "pop"), (0.45, "meow")]),
    ("grandma_shock", 1.4, [(0.0, "zoom"), (0.05, "taiko")]),
    ("grandpa_laugh", 2.4, [(0.1, "sparkle"), (1.2, "meow")]),
    # 8. Button: back to the nose (loops to the hook)
    ("final_nose", 3.4, [(1.0, "zoom"), (1.05, "boing")]),
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
    ("hook_nose", 0.35, "leo", "Grandpa... is that your nose?"),
    ("grandpa_wake", 0.55, "grandpa", "Ooh! It's Leo!"),
    ("too_close", 0.3, "grandpa", "Hello? HELLO?"),
    ("view_nose", 0.3, "leo", "I can only see your nose!"),
    ("view_forehead", 0.4, "leo", "Now it's just your forehead!"),
    ("grandpa_suspicious", 0.2, "grandpa", "Where is the camera on this thing?"),
    ("view_cat", 0.75, "leo", "Grandpa, you're a cat!"),
    ("grandpa_wipe", 0.3, "grandpa", "Shoo! Get off my face!"),
    ("ear_call", 0.3, "grandpa", "Hello?! Can you hear me?"),
    ("leo_facepalm", 0.3, "leo", "I'm right here, Grandpa!"),
    ("grandma_enter", 1.0, "grandma", "Harold. Give me that."),
    ("view_grandma", 0.3, "leo", "Hi, Grandma!"),
    ("view_grandma", 1.4, "grandma", "Hello, sweetheart!"),
    ("grandma_smug", 0.2, "grandma", "See? Easy."),
    ("grandpa_grumpy", 0.3, "grandpa", "Beginner's luck."),
    ("view_grandma_cat", 0.9, "leo", "Grandma... you're a cat too!"),
    ("grandpa_laugh", 0.3, "grandpa", "Meow, Margaret!"),
    ("final_nose", 0.2, "grandpa", "Bye, Leo!"),
    ("final_nose", 1.6, "leo", "The nose is back."),
]


# Same API as episode 1's timeline so its voice and audio helpers can be reused.
def shots(voice=False):
    return SHOTS


def starts(voice=False):
    return shot_starts()


def total(voice=False):
    return TOTAL
