#!/usr/bin/env python3
"""Generate the English dialogue with Kokoro TTS, reusing the series' voice settings.

  python make_voice.py MODEL_DIR voice_track.wav voice_track.json
"""
import ep1

v = ep1.voice()
# Leo, the grandson (same voice as episodes 2-3)
v.VOICES["leo"] = ("am_puck", 1.1, 2.5)

if __name__ == "__main__":
    v.main()
