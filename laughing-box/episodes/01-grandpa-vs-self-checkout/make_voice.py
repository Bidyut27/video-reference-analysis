#!/usr/bin/env python3
"""Generate the English dialogue with Kokoro TTS (offline, Apache-2.0 model).

  python make_voice.py MODEL_DIR voice_track.wav voice_track.json

MODEL_DIR must contain kokoro-v1.0.onnx and voices-v1.0.bin from
https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
The JSON holds caption spans and per-frame mouth envelopes for make_video.py --voice.
"""
import json
import os
import sys
import wave

import librosa
import numpy as np
from kokoro_onnx import Kokoro
from scipy.signal import butter, sosfilt

from timeline import FPS, LINES, shots, starts, total

SR = 44100
# speaker: (kokoro voice, speed, semitone shift)
VOICES = {
    "grandpa": ("bm_george", 0.95, -1.5),
    "grandma": ("bf_emma", 0.95, 0.0),
    "teen": ("am_puck", 1.1, 1.0),
    "shopper": ("am_fenrir", 1.05, 0.0),
    "woman": ("af_bella", 1.05, 0.0),
    "kid": ("af_sky", 1.15, 3.0),
    "kiosk": ("af_nicole", 1.0, 0.0),
}


def robot(y, sr):
    t = np.arange(len(y)) / sr
    y = 0.6 * y + 0.4 * y * np.sin(2 * np.pi * 55 * t)
    return sosfilt(butter(2, [300, 3800], "band", fs=sr, output="sos"), y)


def synth(kokoro, speaker, text):
    voice, speed, shift = VOICES[speaker]
    y, sr = kokoro.create(text, voice=voice, speed=speed, lang="en-us" if voice[0] == "a" else "en-gb")
    y, _ = librosa.effects.trim(np.asarray(y, dtype=np.float32), top_db=35)
    if shift:
        y = librosa.effects.pitch_shift(y, sr=sr, n_steps=shift)
    if speaker == "kiosk":
        y = robot(y, sr)
    y = librosa.resample(y, orig_sr=sr, target_sr=SR)
    return y / (np.max(np.abs(y)) + 1e-9) * 0.9


def main():
    model_dir, wav_out, json_out = sys.argv[1:4]
    kokoro = Kokoro(os.path.join(model_dir, "kokoro-v1.0.onnx"), os.path.join(model_dir, "voices-v1.0.bin"))
    st, sh = starts(True), {n: d for n, d, _ in shots(True)}
    n = int((total(True) + 0.5) * SR)
    track = np.zeros(n)
    lines, ok = [], True
    for i, (shot, lt, spk, text) in enumerate(LINES):
        y = synth(kokoro, spk, text)
        t0 = st[shot] + lt
        t1 = t0 + len(y) / SR
        nxt = st[LINES[i + 1][0]] + LINES[i + 1][1] if i + 1 < len(LINES) else total(True)
        flag = "OK"
        if t1 > nxt - 0.05:
            flag, ok = f"OVERLAPS next line by {t1 - nxt + 0.05:.2f}s", False
        print(f"{t0:6.2f}-{t1:6.2f} [{shot} {sh[shot]:.1f}s] {spk:8s} {text!r} {flag}")
        a = int(t0 * SR)
        track[a:a + len(y)] += y[: n - a]
        hop = SR // FPS
        env = [float(np.sqrt(np.mean(y[k:k + hop] ** 2))) for k in range(0, len(y), hop)]
        peak = max(env) or 1.0
        lines.append(dict(speaker=spk, text=text, start=round(t0, 3), end=round(t1, 3),
                          env=[round(min(1.0, e / peak * 1.3), 3) for e in env]))
    if True:
        pcm = (np.stack([track, track], 1) * 32767 * 0.95).clip(-32768, 32767).astype("<i2")
        with wave.open(wav_out, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        with open(json_out, "w") as f:
            json.dump(dict(fps=FPS, lines=lines), f)
    print("ALL LINES FIT" if ok else "SOME LINES DO NOT FIT")


if __name__ == "__main__":
    main()
