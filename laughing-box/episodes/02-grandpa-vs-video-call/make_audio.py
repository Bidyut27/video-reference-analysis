#!/usr/bin/env python3
"""Synthesise the soundtrack (music + SFX + ducked dialogue) for "Grandpa vs. the Video Call".

Reuses episode 1's synthesised SFX and theme music so the series sounds the same,
and adds phone, cat and snore sounds. No samples or licensed tracks.

  VOICE_WAV=voice_track.wav python make_audio.py soundtrack.wav
"""
import os
import sys
import wave

import numpy as np

import ep1
from timeline import SHOTS, TOTAL, shot_starts

A = ep1.audio()
SR = A.SR


def sfx_ringtone():
    notes = [76, 79, 84, 79, 76, 79, 84, 88]
    parts = []
    for rep in range(2):
        for i, m in enumerate(notes):
            parts.append((rep * 1.3 + i * 0.12, A.marimba(A.mtof(m), 0.3) * 0.35))
    return A.seq(parts)


def sfx_vibrate():
    d = 0.7
    t = A.tt(d)
    y = A.osc(150, d, "square") * (np.sin(2 * np.pi * 9 * t) > -0.2)
    return A.fade(A.filt(y, "low", 600), 0.01, 0.05) * 0.18


def sfx_snore():
    d = 1.6
    t = A.tt(d)
    env = np.clip(np.sin(np.pi * t / 1.0), 0, 1) ** 1.5 * (t < 1.0)
    y = A.filt(A.osc(85 + 10 * np.sin(2 * np.pi * 30 * t), d, "saw"), "low", 500) * 0.5 + \
        A.filt(A.noise(d), "band", [200, 900]) * 0.4
    whistle = A.osc(1200 + 200 * t, d) * np.clip(np.sin(np.pi * (t - 1.05) / 0.5), 0, 1) * (t > 1.05) * 0.08
    return A.fade(y * env + whistle, 0.02, 0.05) * 0.5


def sfx_meow():
    d = 0.7
    t = A.tt(d)
    f = np.interp(t, [0, 0.15, 0.45, 0.7], [520, 780, 700, 430]) * (1 + 0.02 * np.sin(2 * np.pi * 6 * t))
    y = A.osc(f, d, "saw")
    form = A.filt(y, "band", [700, 1300]) * np.interp(t, [0, 0.2, 0.7], [0.4, 1.0, 0.6]) + \
        A.filt(y, "band", [1800, 3200]) * 0.5
    return A.fade(form * np.sin(np.pi * t / d) ** 0.6, 0.02, 0.08) * 0.9


def sfx_boing():
    d = 0.6
    t = A.tt(d)
    f = 160 + 140 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 5) + 60 * t
    return A.fade(A.osc(f, d) * np.exp(-t * 4), 0.003, 0.05) * 0.55


def sfx_rub():
    d = 0.12
    return A.fade(A.osc(np.linspace(1100, 1600, A.ns(d)), d, "tri"), 0.005, 0.03) * 0.16


def sfx_slap():
    d = 0.12
    return A.filt(A.noise(d), "band", [600, 4000]) * A.edec(A.ns(d), 40) * 0.6


SFX = dict(A.SFX, ringtone=sfx_ringtone, vibrate=sfx_vibrate, snore=sfx_snore, meow=sfx_meow,
           boing=sfx_boing, rub=sfx_rub, slap=sfx_slap)


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
    # calm living-room pad until the call goes wrong
    put(0, A.pad(st["too_close"]), 0.35, mus)
    # comedy score on the three escalations; silence drop when grandma taps
    put(st["too_close"], A.fade(A.music(st["grandma_tap"] - st["too_close"]), 0.01, 0.05), 0.75, mus)
    # light marimba while grandma is the hero, killed by the record scratch
    d = st["view_grandma_cat"] - st["view_grandma"]
    put(st["view_grandma"], A.fade(A.music(d, drums=False, bass=True, mel_gain=0.45), 0.05, 0.01), 0.6, mus)
    # full score back for the payoff and the loop
    put(st["grandpa_laugh"], A.fade(A.music(TOTAL - st["grandpa_laugh"]), 0.02, 0.6), 0.75, mus)

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
