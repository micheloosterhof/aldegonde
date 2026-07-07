#!/usr/bin/env python3
"""Every interaction channel between the doublets and the lag-5 structure.

The corpus has exactly two anomalies: 86 doublets (suppressed 5x) and
the lag-5 copy events. Prior work established they do not co-tile
(cotiling_test.py) and that event-adjacent runes are corpus-typical
(mark_forensics.py). This script measures the remaining direct
interaction channels:

1. Position overlap: symbols that are simultaneously in a doublet and
   in a lag-5 match, vs independence.
2. Copied doublets: d1 events whose source pair is itself a doublet
   (this would put two doublets at gap 5 -- the observed min doublet
   gap is 6, so the prediction from the data is zero; quantify the
   chance expectation).
3. Distance from each paired event to the nearest doublet, vs a
   Monte Carlo null (uniform doublets with the min-gap-6 dead time).
4. Lag-5 match rate at offsets -12..+12 around doublets (does the
   copy machinery switch off near a doublet, or vice versa?).
5. Doublets inside the 91 hit words and the 9 XY..XY words.

Usage: python experiments/doublet_lag5_interaction.py
"""

from __future__ import annotations

import json
import random

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
CATALOG = "hypotheses/lag5-event-catalog.json"
D = 5


def load() -> np.ndarray:
    with open(DATA) as f:
        raw = f.read()
    pages = [[R2I[ch] for ch in p if ch in R2I] for p in raw.split("%")]
    pages = [p for p in pages if p][:-2]
    return np.array([r for p in pages for r in p], dtype=np.int64)


def main() -> None:
    rng = random.Random(20260707)
    c = load()
    n = len(c)
    with open(CATALOG) as f:
        cat = json.load(f)
    doublets = cat["doublets"]                       # i with C[i] == C[i+1]
    d1 = cat["d1_events"]
    d4 = cat["d4_events"]
    events = sorted(d1 + d4)
    m = c[:-D] == c[D:]

    # 1. symbol-level overlap ------------------------------------------
    in_dbl = np.zeros(n, dtype=bool)
    for i in doublets:
        in_dbl[i] = in_dbl[i + 1] = True
    in_match = np.zeros(n, dtype=bool)
    for i in np.nonzero(m)[0]:
        in_match[i] = in_match[i + D] = True
    both = int((in_dbl & in_match).sum())
    exp = in_dbl.sum() * in_match.sum() / n
    sd = (exp * (1 - in_match.sum() / n)) ** 0.5
    print(f"1. symbols in a doublet AND in a lag-5 match: {both} "
          f"vs {exp:.1f} expected (z={(both-exp)/sd:+.2f})")

    # 2. copied doublets ------------------------------------------------
    src_dbl = sum(1 for i in d1 if c[i] == c[i + 1])
    tgt_dbl = sum(1 for i in d1 if c[i + D] == c[i + D + 1])
    print(f"2. d1 events with doublet source: {src_dbl}; with doublet "
          f"target: {tgt_dbl} (chance ~{len(d1)*0.0066:.2f} each; a copied "
          f"doublet would put two doublets at gap 5 -- min observed gap 6)")

    # 3. nearest-doublet distance from events ---------------------------
    darr = np.array(doublets)

    def nearest(events_: list[int], dbl: np.ndarray) -> float:
        return float(np.mean([np.abs(dbl - e).min() for e in events_]))

    obs = nearest(events, darr)
    sims = []
    for _ in range(2000):
        while True:
            pos = sorted(rng.sample(range(n - 1), len(doublets)))
            if min(b - a for a, b in zip(pos, pos[1:])) >= 6:
                break
        sims.append(nearest(events, np.array(pos)))
    sims = np.array(sims)
    print(f"3. mean |event - nearest doublet|: {obs:.1f} vs null "
          f"{sims.mean():.1f}±{sims.std():.1f} "
          f"(z={(obs-sims.mean())/sims.std():+.2f})")

    # 4. match rate around doublets --------------------------------------
    print("4. lag-5 match rate at offsets around doublets "
          f"(global {m.mean():.4f}):")
    rows = []
    for off in range(-12, 13):
        idx = [i + off for i in doublets if 0 <= i + off < len(m)]
        rate = float(np.mean([m[j] for j in idx]))
        rows.append((off, rate, len(idx)))
    for off, rate, k in rows:
        se = (m.mean() * (1 - m.mean()) / k) ** 0.5
        flag = " *" if abs(rate - m.mean()) > 2.5 * se else ""
        if abs(off) <= 3 or flag:
            print(f"   offset {off:+3d}: {rate:.4f} (n={k}){flag}")

    # 5. doublets in hit words -------------------------------------------
    # word map
    with open(DATA) as f:
        raw = f.read()
    word_of = []
    widx = 0
    in_word = False
    sec = 0
    for ch in raw:
        if ch in R2I:
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
    word_of = np.array(word_of[:n])
    hit_words = {word_of[x["i"]] for x in cat["matches"] if x["within_word"]}
    dbl_words = {word_of[i] for i in doublets
                 if word_of[i] == word_of[i + 1]}
    overlap = len(hit_words & dbl_words)
    # expectation ~ hypergeometric on words weighted by length; report raw
    n_words = word_of.max() + 1
    exp = len(hit_words) * len(dbl_words) / n_words
    print(f"5. words containing both a within-word match and a doublet: "
          f"{overlap} (rough independence expectation {exp:.1f}; "
          f"{len(hit_words)} hit words, {len(dbl_words)} doublet words, "
          f"{n_words} words) -- length confounding makes this an upper-"
          f"bound style check only")


if __name__ == "__main__":
    main()
