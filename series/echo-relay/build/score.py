"""Synthesize the 52.5 s ambient score for ECHO RELAY EP01 -> score.wav."""
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 52.5
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "ep01_score.wav"

t = np.arange(int(SR * DUR)) / SR
L = np.zeros_like(t)
R = np.zeros_like(t)


def add(sig, start=0.0, pan=0.0, gain=1.0):
    global L, R
    i0 = int(start * SR)
    n = len(sig)
    if i0 + n >= len(L):
        n = len(L) - i0
        sig = sig[:n]
    gl = gain * min(1.0, 1.0 - pan)
    gr = gain * min(1.0, 1.0 + pan)
    L[i0:i0 + n] += sig * gl
    R[i0:i0 + n] += sig * gr


def env(n, a, r):
    e = np.ones(n)
    an, rn = int(a * SR), int(r * SR)
    e[:an] = np.linspace(0, 1, an)
    e[-rn:] *= np.linspace(1, 0, rn)
    return e


def tone(freq, dur, shape="sine"):
    tt = np.arange(int(dur * SR)) / SR
    if shape == "sine":
        return np.sin(2 * np.pi * freq * tt)
    if shape == "tri":
        return 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * tt))
    raise ValueError(shape)


# slow A-minor-ish drone pad, breathing
pad_g = 0.05 + 0.02 * np.sin(2 * np.pi * 0.05 * t)
for f in (55.0, 82.4, 110.0, 130.8, 164.8):
    det = 1.0 + 0.002 * np.sin(2 * np.pi * 0.07 * t + f)
    wob = np.sin(2 * np.pi * f * np.cumsum(np.ones_like(t)) / SR * (1 + 0 * det))
    s = np.sin(2 * np.pi * np.cumsum(np.full(len(t), f / SR)))
    add(s * pad_g, pan=0.1 * np.sin(f))

# dark noise bed
rng = np.random.default_rng(2087)
noise = rng.standard_normal(len(t))
for k in range(1, 6):
    noise -= np.sin(2 * np.pi * k * 50 * t)  # crude tone removal
noise *= 0.012
add(noise[: int(len(t))], gain=1.0)

# heartbeat sub-thumps every 2 s, growing
pulse_rate = 2.0
pulse_gain = 0.10 + 0.10 * (t / DUR)
tt = np.arange(int(0.5 * SR)) / SR
thump = np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 9)
times = np.arange(0.5, DUR - 0.6, pulse_rate)
for k, ti in enumerate(times):
    g = 0.10 + 0.14 * (k / len(times))
    add(thump, start=ti, gain=g)

# open: lonely high drone swell (shots 1-2)
sw = tone(329.6, 9.0) * env(len(tone(329.6, 9.0)), 3.5, 3.5) * 0.03
add(sw, start=0.0)

# alarm beeps during shot 3 (t 9.0-13.5)
for mode, ti in enumerate(np.arange(9.2, 13.4, 0.7)):
    bb = tone(587 if mode % 2 else 440, 0.30) * env(int(0.3 * SR), 0.02, 0.2)
    add(bb, start=ti, gain=0.05, pan=0.2 if mode % 2 else -0.2)

# beacon pings from shot 4 onward
ping = tone(880, 1.1) * env(int(1.1 * SR), 0.005, 1.0)
for ti in np.arange(14.0, 44.0, 5.0):
    add(ping, start=ti, gain=0.035)
    add(ping, start=ti + 0.42, gain=0.014, pan=-0.25)

# tension riser into the final wide shot (44-48.5)
n = int(4.5 * SR)
tt = np.arange(n) / SR
sweep = np.sin(2 * np.pi * (110 + 220 * (tt / 4.5) ** 2) * tt) * np.linspace(0, 0.09, n)
add(sweep, start=44.0)

# low boom on the title card, then silence
boom = np.sin(2 * np.pi * 44 * np.arange(int(3.0 * SR)) / SR) * np.exp(
    -np.arange(int(3.0 * SR)) / SR * 1.6
)
add(boom, start=48.5, gain=0.30)

mix = np.stack([L, R], axis=1)
mix[: SR] *= np.linspace(0, 1, SR)[:, None]
mix[-2 * SR:] *= np.linspace(1, 0, 2 * SR)[:, None]
mix = mix / max(1e-9, np.abs(mix).max()) * 0.75

with wave.open(str(OUT), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", OUT, f"{DUR}s")
