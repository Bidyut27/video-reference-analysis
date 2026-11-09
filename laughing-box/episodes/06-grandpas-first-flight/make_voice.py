#!/usr/bin/env python3
"""Generate the English dialogue with Kokoro TTS, reusing the series' voice settings.

Adds Rosa (flight attendant) and the pilot, whose lines go through a cabin-PA filter.

  python make_voice.py MODEL_DIR voice_track.wav voice_track.json
"""
import numpy as np
from scipy.signal import butter, sosfilt

import ep1

v = ep1.voice()
v.VOICES["leo"] = ("am_puck", 1.1, 2.5)       # same as episodes 2-5
v.VOICES["rosa"] = ("af_sarah", 1.05, 0.0)    # flight attendant
v.VOICES["pilot"] = ("am_michael", 0.95, -1.0)

_synth = v.synth


def synth(kokoro, speaker, text):
    y = _synth(kokoro, speaker, text)
    if speaker == "pilot":
        # small cabin speaker: band-limited with a touch of grit
        y = sosfilt(butter(4, [350, 3400], "band", fs=v.SR, output="sos"), y)
        y = np.tanh(y * 2.5)
        y = y / (np.max(np.abs(y)) + 1e-9) * 0.9
    return y


v.synth = synth

if __name__ == "__main__":
    v.main()
