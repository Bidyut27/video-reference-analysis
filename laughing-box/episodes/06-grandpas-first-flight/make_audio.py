#!/usr/bin/env python3
"""Synthesise the soundtrack (music + SFX + ducked dialogue) for "Grandpa's First Flight".

Reuses the series' synthesised SFX and theme music (episodes 1-5) and adds the
call-button bing, seat-belt click, life-vest inflate, jet engine and cork pop.
No samples or licensed tracks.

  VOICE_WAV=voice_track.wav python make_audio.py soundtrack.wav
"""
import os
import sys
import wave

import numpy as np

import ep1
from timeline import SHOTS, TOTAL, shot_starts

A = ep1.audio()
E5 = ep1.ep5_audio()
SR = A.SR


def sfx_bing():
    return A.bell(1318.5, 0.5, 5) * 0.35


def sfx_click():
    return A.seq([(0, A.filt(A.noise(0.012), "high", 3000) * A.edec(A.ns(0.012), 300) * 0.8),
                  (0.035, A.filt(A.noise(0.012), "high", 2000) * A.edec(A.ns(0.012), 300) * 0.6)])


def sfx_inflate():
    d = 0.5
    t = A.tt(d)
    hiss = A.filt(A.noise(d), "band", [800, 5000]) * np.minimum(1, t / 0.05) * 0.4
    rise = A.osc(np.linspace(180, 900, A.ns(d)), d, "tri") * 0.18
    return A.fade(hiss + rise, 0.005, 0.03)


def sfx_engine():
    d = 2.6
    t = A.tt(d)
    swell = np.minimum(1, t / 1.2)
    nz = A.noise(d)
    # crossfade two fixed low-passes: the roar opens up as the engines spool
    roar = (A.filt(nz, "low", 400) * (1 - swell) + A.filt(nz, "low", 1300) * swell) * (0.4 + 0.6 * swell)
    whine = A.osc(300 + 500 * swell, d, "saw") * 0.06 * swell
    return A.fade((roar + A.filt(whine, "band", [300, 2500])) * 0.7, 0.05, 0.4)


def sfx_cork():
    d = 0.18
    t = A.tt(d)
    return A.fade(A.osc(700 * np.exp(-t * 18) + 250, d) * np.exp(-t * 25), 0.001, 0.02) * 0.9


SFX = dict(E5.SFX, bing=sfx_bing, click=sfx_click, inflate=sfx_inflate, engine=sfx_engine, cork=sfx_cork)


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

    # cabin hum throughout
    put(0, A.filt(A.noise(TOTAL), "low", 220) * 0.07)
    put(0, A.pad(st["belt_pull"]), 0.35, mus)
    # comedy score from the seat belt; silence drop for the POOF
    put(st["belt_pull"], A.fade(A.music(st["vest_poof"] - st["belt_pull"]), 0.01, 0.01), 0.75, mus)
    # back in after takeoff, through the call-button montage
    put(st["plane_exterior"], A.fade(A.music(st["grandma_sleep"] - st["plane_exterior"]), 0.05, 0.1), 0.75, mus)
    # gentle marimba for the sunset, cut by the PA chime
    put(st["sunset"], A.fade(A.music(st["pilot_pa"] - st["sunset"], drums=False, bass=True, mel_gain=0.5),
                             0.2, 0.02), 0.6, mus)
    # full score for the escape attempt and the loop
    put(st["grandpa_no"], A.fade(A.music(TOTAL - st["grandpa_no"]), 0.02, 0.6), 0.75, mus)

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
