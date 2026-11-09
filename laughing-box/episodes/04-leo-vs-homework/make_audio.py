#!/usr/bin/env python3
"""Synthesise the soundtrack (music + SFX + ducked dialogue) for "Leo vs. Homework".

Reuses the series' synthesised SFX and theme music (episodes 1-3) and adds a
knuckle crack, pencil snap, sharpener grind, scribble and purr. No samples.

  VOICE_WAV=voice_track.wav python make_audio.py soundtrack.wav
"""
import os
import sys
import wave

import numpy as np

import ep1
from timeline import SHOTS, TOTAL, shot_starts

A = ep1.audio()
E3 = ep1.ep3_audio()
SR = A.SR


def sfx_crack():
    return A.seq([(k * 0.05, A.filt(A.noise(0.02), "high", 2500) * A.edec(A.ns(0.02), 220) * 0.7)
                  for k in range(3)])


def sfx_snap():
    d = 0.25
    t = A.tt(d)
    crack = A.filt(A.noise(d), "band", [1500, 6000]) * np.exp(-t * 40)
    knock = A.osc(900 * np.exp(-t * 20) + 200, d) * np.exp(-t * 30) * 0.5
    return (crack + knock) * 0.9


def sfx_grind():
    d = 1.9
    t = A.tt(d)
    y = A.filt(A.noise(d), "band", [600, 3000]) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 7 * t)))
    return A.fade(y, 0.05, 0.1) * 0.35


def sfx_scribble():
    d = 0.75
    t = A.tt(d)
    y = A.filt(A.noise(d), "band", [2000, 7000]) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 9 * t)))
    return A.fade(y, 0.02, 0.05) * 0.3


def sfx_purr():
    d = 1.4
    t = A.tt(d)
    y = A.filt(A.noise(d), "low", 300) * (0.5 + 0.5 * np.sin(2 * np.pi * 24 * t)) * np.sin(np.pi * t / d)
    return A.fade(y, 0.05, 0.1) * 1.4


SFX = dict(E3.SFX, crack=sfx_crack, snap=sfx_snap, grind=sfx_grind, scribble=sfx_scribble, purr=sfx_purr)


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
    put(0, A.pad(st["phone_buzz"]), 0.35, mus)
    # comedy score through the three distractions; cut for the sad trombone
    put(st["phone_buzz"], A.fade(A.music(st["leo_desperate"] - st["phone_buzz"]), 0.01, 0.05), 0.75, mus)
    # light marimba while Grandpa "helps", killed by the record scratch on the reveal
    d = st["grandma_read"] + 0.6 - st["grandpa_enter"]
    put(st["grandpa_enter"], A.fade(A.music(d, drums=False, bass=True, mel_gain=0.45), 0.05, 0.01), 0.6, mus)
    # full score for the punchline and the loop
    put(st["grandpa_shrug"], A.fade(A.music(TOTAL - st["grandpa_shrug"]), 0.02, 0.6), 0.75, mus)

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
