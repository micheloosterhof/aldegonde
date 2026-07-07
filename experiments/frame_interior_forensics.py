#!/usr/bin/env python3
"""Forensics on the interiors of the 28 frame (d4) events.

A frame event at start i is C[i] = C[i+5] and C[i+4] = C[i+9]: two
contiguous 5-windows agreeing in their edge glyphs, X···Y X'···Y' with
X = X', Y = Y'. This script characterizes "the space between": the two
3-rune interiors A = C[i+1..i+3] and B = C[i+6..i+8], and the geometry
of the whole 10-rune span.

Tested relations between A and B (each would survive the earlier
per-position tests if present):

    identity        B == A                (per-position matches)
    constant shift  B == A + t, t != 0    (an additive re-key of the
                                           interior only)
    reversal        B == reverse(A)
    permutation     multiset(B) == multiset(A)
    partial overlap |multiset(A) & multiset(B)| distribution

Also: the X-Y edge relation (is Y tied to X?), doublets inside the
span, interior rune typicality, and where word boundaries fall inside
the span (do frames bracket a word junction?), each against a
Monte Carlo null of random span-10 windows.

n = 28, so only strong effects are detectable; the value of this scan
is closing the "the interiors carry the message" family cheaply.

Usage: python experiments/frame_interior_forensics.py
"""

from __future__ import annotations

import json
import random
from collections import Counter

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
CATALOG = "hypotheses/lag5-event-catalog.json"
D = 5


def load():
    with open(DATA) as f:
        raw = f.read()
    stream: list[int] = []
    word_of: list[int] = []
    widx = 0
    in_word = False
    sec = 0
    for ch in raw:
        if ch in R2I:
            stream.append(R2I[ch])
            word_of.append(widx)
            in_word = True
        elif ch == "$":
            if in_word:
                widx += 1
                in_word = False
            sec += 1
            if sec >= 10:
                break
        elif ch in "-.&%" and in_word:
            widx += 1
            in_word = False
    c = np.array(stream, dtype=np.int64)
    assert len(c) == 12956
    return c, np.array(word_of[: len(c)])


def main() -> None:
    rng = random.Random(20260707)
    c, word_of = load()
    n = len(c)
    with open(CATALOG) as f:
        cat = json.load(f)
    d4 = cat["d4_events"]
    k_ev = len(d4)
    print(f"{k_ev} frame events; span = 10 runes each\n")

    # ---------------- relations between the two interiors A and B
    ident = shift = rever = perm = 0
    overlaps = []
    shift_vals = []
    for i in d4:
        a = c[i + 1: i + 4]
        b = c[i + 6: i + 9]
        deltas = (b - a) % MOD
        if (deltas == 0).all():
            ident += 1
        elif (deltas == deltas[0]).all():
            shift += 1
            shift_vals.append(int(deltas[0]))
        if (b == a[::-1]).all():
            rever += 1
        ca, cb = Counter(a.tolist()), Counter(b.tolist())
        inter = sum((ca & cb).values())
        overlaps.append(inter)
        if inter == 3:
            perm += 1
    # chance levels per event
    p_ident = (1 / MOD) ** 3
    p_shift = 28 / MOD ** 2 / MOD * MOD  # P(d1==d2==d3, common value != 0)
    p_shift = 28 / MOD ** 2
    p_rev = (1 / MOD) ** 3
    print("interior A -> interior B relations (chance expectation):")
    print(f"  identity     : {ident} ({k_ev * p_ident:.4f})")
    print(f"  constant shift: {shift} ({k_ev * p_shift:.2f})"
          + (f"  values={shift_vals}" if shift_vals else ""))
    print(f"  reversal     : {rever} ({k_ev * p_rev:.4f})")
    print(f"  permutation  : {perm} (multiset-equal; chance ~"
          f"{k_ev * 20 / MOD ** 3:.3f})")
    # overlap distribution vs null (random unrelated triples)
    sims = []
    for _ in range(20000):
        a = [rng.randrange(MOD) for _ in range(3)]
        b = [rng.randrange(MOD) for _ in range(3)]
        sims.append(sum((Counter(a) & Counter(b)).values()))
    sim_mean = np.mean(sims) * k_ev
    obs_total = sum(overlaps)
    print(f"  total shared glyphs (multiset): {obs_total} vs "
          f"{sim_mean:.1f} expected; per-event dist "
          f"{Counter(overlaps)}")

    # ---------------- the X-Y edge relation
    xy = [(int(c[i]), int(c[i + 4])) for i in d4]
    same = sum(1 for x, y in xy if x == y)
    dxy = Counter((y - x) % MOD for x, y in xy)
    print(f"\nedges: X == Y in {same}/{k_ev} events "
          f"(chance {k_ev / MOD:.1f}); (Y-X) mod 29 spread over "
          f"{len(dxy)} values, max multiplicity {max(dxy.values())}")

    # ---------------- doublets inside the spans
    dbl_in = sum(1 for i in d4 for t in range(i, i + 9)
                 if c[t] == c[t + 1])
    exp_dbl = k_ev * 9 * float((c[1:] == c[:-1]).mean())
    print(f"doublets inside spans: {dbl_in} vs {exp_dbl:.1f} expected")

    # ---------------- interior rune typicality
    pooled = np.concatenate([c[i + 1: i + 4] for i in d4]
                            + [c[i + 6: i + 9] for i in d4])
    counts = np.bincount(pooled, minlength=MOD)
    base = np.bincount(c, minlength=MOD) / n
    chi = float(((counts - len(pooled) * base) ** 2
                 / (len(pooled) * base)).sum())
    print(f"interior rune frequencies: chi2 = {chi:.1f} (df 28) "
          f"over {len(pooled)} runes")

    # ---------------- word-boundary geometry inside the span
    def boundary_profile(starts: list[int]) -> tuple[np.ndarray, Counter]:
        prof = np.zeros(9, dtype=float)
        nb = Counter()
        for i in starts:
            b = 0
            for t in range(9):
                if word_of[i + t] != word_of[i + t + 1]:
                    prof[t] += 1
                    b += 1
            nb[b] += 1
        return prof, nb

    obs_prof, obs_nb = boundary_profile(d4)
    null_starts = [rng.randrange(n - 10) for _ in range(20000)]
    null_prof, null_nb = boundary_profile(null_starts)
    null_prof *= k_ev / 20000
    print("\nword boundaries inside the 10-rune span "
          "(offset: observed vs null):")
    for t in range(9):
        se = (null_prof[t] * (1 - null_prof[t] / k_ev)) ** 0.5
        z = (obs_prof[t] - null_prof[t]) / se if se else 0.0
        print(f"  after offset {t}: {int(obs_prof[t]):>2} vs "
              f"{null_prof[t]:.1f} (z={z:+.2f})")
    mean_b_obs = sum(k * v for k, v in obs_nb.items()) / k_ev
    mean_b_null = sum(k * v for k, v in null_nb.items()) / 20000
    print(f"boundaries per span: mean {mean_b_obs:.2f} vs null "
          f"{mean_b_null:.2f}; distribution {dict(sorted(obs_nb.items()))}")

    # is there preferentially a boundary strictly between X and Y
    # (offsets 0..3 of each window)?
    def between_edges(starts):
        cnt = 0
        for i in starts:
            if any(word_of[i + t] != word_of[i + t + 1] for t in range(4)):
                cnt += 1
        return cnt

    obs_be = between_edges(d4)
    null_be = between_edges(null_starts) * k_ev / 20000
    se = (null_be * (1 - null_be / k_ev)) ** 0.5
    print(f"events with a boundary inside the FIRST window (X···Y): "
          f"{obs_be} vs {null_be:.1f} (z={(obs_be-null_be)/se:+.2f})")


if __name__ == "__main__":
    main()
