#!/usr/bin/env python3
"""Battery 23: reroll-aware (drift-tolerant) sweep of the full stream catalog.

The complexity ladder of the solved sections runs constant key ->
repeating word key -> PUBLIC aperiodic mathematical stream (AN END's
prime-1, zero secret material). If the unsolved system is the next rung
— another public stream wrapped in the two rules — then plain
subtraction sweeps (batteries 13/14/19/21) are blind: the doublet
reroll consumes an extra key symbol at ~3.3% of positions
(plaintext-dependent, ~6-8 per page), so even the CORRECT stream
decrypts to garbage shortly after the first reroll. The only search
that can see through the rules is drift-tolerant alignment.

Method: per-page Viterbi over drift states 0..DMAX (a drift step =
one reroll's extra key consumption; prior 4% per position, matching
the measured collision-attempt rate). Emission = runeglish unigram LL
gain. Every page's score is z-scored against an ensemble of RANDOM
keystreams pushed through the identical Viterbi on the same page (so
length and drift-flexibility are exactly controlled).

Streams: the 13 mathematical streams of battery 19 + all 153 seeded
conventional PRNGs of battery 21, both signs. Positive control: the
solved page 55 (totient with ciphertext-triggered skips — a drift
pattern) must produce an extreme z under totient-.

Usage: python experiments/lp_battery23.py
"""

from __future__ import annotations

import collections
import math

import numpy as np
from lp_battery21 import all_streams

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
N = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"

DMAX = 15
SKIP_LP = math.log(0.04)
STAY_LP = math.log(0.96)
NULL_KEYS = 40


def load_pages(*, include_solved: bool = False) -> list[np.ndarray]:
    with open(DATA) as f:
        raw = f.read()
    pages = [np.array([R2I[ch] for ch in p if ch in R2I], dtype=np.int64)
             for p in raw.split("%")]
    pages = [p for p in pages if len(p)]
    return pages if include_solved else pages[:-2]


def load_ll() -> np.ndarray:
    uni: collections.Counter = collections.Counter()
    with open("src/aldegonde/data/ngrams/runeglish/unigrams.txt") as f:
        for line in f:
            g, cnt = line.split()
            uni[R2I[g.replace("ᛂ", "ᛄ")]] += int(cnt)
    tot = sum(uni.values())
    return np.array([math.log((uni[i] + 1) / tot) - math.log(1 / N)
                     for i in range(N)])


def math_streams(mx: int) -> dict[str, np.ndarray]:
    pr = []
    is_c = bytearray(400000)
    for i in range(2, 400000):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, 400000, i):
                is_c[j] = 1
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
        "primes+1": (np.array(pr[:mx]) + 1) % N,
        "index": np.arange(mx) % N,
        "tri": np.array([i * (i + 1) // 2 for i in range(mx)]) % N,
        "fib": np.array(fib[:mx]),
        "lucas": np.array(lucas[:mx]),
        "pi": np.array([int(c) for c in pi * (mx // len(pi) + 1)][:mx]),
        "e": np.array([int(c) for c in e_ * (mx // len(e_) + 1)][:mx]),
        "2^i": np.array([pow(2, i, N) for i in range(mx)]),
        "squares": np.array([i * i for i in range(mx)]) % N,
        "cubes": np.array([i ** 3 for i in range(mx)]) % N,
        "primegap": np.array([pr[i + 1] - pr[i] for i in range(mx)]) % N,
    }


def viterbi(cs: np.ndarray, key: np.ndarray, sign: int,
            llg: np.ndarray) -> float:
    """Best LL gain over drift paths (drift = extra key consumptions)."""
    m = len(cs)
    cur = np.full(DMAX + 1, -1e18)
    cur[0] = 0.0
    drifts = np.arange(DMAX + 1)
    for i in range(m):
        emit = llg[(cs[i] + sign * key[i + drifts]) % N]
        stay = cur + emit + STAY_LP
        skip = np.empty(DMAX + 1)
        skip[0] = -1e18
        emit_shift = llg[(cs[i] + sign * key[i + drifts[1:]]) % N]
        skip[1:] = cur[:-1] + emit_shift + SKIP_LP
        cur = np.maximum(stay, skip)
    return float(cur.max())


def main() -> None:
    rng = np.random.default_rng(20260707)
    pages = load_pages()
    llg = load_ll()
    maxlen = max(len(p) for p in pages) + DMAX + 5

    # per-page null ensembles: random keystreams through the same Viterbi
    print(f"calibrating per-page nulls ({NULL_KEYS} random keys/page)...")
    null_mu, null_sd = [], []
    for pg in pages:
        scores = [viterbi(pg, rng.integers(0, N, len(pg) + DMAX + 2), 1, llg)
                  for _ in range(NULL_KEYS)]
        null_mu.append(float(np.mean(scores)))
        null_sd.append(float(np.std(scores)))

    def sweep(streams) -> list[tuple]:
        results = []
        for name, k in streams:
            if len(k) < maxlen:
                k = np.concatenate([k, np.zeros(maxlen - len(k),
                                                dtype=np.int64)])
            for sign in (-1, 1):
                for pj, pg in enumerate(pages):
                    sc = viterbi(pg, k, sign, llg)
                    z = (sc - null_mu[pj]) / null_sd[pj]
                    results.append((z, name, sign, pj))
        return results

    ms = math_streams(maxlen)
    res = sweep(ms.items())
    n_math = len(res)
    res += sweep(all_streams(maxlen))
    res.sort(reverse=True)
    n_tests = len(res)
    print(f"\n{n_tests} page-tests ({n_math} math + rest PRNG); "
          f"threshold ~{math.sqrt(2 * math.log(n_tests)) + 0.7:.1f}")
    for z, name, sign, pj in res[:10]:
        print(f"  z={z:+5.2f} {name:>28} {'-' if sign < 0 else '+'} "
              f"page {pj}")

    # positive control: solved page 55, totient-, same machinery & null
    p55 = load_pages(include_solved=True)[55]
    scores = [viterbi(p55, rng.integers(0, N, len(p55) + DMAX + 2), 1, llg)
              for _ in range(NULL_KEYS)]
    sc = viterbi(p55, ms["totient"], -1, llg)
    z = (sc - np.mean(scores)) / np.std(scores)
    print(f"\npositive control (solved page 55, totient-): z = {z:+.1f}")


if __name__ == "__main__":
    main()
