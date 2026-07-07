#!/usr/bin/env python3
"""Battery 20: Fibonacci-spacing probes.

Prompted by the recollection that a late 3301 communication hid a hint
in its whitespace at Fibonacci distances. If the LP hides anything at
Fibonacci distances, the places it could live are enumerable:

A. Runes AT Fibonacci positions (corpus-, section-, and page-aligned,
   both 0- and 1-indexed): pooled extraction scored by runeglish
   unigram LL and IoC against random-position draws of the same size.
B. Doublet gaps and lag-5 event gaps: Fibonacci membership counts vs
   uniform-placement Monte Carlo.
C. Word lengths and sentence lengths (in words): fraction Fibonacci
   {1,2,3,5,8,13,21,34} vs the solved-section control (Cicada's own
   style) and the lexicon.
D. Word boundaries falling AT Fibonacci rune-positions of their page:
   count vs within-page word-length-shuffle null.
E. Keystream attacks with Fibonacci-position interrupts: per page, the
   standard streams, key skips one extra symbol (or restarts) at the
   Fibonacci positions of the page; runeglish unigram LL z-scores.
   (The solved AN END page used position-triggered interrupts, so this
   closes the "interrupts at Fibonacci positions" variant.)

Usage: python experiments/lp_battery20.py
"""

from __future__ import annotations

import collections
import math
import random

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
N = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
MASTER = "data/liber-primus__transcription--master.txt"

FIBS = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987,
        1597, 2584, 4181, 6765, 10946]
FIBSET = set(FIBS)


def parse_pages():
    with open(DATA) as f:
        raw = f.read()
    pages = [[R2I[ch] for ch in p if ch in R2I] for p in raw.split("%")]
    return [p for p in pages if p][:-2]


def parse_words_sentences():
    """Clean-corpus words and sentence lengths (in words)."""
    with open(DATA) as f:
        raw = f.read()
    # sections 0-9 only
    clean = "$".join(raw.split("$")[:10])
    words: list[list[int]] = []
    sent_lens: list[int] = []
    cur: list[int] = []
    words_in_sent = 0
    for ch in clean:
        if ch in R2I:
            cur.append(R2I[ch])
        elif ch in "-.&%$":
            if cur:
                words.append(cur)
                words_in_sent += 1
                cur = []
            if ch == "." and words_in_sent:
                sent_lens.append(words_in_sent)
                words_in_sent = 0
    if cur:
        words.append(cur)
        words_in_sent += 1
    if words_in_sent:
        sent_lens.append(words_in_sent)
    return words, sent_lens


def load_ll():
    uni: collections.Counter = collections.Counter()
    with open("src/aldegonde/data/ngrams/runeglish/unigrams.txt") as f:
        for line in f:
            g, c = line.split()
            uni[R2I[g.replace("ᛂ", "ᛄ")]] += int(c)
    tot = sum(uni.values())
    return np.array([math.log((uni[i] + 1) / tot) for i in range(N)])


def ll_z(seq: np.ndarray, ll: np.ndarray) -> float:
    mu, sd = float(ll.mean()), float(ll.std())
    return (float(ll[seq].sum()) - len(seq) * mu) / (sd * math.sqrt(len(seq)))


def ioc29(seq: np.ndarray) -> float:
    if len(seq) < 2:
        return 0.0
    _, counts = np.unique(seq, return_counts=True)
    return float((counts * (counts - 1)).sum()
                 / (len(seq) * (len(seq) - 1)) * N)


def main() -> None:
    rng = np.random.default_rng(20260707)
    pyrng = random.Random(20260707)
    pages = parse_pages()
    corpus = np.array([r for p in pages for r in p], dtype=np.int64)
    n = len(corpus)
    ll = load_ll()

    # ---------------------------------------------------- A. extraction
    print("=== A. runes at Fibonacci positions ===")
    with open(DATA) as f:
        raw = f.read()
    sec_streams = [np.array([R2I[c] for c in s if c in R2I], dtype=np.int64)
                   for s in raw.split("$")[:10]]
    sec_streams = [s for s in sec_streams if len(s)]
    units = {"corpus": [corpus], "page": [np.array(p) for p in pages],
             "section": sec_streams}
    for base in (0, 1):
        for uname, streams in units.items():
            pooled = np.concatenate(
                [s[[f - base for f in FIBS if f - base < len(s)]]
                 for s in streams])
            # null: same number of random positions from each stream
            zs = []
            for _ in range(400):
                sim = np.concatenate([
                    s[rng.integers(0, len(s),
                                   size=sum(1 for f in FIBS
                                            if f - base < len(s)))]
                    for s in streams])
                zs.append(ll_z(sim, ll))
            obs = ll_z(pooled, ll)
            zs = np.array(zs)
            print(f"  {uname}-aligned, {base}-indexed: {len(pooled)} runes, "
                  f"LL z={obs:+.2f} (null {zs.mean():+.2f}±{zs.std():.2f}), "
                  f"nIoC={ioc29(pooled):.3f}")
            if uname == "corpus":
                print("    runes: " + " ".join(RUNES[c] for c in pooled))

    # ------------------------------------------- B. gap membership tests
    print("\n=== B. Fibonacci membership of gaps ===")
    import json
    with open("hypotheses/lag5-event-catalog.json") as f:
        cat = json.load(f)
    doublets = cat["doublets"]
    events = sorted(cat["d1_events"] + cat["d4_events"])

    def gap_test(positions: list[int], label: str, mingap: int) -> None:
        """Fibonacci(>=8) membership of gaps, null conditioned on the
        known minimum gap (the doublet dead time would otherwise fake a
        deficit by excluding Fibonacci 1/2/3/5 automatically)."""
        big_fib = {f for f in FIBSET if f >= 8}
        gaps = [b - a for a, b in zip(positions, positions[1:])]
        obs = sum(1 for g in gaps if g in big_fib)
        k = len(positions)
        sims: list[int] = []
        while len(sims) < 4000:
            pos = sorted(pyrng.sample(range(n), k))
            gs = [b - a for a, b in zip(pos, pos[1:])]
            if min(gs) < mingap:
                continue
            sims.append(sum(1 for g in gs if g in big_fib))
        arr = np.array(sims)
        p_hi = (np.sum(arr >= obs) + 1) / (len(arr) + 1)
        p_lo = (np.sum(arr <= obs) + 1) / (len(arr) + 1)
        print(f"  {label}: {obs}/{len(gaps)} Fibonacci(>=8) gaps "
              f"(min-gap-{mingap} null {arr.mean():.2f}±{arr.std():.2f}, "
              f"P(>=)={p_hi:.3f}, P(<=)={p_lo:.3f})")

    gap_test(doublets, "doublet gaps", 6)
    gap_test(events, "lag-5 event gaps", 1)

    # --------------------------------------- C. word / sentence lengths
    print("\n=== C. Fibonacci lengths ===")
    words, sent_lens = parse_words_sentences()
    fib_small = {1, 2, 3, 5, 8, 13, 21, 34}
    frac_lp = sum(1 for w in words if len(w) in fib_small) / len(words)
    # control: solved-section words from the master transcription
    with open(MASTER) as f:
        m = f.read()
    solved_secs = [0, 2, 3, 4, 6, 18]
    ctrl_words = []
    for i, sec in enumerate(m.split("$")):
        if i not in solved_secs:
            continue
        cur = 0
        for ch in sec:
            if ch in R2I or ch == "ᛂ":
                cur += 1
            elif ch in "-.&" and cur:
                ctrl_words.append(cur)
                cur = 0
        if cur:
            ctrl_words.append(cur)
    frac_ctrl = sum(1 for length in ctrl_words
                    if length in fib_small) / len(ctrl_words)
    se = math.sqrt(frac_lp * (1 - frac_lp) / len(words)
                   + frac_ctrl * (1 - frac_ctrl) / len(ctrl_words))
    print(f"  word lengths Fibonacci: LP {frac_lp:.3f} "
          f"({len(words)} words) vs solved control {frac_ctrl:.3f} "
          f"({len(ctrl_words)} words); diff z = "
          f"{(frac_lp - frac_ctrl) / se:+.2f}")
    fs = sum(1 for s in sent_lens if s in fib_small)
    # null: perturb each length by +/-1 with prob 1/2 (local smoothness null)
    sims = []
    for _ in range(4000):
        sims.append(sum(1 for s in sent_lens
                        if s + pyrng.choice((-1, 0, 1)) in fib_small))
    sims = np.array(sims)
    print(f"  sentence lengths (words): {fs}/{len(sent_lens)} Fibonacci "
          f"(smoothness null {sims.mean():.1f}±{sims.std():.1f}, "
          f"z={(fs - sims.mean()) / sims.std():+.2f})")

    # ------------------------- D. boundaries at Fibonacci page positions
    print("\n=== D. word boundaries at Fibonacci rune positions of pages ===")
    with open(DATA) as f:
        raw = f.read()
    page_words: list[list[int]] = [[]]
    cur = 0
    for ch in raw:
        if ch in R2I:
            cur += 1
        elif ch in "-.&$" and cur:
            page_words[-1].append(cur)
            cur = 0
        elif ch == "%":
            if cur:
                page_words[-1].append(cur)
                cur = 0
            page_words.append([])
    page_words = [p for p in page_words if p][:-2]
    obs = 0
    for pw in page_words:
        acc = 0
        for length in pw:
            acc += length
            if acc in FIBSET:
                obs += 1
    sims = []
    for _ in range(2000):
        tot = 0
        for pw in page_words:
            ls = pw[:]
            pyrng.shuffle(ls)
            acc = 0
            for length in ls:
                acc += length
                if acc in FIBSET:
                    tot += 1
        sims.append(tot)
    sims = np.array(sims)
    print(f"  boundaries at Fibonacci positions: {obs} "
          f"(shuffle null {sims.mean():.1f}±{sims.std():.1f}, "
          f"z={(obs - sims.mean()) / sims.std():+.2f})")

    # ------------------------------- E. Fibonacci-interrupt key attacks
    print("\n=== E. keystreams with Fibonacci-position interrupts ===")
    pr = []
    is_c = bytearray(300000)
    for i in range(2, 300000):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, 300000, i):
                is_c[j] = 1
    mx = 30000
    fib_seq = [1, 1]
    while len(fib_seq) < mx:
        fib_seq.append((fib_seq[-1] + fib_seq[-2]) % N)
    streams = {
        "primes": np.array(pr[:mx]) % N,
        "totient": (np.array(pr[:mx]) - 1) % N,
        "index": np.arange(mx) % N,
        "fib": np.array(fib_seq[:mx]),
    }
    mu, sd = float(ll.mean()), float(ll.std())
    results = []
    for mode in ("skip", "restart"):
        for name, k in streams.items():
            for sign in (-1, 1):
                best = (-99.0, -1)
                for pj, page in enumerate(pages):
                    ki = 0
                    dec = []
                    for t, cr in enumerate(page):
                        if (t + 1) in FIBSET:
                            ki = 0 if mode == "restart" else ki + 1
                        dec.append((cr + sign * int(k[ki])) % N)
                        ki += 1
                    z = ((float(ll[np.array(dec)].sum()) - len(dec) * mu)
                         / (sd * math.sqrt(len(dec))))
                    if z > best[0]:
                        best = (z, pj)
                results.append((best[0], mode, name, sign, best[1]))
    results.sort(reverse=True)
    n_tests = 2 * len(streams) * 2 * len(pages)
    print(f"  ({n_tests} page-tests; threshold ~4.2)")
    for z, mode, name, sign, pj in results[:6]:
        print(f"  z={z:+5.2f} mode={mode:8s} {name} "
              f"{'-' if sign < 0 else '+'} page {pj}")


if __name__ == "__main__":
    main()
