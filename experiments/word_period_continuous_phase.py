# ABOUTME: 29-word base cycle with a CONTINUOUS letter phase -- the phase does
# ABOUTME: not reset per word, so the offset between words 29 apart drifts.
"""Michel's follow-up. word_period_phase_ioc.py assumed the letter phase
RESETS at every word, so positions j and j' in words a period apart share an
alphabet when j == j' (mod 5). If instead the phase runs CONTINUOUSLY across
word boundaries, the alphabet at absolute rune position i is

    A(i) = B(w(i) mod P) . g^(i mod 5)

and two runes share an alphabet iff BOTH

    w(i) == w(i')  (mod P)      -- same disk position
    i    == i'     (mod 5)      -- same letter phase

The offset between word w and word w+P is then the cumulative rune count
between them, mod 5 -- which varies from word to word. That is exactly
"first letter of the first word, second letter of the 29th": a fixed-offset
test looks in the wrong place and sees nothing even if the model is right.

Two implementations:

1. BUCKETED (primary, most power): group every rune by (w mod P, i mod 5) and
   pool the within-bucket coincidence. If the model holds this is the
   plaintext rate (~0.060); otherwise 1/29.
2. PAIRED (Michel's framing): words P apart, pairing j with the drifting
   offset the cumulative length dictates.

Positive control: a PLANTED key of exactly this shape must be detected. If the
test cannot find a machine it was built to find, its null means nothing.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

N = 29
CHANCE = 1.0 / N


def bucket_coincidence(
    stream: list[int], word_id: list[int], period: int, phase_mod: int = 5
) -> tuple[int, int]:
    """Pooled coincidence within buckets keyed by (word mod period, pos mod 5)."""
    buckets: dict[tuple[int, int], list[int]] = {}
    for i, (r, w) in enumerate(zip(stream, word_id)):
        buckets.setdefault((w % period, i % phase_mod), []).append(r)
    hits = tot = 0
    for vals in buckets.values():
        n = len(vals)
        if n < 2:
            continue
        counts: dict[int, int] = {}
        for v in vals:
            counts[v] = counts.get(v, 0) + 1
        hits += sum(c * (c - 1) // 2 for c in counts.values())
        tot += n * (n - 1) // 2
    return hits, tot


def paired_drifting(
    stream: list[int], word_id: list[int], period: int
) -> tuple[int, int, int, int]:
    """Words `period` apart, pairing positions at the drifting phase offset.

    Returns (hits_on, tot_on, hits_off, tot_off) for the phase-matched set and
    its complement.
    """
    starts: dict[int, int] = {}
    words: dict[int, list[int]] = {}
    for i, (r, w) in enumerate(zip(stream, word_id)):
        if w not in starts:
            starts[w] = i
        words.setdefault(w, []).append(r)
    nw = max(words) + 1
    hon = ton = hoff = toff = 0
    for w in range(nw - period):
        a, b = words[w], words[w + period]
        A, B = starts[w], starts[w + period]
        for j in range(len(a)):
            for k in range(len(b)):
                on = (A + j) % 5 == (B + k) % 5
                if on:
                    ton += 1
                    hon += a[j] == b[k]
                else:
                    toff += 1
                    hoff += a[j] == b[k]
    return hon, ton, hoff, toff


def z(hits: int, tot: int, p: float) -> float:
    return (hits - tot * p) / math.sqrt(tot * p * (1 - p)) if tot else float("nan")


def plant(word_lens: list[int], rng: random.Random, period: int) -> list[int]:
    """Encipher iid runeglish-ish plaintext with disk^(w mod period) . g^(i mod 5)."""
    # order-5 g of cycle type 5^5 1^4
    pts = list(range(N))
    rng.shuffle(pts)
    g = list(range(N))
    for c in range(5):
        cyc = pts[5 * c : 5 * c + 5]
        for t in range(5):
            g[cyc[t]] = cyc[(t + 1) % 5]
    gp = [list(range(N))]
    for _ in range(4):
        gp.append([g[x] for x in gp[-1]])
    # a 29-cycle disk
    order = list(range(N))
    rng.shuffle(order)
    disk = list(range(N))
    for t in range(N):
        disk[order[t]] = order[(t + 1) % N]
    dp = [list(range(N))]
    for _ in range(N - 1):
        dp.append([disk[x] for x in dp[-1]])
    # plaintext: iid from a skewed distribution so coincidence ~ 0.060
    weights = [1.0 / (1 + k) ** 0.9 for k in range(N)]
    tot = sum(weights)
    weights = [x / tot for x in weights]
    pool = random.Random(7)
    out: list[int] = []
    i = 0
    for w, L in enumerate(word_lens):
        for _ in range(L):
            p = pool.choices(range(N), weights=weights)[0]
            out.append(dp[w % period][gp[i % 5][p]])
            i += 1
    return out


def main() -> None:
    stream, word_id = load_clean()
    lens: list[int] = []
    for w in word_id:
        while w >= len(lens):
            lens.append(0)
        lens[w] += 1
    print(f"corpus: {len(stream)} runes, {len(lens)} words")
    print(f"chance {CHANCE:.4f} (nIoC 1.000); a shared alphabet gives ~0.060 (nIoC ~1.74)\n")

    # --- POSITIVE CONTROL: plant the exact machine and detect it ------------
    print("POSITIVE CONTROL: ciphertext planted with a 29-disk + continuous phase")
    rng = random.Random(3301)
    planted = plant(lens, rng, 29)
    h, t = bucket_coincidence(planted, word_id, 29)
    print(f"  bucketed at the TRUE period 29: {h}/{t} = {h / t:.4f}  nIoC {h / t * N:.3f}"
          f"   z(chance)={z(h, t, CHANCE):+.2f}")
    assert z(h, t, CHANCE) > 8, "harness cannot detect its own planted machine"
    h2, t2 = bucket_coincidence(planted, word_id, 23)
    print(f"  bucketed at a WRONG period 23: {h2}/{t2} = {h2 / t2:.4f}  nIoC {h2 / t2 * N:.3f}"
          f"   z(chance)={z(h2, t2, CHANCE):+.2f}")
    hon, ton, hoff, toff = paired_drifting(planted, word_id, 29)
    print(f"  paired drifting, phase-matched: {hon}/{ton} = {hon / ton:.4f} "
          f"nIoC {hon / ton * N:.3f}  z={z(hon, ton, CHANCE):+.2f}")
    print(f"  paired drifting, complement:    {hoff}/{toff} = {hoff / toff:.4f} "
          f"nIoC {hoff / toff * N:.3f}  z={z(hoff, toff, CHANCE):+.2f}")
    print("  -> the test finds the machine it was built to find\n")

    # --- THE REAL CORPUS ----------------------------------------------------
    print("THE LP, same tests")
    h, t = bucket_coincidence(stream, word_id, 29)
    print(f"  bucketed (w mod 29, i mod 5): {h}/{t} = {h / t:.4f}  nIoC {h / t * N:.3f}"
          f"   z(chance)={z(h, t, CHANCE):+.2f}")
    hon, ton, hoff, toff = paired_drifting(stream, word_id, 29)
    print(f"  paired drifting, phase-matched: {hon}/{ton} = {hon / ton:.4f} "
          f"nIoC {hon / ton * N:.3f}  z={z(hon, ton, CHANCE):+.2f}")
    print(f"  paired drifting, complement:    {hoff}/{toff} = {hoff / toff:.4f} "
          f"nIoC {hoff / toff * N:.3f}  z={z(hoff, toff, CHANCE):+.2f}")

    # --- scan the period ----------------------------------------------------
    print("\nPERIOD SCAN (bucketed, continuous phase)")
    rows = []
    for p in range(2, 121):
        h, t = bucket_coincidence(stream, word_id, p)
        if t < 3000:
            continue
        rows.append((z(h, t, CHANCE), p, h, t))
    rows.sort(reverse=True)
    for zz, p, h, t in rows[:6]:
        mark = "   <== 29" if p == 29 else ""
        print(f"    P={p:>4}: {h / t:.4f}  nIoC {h / t * N:.3f}  z={zz:+5.2f}{mark}")
    rank = [p for _, p, _, _ in rows].index(29) + 1
    print(f"  29 ranks {rank} of {len(rows)}; scan max |z| {max(abs(r[0]) for r in rows):.2f}"
          f" (noise expects ~{math.sqrt(2 * math.log(len(rows))):.2f})")

    # --- also: phase-only, no disk at all -----------------------------------
    h, t = bucket_coincidence(stream, word_id, 1)
    print(f"\n  phase alone (i mod 5, no disk): {h}/{t} = {h / t:.4f} "
          f"nIoC {h / t * N:.3f}  z={z(h, t, CHANCE):+.2f}")
    print("  (a continuous global phase with NO per-word step would show here)")


if __name__ == "__main__":
    main()
