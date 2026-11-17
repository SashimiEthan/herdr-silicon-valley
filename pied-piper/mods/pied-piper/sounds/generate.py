#!/usr/bin/env python3
"""The theme's two notification sounds: the opening bars of the show's title
music, played again from scratch on a synth built here. No audio from the
recording is in them, only what measuring its first six seconds gave.

What is in those seconds (84 beats a minute, a sixteenth note = 0.1785s): one
synth, a sawtooth with a triangle an octave under it, sliding between notes; a
kick and a snare. A unit of two beats is played four times: two kicks over a
low F, then the snare and a three-note lick (B flat, C, and a note held). The
fourth unit ends differently: the line jumps up early to a high E flat, drops
to the low F for one sixteenth and slides up to a high F.

    needs-you.wav   an agent needs you: the second unit, whose lick ends on
                    the home note, left to ring
    finished.wav    an agent finished: the turn that closes the fourth unit

settings.json names the two files (sounds.blocked and sounds.done). To write
them again: python3 mods/pied-piper/sounds/generate.py
"""
import math, os, random, struct, wave

RATE = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
S16 = 0.1785                      # a sixteenth note
GLIDE = 0.030                     # how fast the synth slides to a new note (time constant)

# As measured: the recording sits about a third of a semitone flat.
NOTE = {"F2": 86.4, "Eb3": 153.3, "F3": 170.8, "Ab3": 205.4, "Bb3": 228.5, "C4": 256.8, "Eb4": 305.4, "F4": 342.8}
LINE = [(4, "F2"), (1, "Bb3"), (1, "C4"), (2, "Ab3"),
        (4, "F2"), (1, "Bb3"), (1, "C4"), (2, "F3"),
        (4, "F2"), (1, "Bb3"), (1, "C4"), (2, "Eb3"),
        (3, "F2"), (2, "Eb4"), (1, "F2"), (2, "F4")]
KICKS = [0, 2, 7, 8, 10, 16, 18, 23, 24, 26]          # in sixteenths
SNARES = [4, 12, 20, 28]
STEPS = [NOTE[name] for count, name in LINE for _ in range(count)]
LEAD = 0.008                      # the synth plays a hair ahead of the drums
EARLY = {30: 0.020}               # and the last slide up starts earlier still


def blep(p, dt):
    """Rounds the sawtooth's jump so it does not ring at pitches that are not there."""
    if p < dt:
        x = p / dt
        return x + x - x * x - 1
    if p > 1 - dt:
        x = (p - 1) / dt
        return x * x + x + x + 1
    return 0.0


def synth(first, last, tail):
    t0 = first * S16
    n = int(((last - first) * S16 + tail) * RATE)
    pitch = math.log(NOTE["F2"])                              # every cut starts from the low note, as the line does
    k = 1 - math.exp(-1 / (GLIDE * RATE))
    lp_k = 1 - math.exp(-2 * math.pi * 4300 / RATE)
    kicks = [s * S16 for s in KICKS if first <= s < last]
    out, p1, p2, lp = [], 0.0, 0.0, 0.0
    for i in range(n):
        t = t0 + i / RATE
        step = int((t + LEAD) / S16)
        if (t + LEAD + EARLY.get(step + 1, 0)) >= (step + 1) * S16:
            step += 1
        pitch += (math.log(STEPS[min(step, last - 1)]) - pitch) * k
        cents = 6 * math.sin(2 * math.pi * 0.8 * t) + 3 * math.sin(2 * math.pi * 5.5 * t)   # worn tape
        f = math.exp(pitch) * 2 ** (cents / 1200)
        p1 = (p1 + f / RATE) % 1.0
        dt = 2 * f / RATE
        p2 = (p2 + dt) % 1.0
        lp += lp_k * ((2 * p2 - 1 - blep(p2, dt)) - lp)        # the saw, its top dulled a little
        duck = 1.0
        for tk in kicks:                                        # the kick pushes the synth down
            if 0 <= t - tk < 0.4:
                duck = min(duck, 1 - 0.6 * math.exp(-(t - tk) / 0.06))
        out.append(duck * ((4 * abs(p1 - 0.5) - 1) + lp))
    return out


def kick():
    n = int(RATE * 0.22)
    rnd = random.Random(3)
    out, ph = [], 0.0
    for i in range(n):
        t = i / RATE
        ph += (75 + 210 * math.exp(-t / 0.028)) / RATE          # a knock falling to a thud
        out.append(math.sin(2 * math.pi * ph) * math.exp(-t / 0.075) + 0.45 * rnd.uniform(-1, 1) * math.exp(-t / 0.006))
    return out


def snare():
    n = int(RATE * 0.30)
    rnd = random.Random(5)
    out, ph, low, mid = [], 0.0, 0.0, 0.0
    for i in range(n):
        t = i / RATE
        ph += (185 + 60 * math.exp(-t / 0.02)) / RATE
        x = rnd.uniform(-1, 1)
        low += 0.13 * (x - low)                                 # a dark rattle
        mid += 0.45 * (x - mid)                                 # and a brighter crack on top
        body = (math.sin(2 * math.pi * ph) + 0.5 * math.sin(2 * math.pi * 1.48 * ph)) * math.exp(-t / 0.055)
        out.append(0.8 * body + 1.6 * low * math.exp(-t / 0.07) + 0.5 * mid * math.exp(-t / 0.045))
    return out


def render(first, last, tail):
    """Sixteenths `first` up to `last`, then the last note let go over `tail` seconds."""
    mix = [0.33 * s for s in synth(first, last, tail)]
    for hits, sound, gain in ((KICKS, kick(), 0.75), (SNARES, snare(), 0.50)):
        for s in hits:
            if first <= s < last:
                at = int((s - first) * S16 * RATE)
                for j, v in enumerate(sound):
                    if at + j < len(mix):
                        mix[at + j] += gain * v
    n, rel = len(mix), int(tail * RATE)
    out = []
    for i, s in enumerate(mix):
        g = 1.0 if i < n - rel else ((n - i) / rel) ** 2
        out.append(math.tanh(1.3 * s) * g)                      # tape-style squash
    return out


def save(name, samples, peak=0.45):
    top = max(abs(s) for s in samples)
    fade = int(RATE * 0.004)
    n = len(samples)
    data = [int(max(-1.0, min(1.0, s / top * peak * min(1.0, i / fade, (n - 1 - i) / fade))) * 32767) for i, s in enumerate(samples)]
    path = os.path.join(HERE, name + ".wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(struct.pack("<%dh" % n, *data))
    print(f"{name + '.wav':22s} {n / RATE:.2f}s")


if __name__ == "__main__":
    save("needs-you", render(8, 16, tail=0.50))
    save("finished", render(26, 32, tail=0.14))
