#!/usr/bin/env python3
"""Synthesise the soundtrack (music + SFX + ducked dialogue) for "Grandpa vs. the Smart Speaker".

Reuses the series' synthesised SFX and theme music (episodes 1-4) and adds a
quack, sneeze and alarm. "Baby Duck Disco" is the series theme played as a disco
groove; no real song is used.

  VOICE_WAV=voice_track.wav python make_audio.py soundtrack.wav
"""
import os
import sys
import wave

import numpy as np

import ep1
from timeline import SHOTS, TOTAL, shot_starts

A = ep1.audio()
E4 = ep1.ep4_audio()
SR = A.SR


def sfx_quack():
    d = 0.28
    t = A.tt(d)
    f = np.interp(t, [0, 0.08, 0.28], [520, 640, 380])
    y = A.filt(A.osc(f, d, "saw"), "band", [600, 2400]) * np.sin(np.pi * t / d) ** 0.5
    return A.fade(y, 0.005, 0.03) * 0.8


def sfx_achoo():
    d = 0.9
    t = A.tt(d)
    ah = A.filt(A.noise(d), "band", [500, 2000]) * np.clip((t - 0.05) / 0.4, 0, 1) * (t < 0.5) * 0.3
    choo = A.filt(A.noise(d), "band", [1500, 6000]) * np.exp(-np.maximum(t - 0.5, 0) * 12) * (t >= 0.5)
    return A.fade(ah + choo * 1.1, 0.01, 0.05) * 0.8


def sfx_alarm():
    d = 2.4
    t = A.tt(d)
    gate = (np.sin(2 * np.pi * 4 * t) > 0).astype(float)
    return A.fade(A.osc(2000, d, "square") * gate * 0.35, 0.005, 0.05)


SFX = dict(E4.SFX, quack=sfx_quack, achoo=sfx_achoo, alarm=sfx_alarm)


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
    # "Baby Duck Disco" in the hook, cut dead by Grandpa's horror
    put(st["speaker_reply"] + 0.9, A.fade(A.music(st["grandpa_horror"] - st["speaker_reply"] - 0.9), 0.02, 0.01), 0.8,
        mus)
    put(st["leo_gift"], A.pad(st["speaker_order"] - st["leo_gift"]), 0.35, mus)
    # comedy score through the three escalations; silence drop when Grandma walks in
    put(st["speaker_order"], A.fade(A.music(st["grandma_enter"] - st["speaker_order"]), 0.01, 0.05), 0.75, mus)
    # "our song": slow marimba, no drums
    put(st["love_song"], A.fade(A.music(st["night"] - st["love_song"], drums=False, bass=True, mel_gain=0.5),
                                0.2, 0.3), 0.6, mus)
    # silent night, then the disco loop again
    put(st["final"] + 1.9, A.fade(A.music(TOTAL - st["final"] - 1.9), 0.02, 0.5), 0.8, mus)

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
