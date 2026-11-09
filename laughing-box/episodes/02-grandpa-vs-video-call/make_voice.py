#!/usr/bin/env python3
"""Generate the English dialogue with Kokoro TTS, reusing episode 1's voice settings.

  python make_voice.py MODEL_DIR voice_track.wav voice_track.json
"""
import ep1

v = ep1.voice()
# Leo, the grandson: young, bright voice
v.VOICES["leo"] = ("am_puck", 1.1, 2.5)

if __name__ == "__main__":
    v.main()
