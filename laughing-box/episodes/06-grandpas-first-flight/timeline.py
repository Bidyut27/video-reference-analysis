"""Shot list and script for "Grandpa's First Flight" (Laughing Box, episode 6).

Each shot: (name, duration_seconds, [(local_time, sfx_name), ...]).
Coordinates are a 1080x1920 canvas; make_video.py renders it at SCALE (2 = 4K).
"""

W, H, FPS = 1080, 1920, 24

SHOTS = [
    # 0. Hook: the call button, for the 40th time
    ("hook_button", 2.6, [(0.15, "bing"), (0.55, "bing"), (0.95, "bing"), (1.35, "bing")]),
    ("attendant_sigh", 2.4, [(0.1, "squeak")]),
    # 1. Setup
    ("cabin_wide", 3.2, [(0.2, "gulp")]),
    ("leo_relax", 2.4, [(0.1, "sparkle")]),
    # 2. Escalation A: the seat belt
    ("belt_pull", 3.0, [(0.2, "whoosh_s"), (0.8, "whoosh_s"), (1.4, "whoosh_s"), (2.2, "click")]),
    ("belt_wrong", 2.4, [(0.1, "squeak")]),
    # 3. Escalation B: the life vest
    ("vest_demo", 3.0, [(0.1, "pop"), (1.6, "ding")]),
    ("vest_pull", 1.6, [(0.9, "click")]),
    ("vest_poof", 2.8, [(0.0, "inflate"), (0.45, "impact"), (0.5, "pop")]),
    # 4. Escalation C: takeoff
    ("takeoff_window", 2.6, [(0.0, "engine")]),
    ("takeoff_face", 2.6, [(0.0, "whoosh")]),
    # breather / world shot
    ("plane_exterior", 3.0, [(0.0, "whoosh"), (1.5, "whoosh_s")]),
    # 5. The call button, x38, x39, x40
    ("call_a", 1.8, [(0.1, "bing")]),
    ("call_b", 1.8, [(0.1, "bing")]),
    ("call_c", 1.8, [(0.1, "bing")]),
    ("attendant_twitch", 2.4, [(0.0, "steam")]),
    ("grandma_sleep", 2.8, [(1.6, "whoosh_s"), (2.0, "snore")]),
    # 6. Twist 1: he loves it
    ("sunset", 3.4, [(0.0, "sparkle"), (1.6, "sparkle")]),
    # 7. Twist 2: landed already, and he's stuck
    ("pilot_pa", 2.8, [(0.0, "door")]),
    ("grandpa_no", 2.2, [(0.0, "zoom"), (0.05, "taiko")]),
    ("stuck", 3.4, [(0.2, "squeak"), (0.8, "squeak"), (1.4, "squeak"), (2.4, "cork"), (2.45, "whoosh")]),
    # 8. Button: back to the call button (loops to the hook)
    ("final", 4.0, [(0.15, "bing"), (2.2, "sparkle")]),
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
    ("attendant_sigh", 0.3, "rosa", "Yes, sir... again?"),
    ("cabin_wide", 0.3, "grandpa", "Metal can't fly. It's science!"),
    ("leo_relax", 0.2, "leo", "Relax, Grandpa. It's safe!"),
    ("belt_pull", 0.3, "grandpa", "This belt is too short!"),
    ("belt_wrong", 0.3, "grandma", "Harold. That's MY belt."),
    ("vest_demo", 0.2, "rosa", "Never pull this tab inside the plane."),
    ("vest_pull", 0.1, "grandpa", "This tab?"),
    ("vest_poof", 1.0, "leo", "Grandpa, you're a balloon!"),
    ("takeoff_face", 0.2, "grandpa", "Whoooaaa!"),
    ("call_a", 0.4, "grandpa", "Water, please!"),
    ("call_b", 0.4, "grandpa", "Are we falling?"),
    ("call_c", 0.25, "grandpa", "Is that cloud normal?"),
    ("attendant_twitch", 0.45, "rosa", "That's forty times, sir."),
    ("grandma_sleep", 0.2, "grandma", "Wake me when we land."),
    ("sunset", 1.0, "grandpa", "Flying is... wonderful!"),
    ("pilot_pa", 0.6, "pilot", "We have landed. Welcome home!"),
    ("grandpa_no", 0.2, "grandpa", "No! One more time!"),
    ("stuck", 0.3, "rosa", "Sir, please let go!"),
    ("final", 0.3, "rosa", "Yes, sir?"),
    ("final", 1.6, "grandpa", "When is the next flight?"),
]


# Same API as episode 1's timeline so its voice and audio helpers can be reused.
def shots(voice=False):
    return SHOTS


def starts(voice=False):
    return shot_starts()


def total(voice=False):
    return TOTAL
