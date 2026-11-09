#!/usr/bin/env python3
"""Synthesise the soundtrack (music + SFX + ducked dialogue) for "Grandma vs. the Robot Vacuum".

Reuses the series' synthesised SFX and theme music (episodes 1-2) and adds a
vacuum motor, bonk, slurp and hiccup. No samples or licensed tracks.

  VOICE_WAV=voice_track.wav python make_audio.py soundtrack.wav
"""
import os
import sys
import wave

import numpy as np

import ep1
from timeline import SHOTS, TOTAL, shot_starts

A = ep1.audio()
E2 = ep1.ep2_audio()
SR = A.SR


def sfx_motor():
    d = 1.4
    t = A.tt(d)
    whine = A.osc(420 + 30 * np.sin(2 * np.pi * 3 * t), d, "saw")
    y = A.filt(whine, "band", [300, 1800]) * 0.25 + A.filt(A.noise(d), "band", [1500, 5000]) * 0.18
    env = np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.3)
    return y * env * 0.7


def sfx_bonk():
    d = 0.25
    t = A.tt(d)
    return A.fade(A.osc(330 * np.exp(-t * 6) + 120, d, "tri") * np.exp(-t * 18), 0.002, 0.03) * 0.6


def sfx_slurp():
    d = 0.6
    t = A.tt(d)
    y = A.filt(A.noise(d), "band", [400, 2200]) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t))
    y += A.osc(np.linspace(300, 900, A.ns(d)), d) * 0.2
    return A.fade(y * np.sin(np.pi * t / d), 0.02, 0.05) * 0.5


def sfx_hiccup():
    d = 0.18
    return A.fade(A.osc(np.linspace(500, 1300, A.ns(d)), d, "tri"), 0.003, 0.04) * 0.45


SFX = dict(E2.SFX, motor=sfx_motor, bonk=sfx_bonk, slurp=sfx_slurp, hiccup=sfx_hiccup)


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav"
    st = shot_starts()
    n = int((TOTAL + 0.5) * SR)
    mix = np.zeros(n)
    mus = np.zeros(n)

    def put(t0, x, g=1.0, bus=None):
        bus = mix if bus is None else bus
        i = int(t0 * SR)
        if i < n:
            bus[i:i + len(x)] += (x * g)[: n - i]

    put(0, A.filt(A.noise(TOTAL), "low", 300) * 0.035)
    put(0, A.pad(st["bump"]), 0.35, mus)
    # comedy score from the first bump; silence drop on the crash
    put(st["bump"], A.fade(A.music(st["crash"] - st["bump"]), 0.01, 0.01), 0.75, mus)
    # light marimba for "next day", cut by the record scratch
    d = st["grandpa_shock"] - st["next_day"] - 0.75
    put(st["next_day"] + 0.75, A.fade(A.music(d, drums=False, bass=True, mel_gain=0.45), 0.05, 0.01), 0.6, mus)
    # full score for the double chase and the loop
    put(st["double_chase"], A.fade(A.music(TOTAL - st["double_chase"]), 0.02, 0.6), 0.75, mus)

    for name, _, cues in SHOTS:
        for lt, sname in cues:
            put(st[name] + lt, SFX[sname]())

    voice_path = os.environ.get("VOICE_WAV")
    if voice_path:
        with wave.open(voice_path) as w:
            v = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2)[:, 0] / 32768.0
        v = np.pad(v, (0, max(0, n - len(v))))[:n]
        env = np.minimum(1, A.filt(np.abs(v), "low", 4) * 6)
        mus *= 1 - 0.6 * env
        mix *= 1 - 0.35 * env
        mix += v * 1.1
    mix += mus
    mix /= np.max(np.abs(mix)) / 0.9
    pcm = (np.stack([mix, mix], axis=1) * 32767).astype("<i2")
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out_path} ({TOTAL:.2f}s)")


if __name__ == "__main__":
    main()
