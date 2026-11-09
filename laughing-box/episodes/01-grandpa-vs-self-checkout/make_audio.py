#!/usr/bin/env python3
"""Synthesise the soundtrack (music + SFX) for "Grandpa vs. the Self-Checkout".

Everything is generated from oscillators and noise, so there are no samples or
licensed tracks.

  python make_audio.py soundtrack.wav
"""
import os
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

from timeline import SHOTS, TOTAL, shot_starts

SR = 44100
RNG = np.random.default_rng(7)


# ---------------------------------------------------------------- synthesis
def ns(d):
    return int(round(d * SR))


def tt(d):
    return np.arange(ns(d)) / SR


def osc(f, d, kind="sine"):
    n = ns(d)
    f = np.full(n, float(f)) if np.isscalar(f) else np.asarray(f)[:n]
    ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == "sine":
        return np.sin(ph)
    if kind == "square":
        return np.sign(np.sin(ph)) * 0.6
    if kind == "saw":
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if kind == "tri":
        return 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1
    raise ValueError(kind)


def noise(d):
    return RNG.uniform(-1, 1, ns(d))


def edec(n, k):
    return np.exp(-np.arange(n) / SR * k)


def fade(x, a=0.005, r=0.02):
    n = len(x)
    na, nr = min(int(a * SR), n), min(int(r * SR), n)
    x = x.copy()
    if na:
        x[:na] *= np.linspace(0, 1, na)
    if nr:
        x[-nr:] *= np.linspace(1, 0, nr)
    return x


def filt(x, kind, fc, order=2):
    return sosfilt(butter(order, fc, kind, fs=SR, output="sos"), x)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def bell(f, d=0.6, dec=6.0):
    t = tt(d)
    y = sum(w * np.sin(2 * np.pi * f * p * t) * np.exp(-t * dec * p) for p, w in ((1, 1), (2.0, 0.4), (3.01, 0.2)))
    return fade(y, 0.002, 0.05)


def brass(f, d):
    y = osc(f, d, "saw") + osc(f * 1.006, d, "saw")
    y = filt(y, "low", 2200)
    n = len(y)
    env = np.minimum(1, np.arange(n) / (0.03 * SR))
    return fade(y * env * 0.5, 0.01, 0.06)


def seq(parts, d=None):
    end = max(t0 + len(x) / SR for t0, x in parts)
    out = np.zeros(int((d or end) * SR) + 1)
    for t0, x in parts:
        i = int(t0 * SR)
        out[i:i + len(x)] += x[: len(out) - i]
    return out


# ---------------------------------------------------------------- sfx
def sfx_buzz():
    d = 0.42
    t = tt(d)
    y = osc(110, d, "square") + 0.6 * osc(166, d, "square")
    y *= ((t < 0.17) | (t > 0.23)).astype(float)
    return fade(filt(y, "low", 1800), 0.003, 0.03) * 0.55


def sfx_beep():
    return fade(osc(1760, 0.12), 0.002, 0.02) * 0.4


def sfx_whoosh(d=0.35, lo=300, hi=3500):
    y = filt(noise(d), "band", [lo, hi])
    return y * np.sin(np.pi * np.linspace(0, 1, len(y))) ** 2 * 0.9


def sfx_impact(big=False):
    d = 0.9 if big else 0.5
    t = tt(d)
    thump = osc(60 * np.exp(-t * 8) + 38, d) * np.exp(-t * (5 if big else 9))
    crack = filt(noise(d), "low", 3000) * np.exp(-t * 28)
    return (thump * 1.0 + crack * (0.9 if big else 0.6)) * (1.0 if big else 0.8)


def sfx_door():
    return seq([(0, bell(659, 0.7, 4)), (0.32, bell(523, 0.9, 4))]) * 0.35


def sfx_step():
    return filt(noise(0.07), "low", 450) * edec(ns(0.07), 60) * 0.6


def sfx_pop():
    d = 0.08
    return fade(osc(np.linspace(300, 950, ns(d)), d), 0.002, 0.02) * 0.4


def sfx_sparkle():
    return seq([(i * 0.06, bell(f, 0.35, 12)) for i, f in enumerate((2093, 2637, 3136, 4186))]) * 0.13


def sfx_gulp():
    d = 0.16
    return seq([(0, fade(osc(np.linspace(520, 170, ns(d)), d))),
                (0.2, fade(osc(np.linspace(400, 150, ns(d)), d)) * 0.6)]) * 0.35


def sfx_squeak():
    d = 0.18
    return fade(osc(np.linspace(900, 1500, ns(d)), d, "tri"), 0.005, 0.04) * 0.25


def sfx_steam():
    d = 1.6
    t = tt(d)
    hiss = filt(noise(d), "high", 3000) * np.minimum(1, t / 0.3) * 0.3
    whistle = osc(2100 + 300 * t + 60 * np.sin(2 * np.pi * 7 * t), d) * np.minimum(1, t / 0.8) * 0.18
    return fade(hiss + whistle, 0.01, 0.2)


def sfx_tick():
    return filt(noise(0.015), "high", 2500) * edec(ns(0.015), 200) * 0.25


def sfx_yawn():
    d = 1.0
    t = tt(d)
    f = np.interp(t, [0, 0.4, 1], [220, 330, 170]) * (1 + 0.02 * np.sin(2 * np.pi * 5 * t))
    y = filt(osc(f, d, "saw"), "low", 900)
    return fade(y * np.sin(np.pi * t / d), 0.05, 0.1) * 0.18


def sfx_taiko():
    d = 0.7
    t = tt(d)
    return (osc(95 * np.exp(-t * 3) + 48, d) * np.exp(-t * 6) +
            filt(noise(d), "low", 700) * np.exp(-t * 25) * 0.6) * 0.9


def sfx_glitch():
    parts = []
    t0 = 0.0
    while t0 < 0.5:
        parts.append((t0, fade(osc(RNG.uniform(150, 2200), 0.03, "square"), 0.001, 0.005) * 0.25))
        t0 += RNG.uniform(0.03, 0.07)
    return seq(parts)


def sfx_chime_ok():
    return seq([(0, bell(1318.5, 0.6, 5)), (0.12, bell(1975.5, 0.9, 4))]) * 0.4


def sfx_fanfare():
    parts = [(0.0, brass(mtof(67), 0.12)), (0.13, brass(mtof(72), 0.12)), (0.26, brass(mtof(76), 0.12))]
    for m in (60, 64, 67, 72, 79):
        parts.append((0.4, brass(mtof(m), 1.3) * 0.7))
    parts += [(1.75, brass(mtof(m), 0.12) * 0.8) for m in (72, 76)]
    parts += [(1.9, brass(mtof(m), 0.6) * 0.8) for m in (65, 69, 72, 77)]
    return seq(parts) * 0.35


def sfx_clap():
    d = 0.1
    return seq([(k * 0.008, filt(noise(d), "band", [900, 3200]) * edec(ns(d), 45)) for k in range(3)]) * 0.35


def sfx_cart():
    d = 2.8
    y = np.zeros(ns(d))
    for _ in range(90):
        i = RNG.integers(0, len(y) - 900)
        y[i:i + 900] += filt(noise(900 / SR), "band", [1500, 5000]) * edec(900, 120) * RNG.uniform(0.2, 0.6)
    return fade(y, 0.2, 0.4) * 0.5


def sfx_scratch():
    d = 0.45
    t = tt(d)
    f = 250 + 1300 * np.sin(np.pi * np.clip(t / 0.18, 0, 1)) ** 2 * (t < 0.18) + \
        np.where(t >= 0.18, 900 * np.exp(-(t - 0.18) * 10), 0)
    y = filt(osc(f, d, "saw"), "band", [200, 4000]) * 0.5 + filt(noise(d), "band", [800, 3000]) * 0.4
    return fade(y, 0.002, 0.05) * 0.8


def sfx_printer():
    d = 1.6
    t = tt(d)
    y = osc(60, d, "square") * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 18 * t)))
    return fade(filt(y, "low", 1500), 0.02, 0.1) * 0.14


def sfx_dundun():
    parts = [(0.0, brass(146.8, 0.22)), (0.3, brass(146.8, 0.22))]
    parts += [(0.6, brass(f, 1.4) * 0.8) for f in (73.4, 110, 146.8, 174.6)]
    return seq(parts) * 0.5


def sfx_sadtrombone():
    parts = []
    t0 = 0.0
    for f, d in ((196, 0.38), (185, 0.38), (174.6, 0.38), (164.8, 1.4)):
        t = tt(d)
        vib = 1 + (0.03 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.3) if d > 1 else 0)
        y = filt(osc(f * vib, d, "saw"), "low", 1100)
        env = np.sin(np.pi * np.minimum(t / d, 1)) ** 0.5
        parts.append((t0, fade(y * env, 0.03, 0.08)))
        t0 += d
    return seq(parts) * 0.45


def sfx_tap():
    return filt(noise(0.02), "high", 2000) * edec(ns(0.02), 150) * 0.5


SFX = {
    "buzz": sfx_buzz, "beep": sfx_beep, "whoosh": sfx_whoosh, "whoosh_s": lambda: sfx_whoosh(0.25, 800, 5000) * 0.6,
    "zoom": lambda: sfx_whoosh(0.18, 500, 6000), "impact": sfx_impact, "impact_big": lambda: sfx_impact(True),
    "stamp": lambda: sfx_impact() * 0.5, "door": sfx_door, "step": sfx_step, "pop": sfx_pop,
    "sparkle": sfx_sparkle, "gulp": sfx_gulp, "squeak": sfx_squeak, "steam": sfx_steam, "tick": sfx_tick,
    "yawn": sfx_yawn, "taiko": sfx_taiko, "glitch": sfx_glitch, "chime_ok": sfx_chime_ok,
    "ding": lambda: bell(2637, 0.6, 6) * 0.3, "ding_wink": lambda: seq([(0, bell(1568, 0.6, 5) * 0.3), (0.05, sfx_sparkle())]),
    "fanfare": sfx_fanfare, "clap": sfx_clap, "cart": sfx_cart, "scratch": sfx_scratch, "printer": sfx_printer,
    "dundun": sfx_dundun, "sadtrombone": sfx_sadtrombone, "tap": sfx_tap,
}


# ---------------------------------------------------------------- music
BPM = 130
EIGHTH = 60 / BPM / 2
ROOTS = [48, 53, 55, 48]  # C F G C
MELODY = [[67, None, 64, 67, 69, 67, 64, None], [69, None, 65, 69, 72, 69, 65, None],
          [71, None, 67, 71, 74, 72, 71, 69], [67, 64, 60, None, 72, None, None, None]]


def pluck(f, d):
    y = filt(osc(f, d, "saw"), "low", 1400)
    return fade(y * edec(len(y), 9), 0.003, 0.02)


def marimba(f, d):
    t = tt(d)
    return fade((np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 30)) * np.exp(-t * 11),
                0.002, 0.02)


def kick():
    d = 0.25
    t = tt(d)
    return osc(110 * np.exp(-t * 25) + 45, d) * np.exp(-t * 10)


def snare():
    d = 0.18
    return filt(noise(d), "band", [1500, 6000]) * edec(ns(d), 22) * 0.45 + osc(190, d) * edec(ns(d), 30) * 0.25


def hat():
    d = 0.04
    return filt(noise(d), "high", 7000) * edec(ns(d), 70) * 0.3


def music(d, drums=True, bass=True, mel_gain=0.32):
    out = np.zeros(ns(d) + SR)
    n_steps = int(d / EIGHTH) + 1
    k, s_, h_, = kick(), snare(), hat()
    for n in range(n_steps):
        t0 = n * EIGHTH
        bar, step = (n // 8) % 4, n % 8
        i = int(t0 * SR)
        parts = []
        if bass:
            root = ROOTS[bar] - (12 if step % 2 == 0 else 0)
            parts.append(pluck(mtof(root), EIGHTH * 0.9) * 0.5)
        m = MELODY[bar][step]
        if m is not None:
            if (n // 32) % 2 == 1:
                m += 12
            parts.append(marimba(mtof(m), EIGHTH * 2) * mel_gain)
        if drums:
            if step in (0, 4):
                parts.append(k * 0.8)
            if step in (2, 6):
                parts.append(s_)
            parts.append(h_ * (1.0 if step % 2 else 0.6))
        for p in parts:
            out[i:i + len(p)] += p[: len(out) - i]
    return out[: ns(d)]


def pad(d):
    t = tt(d)
    y = sum(np.sin(2 * np.pi * mtof(m) * t) for m in (60, 64, 67, 72)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * t))
    return fade(y * 0.25, 0.4, 0.05)


# ---------------------------------------------------------------- mix
def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav"
    st = shot_starts()
    n = int((TOTAL + 0.5) * SR)
    mix = np.zeros(n)
    mus = np.zeros(n)

    def put(t0, x, g=1.0, bus=None):
        bus = mix if bus is None else bus
        i = int(t0 * SR)
        if i >= n:
            return
        bus[i:i + len(x)] += (x * g)[: n - i]

    # room tone throughout
    put(0, filt(noise(TOTAL), "low", 300) * 0.04)
    # quiet store pad until the conflict starts
    put(0, pad(st["scan1"]), 0.35, mus)
    # comedy score: enters on the first rejection, cut dead on the glitch (silence drop)
    put(st["scan1"], fade(music(st["glitch"] - st["scan1"]), 0.01, 0.01), 0.8, mus)
    # resumes after the fanfare, then killed by the record scratch
    put(st["victory"] + 2.6, fade(music(st["receipt"] - st["victory"] - 2.6), 0.05, 0.01), 0.8, mus)
    # light marimba ditty for grandma, cut by the final buzz
    d = st["final"] + 0.95 - (st["grandma_pays"] + 0.9)
    put(st["grandma_pays"] + 0.9, fade(music(d, drums=False, bass=True, mel_gain=0.45), 0.05, 0.03), 0.6, mus)

    for name, _, cues in SHOTS:
        for lt, sname in cues:
            put(st[name] + lt, SFX[sname]())

    voice_path = os.environ.get("VOICE_WAV")
    if voice_path:
        with wave.open(voice_path) as w:
            v = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, 2)[:, 0] / 32768.0
        v = np.pad(v, (0, max(0, n - len(v))))[:n]
        # duck music and SFX under dialogue (~0.25 s release)
        env = np.minimum(1, filt(np.abs(v), "low", 4) * 6)
        mus *= 1 - 0.6 * env
        mix *= 1 - 0.35 * env
        mix += v * 1.1
    mix += mus

    mix /= np.max(np.abs(mix)) / 0.9
    stereo = np.stack([mix, mix], axis=1)
    pcm = (stereo * 32767).astype("<i2")
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out_path} ({TOTAL:.2f}s)")


if __name__ == "__main__":
    main()
