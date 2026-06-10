#!/usr/bin/env python3
# ABOUTME: Encrypts Markov-generated runeglish with candidate cipher mechanisms
# ABOUTME: and compares each output's statistical fingerprint to the LP corpus.
"""Mechanism fingerprint harness for the Liber Primus unsolved corpus.

Generates order-2 Markov runeglish from the library's trigram tables, carves
it into the real LP word-length sequence, encrypts it with each candidate
mechanism, and measures the fingerprint that any valid hypothesis must match:

- doublet rate 0.66% (5x suppressed), zero triplets
- unigram nIoC exactly 1.000
- mono kappa at lag 5 only mildly elevated (1.073)
- lag-5 match pairs elevated at separations 1 and 4 only (T5z ~ +4.7)

Results (see the hypothesis files for verdicts):

| mechanism          | doublets | nIoC  | lag-5 d1/d4 pattern |
|--------------------|----------|-------|---------------------|
| observed LP        | 0.66%    | 1.000 | yes (selective)     |
| running-key-text   | 3.6%     | 1.048 | no                  |
| word pt/ct autokey | 3.5-3.6% | ~1.00 | no                  |
| wordpos-key        | 3.7%     | 1.118 | no                  |
| bifid p5/p7/p10    | 3.6-4.0% | 1.19+ | wrong shape         |
| K[i]!=K[i+1] only  | 3.48%    | 1.000 | no                  |
| LFG lag-5 taps     | 3.4-3.5% | 1.000 | no                  |
| output-avoidance   | 0.70%    | 1.000 | no                  |

Two structural conclusions:

1. A no-repeat KEYSTREAM does not suppress ciphertext doublets: a doublet
   needs dP = -dK, and forbidding dK=0 only blocks the plaintext-doublet
   channel, leaving rate ~ (1 - 3.2%)/28 = 3.46%. Doublet suppression
   requires encryption-time feedback from the previous CIPHERTEXT symbol
   (or equivalently plaintext-aware key selection).
2. No tested mechanism reproduces the selective lag-5 d1/d4 paired-match
   structure. It remains the open discriminator.
"""

import random
from collections import Counter, defaultdict
from collections.abc import Callable
from math import sqrt

from aldegonde import c3301

ALPHABET = c3301.CICADA_ALPHABET
MOD = 29
DATA = "data/page0-58.txt"
r2i = c3301.r2i
i2r = c3301.i2r

Mechanism = Callable[[str, list[int]], str]


def load_corpus() -> tuple[str, list[int]]:
    """Return the unsolved corpus and its word-length sequence."""
    with open(DATA) as f:
        raw = f.read()
    pages = [p for p in raw.split("%") if any(c in ALPHABET for c in p)][:-2]
    words = []
    cur: list[str] = []
    for p in pages:
        for ch in p:
            if ch in ALPHABET:
                cur.append(ch)
            elif ch in "-./" and cur:
                words.append("".join(cur))
                cur = []
        if cur:
            words.append("".join(cur))
            cur = []
    return "".join(words), [len(w) for w in words]


def build_markov() -> Callable[[int], str]:
    """Order-2 Markov runeglish generator from the package trigram tables.

    The ngram tables use the variant rune ᛂ where the alphabet uses ᛄ.
    """
    tri = {g.replace("ᛂ", "ᛄ"): c for g, c in c3301.trigrams.items()}
    agg: dict[str, dict[str, int]] = defaultdict(dict)
    for g, c in tri.items():
        agg[g[:2]][g[2]] = c
    cond = {pre: (list(d.keys()), list(d.values())) for pre, d in agg.items()}
    bi = {g.replace("ᛂ", "ᛄ"): c for g, c in c3301.bigrams.items()}
    bks = list(bi.keys())
    bws = list(bi.values())

    def gen(length: int) -> str:
        out = list(random.choices(bks, weights=bws)[0])
        while len(out) < length:
            pre = "".join(out[-2:])
            if pre in cond:
                ks, ws = cond[pre]
                out.append(random.choices(ks, weights=ws)[0])
            else:
                out.append(random.choices(bks, weights=bws)[0][0])
        return "".join(out[:length])

    return gen


# ---------------- mechanisms ----------------
def chop(pt: str, wl: list[int]) -> list[str]:
    """Split a rune stream into words of the given lengths."""
    out = []
    i = 0
    for ln in wl:
        out.append(pt[i : i + ln])
        i += ln
    return out


def enc_otp(pt: str, wl: list[int]) -> str:
    """Control: uniform random key, C = P + K."""
    return "".join(i2r((r2i(c) + random.randrange(MOD)) % MOD) for c in pt)


def make_running_text(gen: Callable[[int], str]) -> Mechanism:
    """Running key from another runeglish text."""

    def enc(pt: str, wl: list[int]) -> str:
        key = gen(len(pt))
        return "".join(i2r((r2i(a) + r2i(b)) % MOD) for a, b in zip(pt, key))

    return enc


def enc_word_pt_autokey(pt: str, wl: list[int]) -> str:
    """Key for word n = plaintext of word n-1, cycled to length."""
    prev = "ᚠᚢᚦ"
    out = []
    for w in chop(pt, wl):
        for k, c in enumerate(w):
            out.append(i2r((r2i(c) + r2i(prev[k % len(prev)])) % MOD))
        prev = w
    return "".join(out)


def enc_word_ct_autokey(pt: str, wl: list[int]) -> str:
    """Key for word n = ciphertext of word n-1, cycled to length."""
    prev = "ᚠᚢᚦ"
    out = []
    for w in chop(pt, wl):
        cw = [i2r((r2i(c) + r2i(prev[k % len(prev)])) % MOD)
              for k, c in enumerate(w)]
        out.extend(cw)
        prev = "".join(cw)
    return "".join(out)


def enc_wordpos_key(pt: str, wl: list[int]) -> str:
    """C = P + S[position within word] for a fixed random S."""
    s = [random.randrange(MOD) for _ in range(20)]
    out = []
    i = 0
    for ln in wl:
        for k in range(ln):
            out.append(i2r((r2i(pt[i + k]) + s[k]) % MOD))
        i += ln
    return "".join(out)


def make_bifid(period: int) -> Mechanism:
    """Bifid-style fractionation over a keyed 6x5 grid (one unused cell)."""

    def enc(pt: str, wl: list[int]) -> str:
        perm = list(range(MOD))
        random.shuffle(perm)
        coord = {i2r(x): (idx // 5, idx % 5) for idx, x in enumerate(perm)}
        letter = {(idx // 5, idx % 5): i2r(x) for idx, x in enumerate(perm)}
        out = []
        for b in range(0, len(pt), period):
            block = pt[b : b + period]
            seq = [coord[c][0] for c in block] + [coord[c][1] for c in block]
            for j in range(len(block)):
                a, bb = seq[2 * j] % 6, seq[2 * j + 1] % 5
                out.append(letter.get((a, bb), letter[(0, 0)]))
        return "".join(out)

    return enc


def enc_norepeat_keystream(pt: str, wl: list[int]) -> str:
    """Keystream with K[i] != K[i+1] but NO ciphertext feedback."""
    k = random.randrange(MOD)
    out = []
    for c in pt:
        out.append(i2r((r2i(c) + k) % MOD))
        nk = random.randrange(MOD - 1)
        if nk >= k:
            nk += 1
        k = nk
    return "".join(out)


def make_lfg(tap1: int, tap2: int, *, avoid: bool) -> Mechanism:
    """Additive lagged-Fibonacci keystream K[i]=K[i-tap1]+K[i-tap2] mod 29,
    optionally with output doublet avoidance (80% re-key on doublet)."""

    def enc(pt: str, wl: list[int]) -> str:
        depth = max(tap1, tap2)
        state = [random.randrange(MOD) for _ in range(depth)]
        out: list[str] = []
        for c in pt:
            k = (state[-tap1] + state[-tap2]) % MOD
            o = (r2i(c) + k) % MOD
            if avoid and out and i2r(o) == out[-1] and random.random() < 0.8:
                k = (k + 1 + random.randrange(MOD - 1)) % MOD
                o = (r2i(c) + k) % MOD
            state.append(k)
            state.pop(0)
            out.append(i2r(o))
        return "".join(out)

    return enc


def enc_output_avoidance(pt: str, wl: list[int]) -> str:
    """OTP with partial avoidance of ciphertext doublets (feedback on C)."""
    out: list[str] = []
    for c in pt:
        o = i2r((r2i(c) + random.randrange(MOD)) % MOD)
        while out and o == out[-1] and random.random() > 0.2:
            o = i2r((r2i(c) + random.randrange(MOD)) % MOD)
        out.append(o)
    return "".join(out)


# ---------------- fingerprint ----------------
def fingerprint(s: str) -> dict[str, float]:
    """Measure the LP discriminating statistics on a rune stream."""
    n = len(s)
    fp: dict[str, float] = {}
    fp["doublet%"] = 100 * sum(1 for i in range(n - 1) if s[i] == s[i + 1]) / (n - 1)
    fp["triplets"] = sum(1 for i in range(n - 2) if s[i] == s[i + 1] == s[i + 2])
    cnt = Counter(s)
    fp["nIoC"] = sum(v * (v - 1) for v in cnt.values()) / (n * (n - 1)) * MOD
    fp["monoK5"] = sum(1 for i in range(n - 5) if s[i] == s[i + 5]) / ((n - 5) / MOD)
    mv = [s[i] == s[i + 5] for i in range(n - 5)]
    m = len(mv)
    for d in (1, 2, 3, 4):
        fp[f"d{d}"] = sum(1 for i in range(m - d) if mv[i] and mv[i + d])
    exp = m / (MOD * MOD)
    fp["T5z"] = (fp["d1"] + fp["d4"] - 2 * exp) / sqrt(2 * exp)
    return fp


def main() -> None:
    """Run every mechanism and print the fingerprint table."""
    text, wlens = load_corpus()
    gen = build_markov()
    reps = 4

    mechs: list[tuple[str, Mechanism | None]] = [
        ("observed-LP", None),
        ("plaintext", lambda pt, wl: pt),
        ("otp-control", enc_otp),
        ("running-key-text", make_running_text(gen)),
        ("word-pt-autokey", enc_word_pt_autokey),
        ("word-ct-autokey", enc_word_ct_autokey),
        ("wordpos-key", enc_wordpos_key),
        ("bifid-p5", make_bifid(5)),
        ("bifid-p7", make_bifid(7)),
        ("bifid-p10", make_bifid(10)),
        ("norepeat-keystrm", enc_norepeat_keystream),
        ("lfg-1-5", make_lfg(1, 5, avoid=False)),
        ("lfg-4-5", make_lfg(4, 5, avoid=False)),
        ("lfg-1-5+avoid", make_lfg(1, 5, avoid=True)),
        ("output-avoidance", enc_output_avoidance),
    ]

    print(f"{'mechanism':18s} {'dbl%':>5s} {'tripl':>5s} {'nIoC':>6s} "
          f"{'monoK5':>6s} {'d1':>4s} {'d2':>4s} {'d3':>4s} {'d4':>4s} {'T5z':>6s}")
    for name, fn in mechs:
        if fn is None:
            fps = [fingerprint(text)]
        else:
            fps = [fingerprint(fn(gen(len(text)), wlens)) for _ in range(reps)]
        avg = {k: sum(f[k] for f in fps) / len(fps) for k in fps[0]}
        print(f"{name:18s} {avg['doublet%']:5.2f} {avg['triplets']:5.1f} "
              f"{avg['nIoC']:6.3f} {avg['monoK5']:6.3f} {avg['d1']:4.0f} "
              f"{avg['d2']:4.0f} {avg['d3']:4.0f} {avg['d4']:4.0f} "
              f"{avg['T5z']:+6.2f}")


if __name__ == "__main__":
    main()
