#!/usr/bin/env python3
"""Battery 19: null-deletion conditional key search.

Under the nulls branch of copy semantics (`lag5-back-reference.md`), the
copied glyph at a lag-5 event is padding: on decryption it is SKIPPED and
consumes NO key symbol. Every earlier keystream sweep (batteries 9/13/14)
assumed one key symbol per ciphertext rune, so if the true scheme is
"simple keystream + inserted null copies", those sweeps were mis-aligned
after the first null and would have missed it. The event catalog
(hypotheses/lag5-event-catalog.json) lets us close that loophole
deterministically.

Deletion modes (which ciphertext positions are treated as nulls):

    none    : baseline (= battery 13 mode "none")
    paired  : the copy TARGETS of the 29 d1 + 28 d4 events
              (positions i+5 / {i+5, i+6} / {i+5, i+9}); ~103 glyphs
    matches : the targets of ALL 479 lag-5 matches (aggressive upper
              bound; most are chance, so this mostly tests robustness)

For each mode x 9 streams x both signs: decrypt with key advancing only
on non-null glyphs, score non-null plaintext with runeglish unigram LL,
z-scored per page (key restarts each page) and corpus-wide (continuous
key). The multiple-test threshold for the per-page family is ~4.5.

Note the honest limitation: only ~40% of paired-event glyphs are real
copies under the calibrated budget (the rest are chance matches), so
even the "paired" mode has residual alignment error late in long pages;
per-page restarts keep the damage bounded (pages have 0-4 events).

Usage: python experiments/lp_battery19.py
"""

from __future__ import annotations

import collections
import json
import math

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
N = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
CATALOG = "hypotheses/lag5-event-catalog.json"
D = 5


def load_pages() -> list[list[int]]:
    with open(DATA) as f:
        raw = f.read()
    pages = [[R2I[ch] for ch in page if ch in R2I]
             for page in raw.split("%")]
    return [p for p in pages if p][:-2]


def sieve(limit: int) -> list[int]:
    pr: list[int] = []
    is_c = bytearray(limit)
    for i in range(2, limit):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, limit, i):
                is_c[j] = 1
    return pr


def build_streams(mx: int) -> dict[str, np.ndarray]:
    pr = sieve(400000)
    pi = ("1415926535897932384626433832795028841971693993751058209749445923"
          "0781640628620899862803482534211706798214808651328230664709384460"
          "9550582231725359408128481117450284102701938521105559644622948954"
          "9303819644288109756659334461284756482337867831652712019091456485")
    e_ = ("2718281828459045235360287471352662497757247093699959574966967627"
          "7240766303535475945713821785251664274274663919320030599218174135"
          "9662904357290033429526059563073813232862794349076323382988075319"
          "5251019011573834187930702154089149934884167092447614606680822648")
    fib = [1, 1]
    while len(fib) < mx:
        fib.append((fib[-1] + fib[-2]) % N)
    lucas = [2, 1]
    while len(lucas) < mx:
        lucas.append((lucas[-1] + lucas[-2]) % N)
    return {
        "primes": np.array(pr[:mx]) % N,
        "totient": (np.array(pr[:mx]) - 1) % N,
        "index": np.arange(mx) % N,
        "tri": np.array([i * (i + 1) // 2 for i in range(mx)]) % N,
        "fib": np.array(fib[:mx]) % N,
        "lucas": np.array(lucas[:mx]) % N,
        "pi": np.array([int(c) for c in pi * (mx // len(pi) + 1)][:mx]),
        "e": np.array([int(c) for c in e_ * (mx // len(e_) + 1)][:mx]),
        "2^i": np.array([pow(2, i, N) for i in range(mx)]),
    }


def load_ll() -> np.ndarray:
    uni: collections.Counter = collections.Counter()
    with open("src/aldegonde/data/ngrams/runeglish/unigrams.txt") as f:
        for line in f:
            g, c = line.split()
            uni[R2I[g.replace("ᛂ", "ᛄ")]] += int(c)
    tot = sum(uni.values())
    return np.array([math.log((uni[i] + 1) / tot) for i in range(N)])


def null_sets(n_total: int) -> dict[str, set[int]]:
    with open(CATALOG) as f:
        cat = json.load(f)
    paired: set[int] = set()
    for i in cat["d1_events"]:
        paired.update((i + D, i + D + 1))
    for i in cat["d4_events"]:
        paired.update((i + D, i + D + 4))
    all_targets = {m["i"] + D for m in cat["matches"]}
    assert max(paired) < n_total
    return {"none": set(), "paired": paired, "matches": all_targets}


def main() -> None:
    pages = load_pages()
    lens = [len(p) for p in pages]
    corpus = np.array([r for p in pages for r in p], dtype=np.int64)
    n = len(corpus)
    print(f"{len(pages)} pages, {n} runes")

    ll = load_ll()
    mu, sd = float(ll.mean()), float(ll.std())
    streams = build_streams(n + 600)
    modes = null_sets(n)

    # page start offsets in corpus coordinates
    starts = np.cumsum([0] + lens[:-1])

    def score(dec: np.ndarray) -> float:
        g = float(ll[dec].sum())
        return (g - len(dec) * mu) / (sd * math.sqrt(len(dec)))

    print("\n=== corpus-wide (continuous key), all modes ===")
    rows = []
    for mode, nulls in modes.items():
        keep = np.array([i not in nulls for i in range(n)])
        cs = corpus[keep]
        for name, k in streams.items():
            key = k[: len(cs)]
            for sign in (-1, 1):
                rows.append((score((cs + sign * key) % N),
                             mode, name, sign))
    rows.sort(reverse=True)
    for zz, mode, name, sign in rows[:8]:
        print(f"  z={zz:+5.2f} mode={mode:8s} {name} "
              f"{'-' if sign < 0 else '+'}")

    print("\n=== per-page (key restarts each page) ===")
    results = []
    for mode, nulls in modes.items():
        for name, k in streams.items():
            for sign in (-1, 1):
                zs = []
                for pj, (st, ln) in enumerate(zip(starts, lens)):
                    idx = [st + t for t in range(ln)
                           if st + t not in nulls]
                    cs = corpus[idx]
                    dec = (cs + sign * k[: len(cs)]) % N
                    zs.append((score(dec), pj))
                zs.sort(reverse=True)
                results.append((zs[0][0], mode, name, sign, zs[:3]))
    results.sort(reverse=True)
    n_tests = len(modes) * len(streams) * 2 * len(pages)
    print(f"  ({n_tests} page-tests; multiple-test threshold ~4.5)")
    for zz, mode, name, sign, top in results[:10]:
        print(f"  max page z={zz:+5.2f} mode={mode:8s} {name} "
              f"{'-' if sign < 0 else '+'} "
              f"top {[(round(a, 2), b) for a, b in top]}")

    # ---------------- per-page keystream OFFSET brute force with deletion
    # battery 14 redone under the nulls branch: each trial z-scored against
    # its own per-(page, stream, sign) offset distribution, so the report
    # is the max over ~33M trials; the battery-14 noise ceiling for that
    # family was ~5.5.
    from numpy.lib.stride_tricks import sliding_window_view

    n_off = 25000
    big = build_streams(n_off + 300)
    offset_streams = {k: big[k] for k in
                      ("primes", "totient", "pi", "e", "tri", "fib")}
    print("\n=== per-page offset brute force (offsets 0..24999) ===")
    grand = []
    for mode in ("none", "paired"):
        nulls = modes[mode]
        for name, k in offset_streams.items():
            for sign in (-1, 1):
                best_here = []
                for pj, (st, ln) in enumerate(zip(starts, lens)):
                    idx = [st + t for t in range(ln)
                           if st + t not in nulls]
                    cs = corpus[idx]
                    w = sliding_window_view(k[: n_off + len(cs)], len(cs))[
                        :n_off]
                    dec = (cs[None, :] + sign * w) % N
                    sums = ll[dec].sum(axis=1)
                    zz = (sums - sums.mean()) / sums.std()
                    o = int(np.argmax(zz))
                    best_here.append((float(zz[o]), pj, o))
                best_here.sort(reverse=True)
                grand.append((best_here[0], mode, name, sign))
    grand.sort(reverse=True)
    print(f"  ({2 * 6 * 2 * len(pages) * n_off / 1e6:.1f}M trials; "
          f"battery-14 noise ceiling for this family ~5.5)")
    for (zz, pj, o), mode, name, sign in grand[:8]:
        print(f"  z={zz:+5.2f} page {pj:>2} offset {o:>5} mode={mode:8s} "
              f"{name} {'-' if sign < 0 else '+'}")


if __name__ == "__main__":
    main()
