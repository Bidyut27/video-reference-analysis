"""Shot list and script for "Grandpa vs. the Smart Speaker" (Laughing Box, episode 5).

Each shot: (name, duration_seconds, [(local_time, sfx_name), ...]).
Coordinates are a 1080x1920 canvas; make_video.py renders it at SCALE (2 = 4K).
"Baby Duck Disco" is an invented song; no real music is named or played.
"""

W, H, FPS = 1080, 1920, 24

SHOTS = [
    # 0. Hook
    ("hook_shout", 2.6, [(0.0, "stamp")]),
    ("speaker_reply", 2.8, [(0.0, "chime_ok"), (1.6, "quack"), (2.0, "quack")]),
    ("grandpa_horror", 1.8, [(0.0, "zoom"), (0.05, "taiko")]),
    # 1. Setup
    ("leo_gift", 3.2, [(0.1, "pop"), (0.15, "sparkle")]),
    ("grandpa_doubt", 2.8, [(0.1, "squeak")]),
    # 2. Escalation A: weather -> feathers
    ("ask_weather", 2.4, [(0.0, "whoosh_s")]),
    ("speaker_order", 2.2, [(0.0, "chime_ok"), (1.5, "ding")]),
    ("delivery", 3.0, [(0.0, "door"), (0.7, "step"), (1.0, "stamp"), (1.6, "pop"), (1.65, "whoosh")]),
    ("feather_face", 2.4, [(0.1, "whoosh_s"), (1.4, "achoo")]),
    # 3. Escalation B: lights -> disco
    ("lights", 2.0, [(0.0, "whoosh_s")]),
    ("disco", 3.4, [(0.0, "chime_ok"), (0.3, "taiko"), (1.2, "sparkle"), (2.2, "sparkle")]),
    # 4. Escalation C: louder, then polite
    ("shout_slow", 3.6, [(0.1, "stamp"), (0.7, "stamp"), (1.3, "stamp"), (1.8, "chime_ok"), (2.9, "ringtone")]),
    ("polite", 3.8, [(0.1, "sparkle"), (1.7, "chime_ok"), (3.0, "ding")]),
    ("grandpa_furious", 1.8, [(0.0, "steam")]),
    # 5. New challenger
    ("grandma_enter", 2.4, [(0.1 + k * 0.4, "step") for k in range(4)]),
    ("grandma_whisper", 2.6, [(0.2, "whoosh_s")]),
    ("love_song", 3.2, [(0.0, "chime_ok"), (0.4, "sparkle"), (2.0, "sparkle")]),
    # 6. Twist 1
    ("grandpa_defeated", 2.4, [(0.1, "sadtrombone")]),
    # 7. Twist 2: the 3 a.m. alarm wakes Grandma, not Grandpa
    ("night", 3.6, [(0.0, "tick"), (0.6, "snore"), (2.2, "snore")]),
    ("alarm", 2.4, [(0.0, "alarm"), (0.05, "zoom")]),
    ("grandma_awake", 2.0, [(0.0, "taiko"), (0.6, "snore")]),
    # 8. Button: back to "Baby Duck Disco" (loops to the hook)
    ("final", 4.2, [(1.9, "chime_ok"), (3.2, "quack"), (3.6, "quack")]),
]


def shot_starts():
    out, acc = {}, 0.0
    for name, dur, _ in SHOTS:
        out[name] = acc
        acc += dur
    return out


TOTAL = sum(d for _, d, _ in SHOTS)

# (shot, local_start_seconds, speaker, line). "kiosk" is the series' machine voice.
LINES = [
    ("hook_shout", 0.2, "grandpa", "Hey box! Play my music!"),
    ("speaker_reply", 0.2, "kiosk", "Playing... Baby Duck Disco."),
    ("grandpa_horror", 0.2, "grandpa", "Baby WHAT?"),
    ("leo_gift", 0.4, "leo", "Just ask it anything, Grandpa!"),
    ("grandpa_doubt", 0.3, "grandpa", "I don't trust anything that small."),
    ("ask_weather", 0.3, "grandpa", "Box. What is the weather?"),
    ("speaker_order", 0.2, "kiosk", "Ordering forty feathers."),
    ("feather_face", 0.3, "grandpa", "Feathers?!"),
    ("lights", 0.2, "grandpa", "Turn on the lights!"),
    ("disco", 0.1, "kiosk", "Party mode!"),
    ("shout_slow", 0.1, "grandpa", "STOP. THE. MUSIC."),
    ("shout_slow", 1.9, "kiosk", "Calling Pickle Mart."),
    ("polite", 0.1, "grandpa", "Please, little box?"),
    ("polite", 1.7, "kiosk", "Alarm set for three a.m."),
    ("grandma_whisper", 0.4, "grandma", "Play our song, please."),
    ("love_song", 0.2, "kiosk", "Of course, Margaret."),
    ("grandpa_defeated", 0.4, "grandpa", "It likes you better."),
    ("grandma_awake", 0.2, "grandma", "HAROLD!"),
    ("final", 0.2, "grandpa", "Hey box... stop..."),
    ("final", 1.9, "kiosk", "Playing... Baby Duck Disco."),
]


# Same API as episode 1's timeline so its voice and audio helpers can be reused.
def shots(voice=False):
    return SHOTS


def starts(voice=False):
    return shot_starts()


def total(voice=False):
    return TOTAL
