#!/usr/bin/env python3
"""Is the lag-5 event pattern itself a covert channel?

Under two of the three surviving branches (nulls, back-references) the
paired lag-5 events are deliberate encoder actions. 57 events could carry
~300 bits in their positions/types — worth a direct look, mirroring the
(negative) doublet-channel probes in covert_channels.py.

Tests on the 57 paired events (29 d1 + 28 d4) in corpus order:

1. type sequence (d1/d4 as bits): balance, runs test, serial correlation
2. inter-event gaps: uniformity of gaps mod 29 / mod 5 / mod 2, and the
   gap distribution vs exponential (memoryless placement)
3. gaps mod 29 decoded as runes: best runeglish-frequency match over all
   58 constant transforms (shift / atbash+shift)
4. event positions: mod-29 and mod-5 uniformity, prime-position count
5. source-glyph sequence (the copied rune values): IoC, runeglish match

Usage: python experiments/event_channel_probe.py
"""

from __future__ import annotations

import json
import math
from collections import Counter

import numpy as np
from scipy.stats import chisquare, kstest

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
N = 29
R2I = {r: i for i, r in enumerate(RUNES)}
CATALOG = "hypotheses/lag5-event-catalog.json"


def runs_test(bits: list[int]) -> float:
    n1, n2 = bits.count(1), bits.count(0)
    runs = 1 + sum(1 for a, b in zip(bits, bits[1:]) if a != b)
    mu = 2 * n1 * n2 / (n1 + n2) + 1
    var = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)
           / ((n1 + n2) ** 2 * (n1 + n2 - 1)))
    return (runs - mu) / math.sqrt(var) if var > 0 else 0.0


def uniformity(vals: list[int], mod: int, label: str) -> None:
    counts = np.bincount([v % mod for v in vals], minlength=mod)
    chi, p = chisquare(counts)
    print(f"  {label} mod {mod}: chi2={chi:.1f} (df {mod-1}), p={p:.3f}")


def runeglish_match(vals: list[int], label: str) -> None:
    uni: Counter = Counter()
    with open("src/aldegonde/data/ngrams/runeglish/unigrams.txt") as f:
        for line in f:
            g, c = line.split()
            uni[R2I[g.replace("ᛂ", "ᛄ")]] += int(c)
    tot = sum(uni.values())
    freq = np.array([uni[i] / tot for i in range(N)])
    ll_flat = math.log(1 / N)
    best = (-1e18, "")
    for atbash in (False, True):
        for shift in range(N):
            t = [(N - 1 - v - shift) % N if atbash else (v - shift) % N
                 for v in vals]
            ll = sum(math.log(freq[x]) for x in t)
            if ll > best[0]:
                best = (ll, f"{'atbash+' if atbash else 'shift-'}{shift}")
    n = len(vals)
    print(f"  {label}: best transform {best[1]}, LL gain over uniform "
          f"{best[0] - n * ll_flat:+.1f} nats over {n} symbols "
          f"(need >> +{1.3 * math.sqrt(n) + 8:.0f} after the 58-transform scan)")


def main() -> None:
    with open(CATALOG) as f:
        cat = json.load(f)
    d1, d4 = cat["d1_events"], cat["d4_events"]
    events = sorted([(i, 0) for i in d1] + [(i, 1) for i in d4])
    pos = [i for i, _ in events]
    types = [t for _, t in events]
    print(f"{len(events)} paired events ({len(d1)} d1, {len(d4)} d4)")

    # 1. type sequence
    z = runs_test(types)
    ac = np.corrcoef(types[:-1], types[1:])[0, 1]
    print(f"\ntype sequence: runs-test z={z:+.2f}, lag-1 r={ac:+.3f}")

    # 2. gaps
    gaps = [b - a for a, b in zip(pos, pos[1:])]
    print(f"\ngaps: n={len(gaps)}, mean={np.mean(gaps):.0f}, "
          f"min={min(gaps)}, max={max(gaps)}")
    lam = 1 / np.mean(gaps)
    ks, p = kstest(gaps, "expon", args=(0, 1 / lam))
    print(f"  KS vs exponential: D={ks:.3f}, p={p:.3f}")
    uniformity(gaps, 29, "gaps")
    uniformity(gaps, 5, "gaps")
    uniformity(gaps, 2, "gaps")

    # 3. gaps as runes
    runeglish_match([g % N for g in gaps], "gaps mod 29 as runes")

    # 4. positions
    uniformity(pos, 29, "positions")
    uniformity(pos, 5, "positions")
    sieve_limit = max(pos) + 1
    is_c = bytearray(sieve_limit)
    for i in range(2, int(sieve_limit ** 0.5) + 1):
        if not is_c[i]:
            for j in range(i * i, sieve_limit, i):
                is_c[j] = 1
    n_prime = sum(1 for i in pos if i >= 2 and not is_c[i])
    dens = sum(1 for i in range(2, sieve_limit) if not is_c[i]) / sieve_limit
    exp = len(pos) * dens
    print(f"  prime positions: {n_prime} vs {exp:.1f} expected "
          f"(z={(n_prime-exp)/math.sqrt(exp):+.2f})")

    # 5. source glyphs (rune at the event start = the copied value)
    by_i = {m["i"]: m["rune"] for m in cat["matches"]}
    src = [R2I[by_i[i]] for i in pos if i in by_i]
    cnt = Counter(src)
    io = (sum(v * (v - 1) for v in cnt.values())
          / (len(src) * (len(src) - 1)) * N)
    print(f"\nsource glyphs: n={len(src)}, nIoC={io:.2f} (uniform 1.0)")
    runeglish_match(src, "source glyphs as runes")


if __name__ == "__main__":
    main()
