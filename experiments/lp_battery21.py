#!/usr/bin/env python3
"""Battery 21: seeded conventional PRNGs as the keystream generator.

"There must be a generator" — agreed that nothing observed requires true
randomness: the base stream only needs to be statistically flat at
12,956 runes, which any conventional PRNG achieves. What has never been
swept is the class a crypto-literate 2014 designer would actually use:
standard generators seeded with Cicada-meaningful constants.

Generators:
    lcg-glibc      x -> (1103515245 x + 12345) mod 2^31
    lcg-minstd     x -> 16807 x mod (2^31 - 1)
    lcg-randu      x -> 65539 x mod 2^31
    lcg-nr         x -> (1664525 x + 1013904223) mod 2^32
    xorshift32     Marsaglia 13/17/5
    mt19937        Python random.Random(seed).randrange(29)
    sha256-ctr     bytes of SHA256(seed || counter), rejection-debiased
    rc4            RC4 keystream bytes, rejection-debiased

Seeds: the Cicada numerology set (3301, 1033, 761, 509, 113, 29, 7, 2,
59, 167, 6395, 1279, 3301*1033, ...) for integer generators; the same
plus obvious passphrases (CICADA, CICADA3301, LIBERPRIMUS, PRIMUS,
INSTAR, DIVINITY, FIRFUMFERENFE, PARABLE, TOTIENT, EMERGENCE) for
byte-keyed ones.

Reduction to runes: direct mod 29 for word generators (bias < 1e-8 for
32-bit words); rejection-debiased byte mod 29 for byte generators.

Each keystream is tested corpus-wide (continuous) and per-page
(restarting the generator at each page), both signs, in two alignment
modes: strict, and nulls (the catalog's paired-event copy targets
consume no key symbol). Runeglish unigram-LL z-scored; the family is
~50k page-tests, so the discovery threshold is z ~ 4.8.

Usage: python experiments/lp_battery21.py
"""

from __future__ import annotations

import collections
import hashlib
import json
import math
import random

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
N = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
CATALOG = "hypotheses/lag5-event-catalog.json"

INT_SEEDS = [1, 2, 5, 7, 29, 59, 113, 167, 509, 761, 1033, 1279, 3301,
             6395, 1595277641, 3301 * 1033, 33011033, 20140105]
STR_SEEDS = [b"3301", b"1033", b"CICADA", b"CICADA3301", b"LIBERPRIMUS",
             b"PRIMUS", b"INSTAR", b"DIVINITY", b"FIRFUMFERENFE",
             b"PARABLE", b"TOTIENT", b"EMERGENCE", b"AN END",
             b"INSTAR EMERGENCE", b"SHED OUR CIRCUMFERENCES"]


# ------------------------------------------------------------- generators
def lcg(a: int, c: int, m: int, seed: int, n: int) -> np.ndarray:
    x = seed % m or 1
    out = np.empty(n, dtype=np.int64)
    for i in range(n):
        x = (a * x + c) % m
        out[i] = x % N
    return out


def xorshift32(seed: int, n: int) -> np.ndarray:
    x = seed & 0xFFFFFFFF or 1
    out = np.empty(n, dtype=np.int64)
    for i in range(n):
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        out[i] = x % N
    return out


def mt19937(seed: int, n: int) -> np.ndarray:
    rng = random.Random(seed)
    return np.array([rng.randrange(N) for _ in range(n)], dtype=np.int64)


def sha256_ctr(seed: bytes, n: int) -> np.ndarray:
    out: list[int] = []
    ctr = 0
    while len(out) < n:
        block = hashlib.sha256(seed + ctr.to_bytes(8, "big")).digest()
        for b in block:
            if b < 232:  # rejection-debias: 232 = 8 * 29
                out.append(b % N)
                if len(out) == n:
                    break
        ctr += 1
    return np.array(out, dtype=np.int64)


def rc4(key: bytes, n: int) -> np.ndarray:
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) % 256
        s[i], s[j] = s[j], s[i]
    out: list[int] = []
    i = j = 0
    while len(out) < n:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        b = s[(s[i] + s[j]) % 256]
        if b < 232:
            out.append(b % N)
    return np.array(out, dtype=np.int64)


def all_streams(n: int):
    for seed in INT_SEEDS:
        yield f"lcg-glibc[{seed}]", lcg(1103515245, 12345, 2 ** 31, seed, n)
        yield f"lcg-minstd[{seed}]", lcg(16807, 0, 2 ** 31 - 1, seed, n)
        yield f"lcg-randu[{seed}]", lcg(65539, 0, 2 ** 31, seed, n)
        yield f"lcg-nr[{seed}]", lcg(1664525, 1013904223, 2 ** 32, seed, n)
        yield f"xorshift32[{seed}]", xorshift32(seed, n)
        yield f"mt19937[{seed}]", mt19937(seed, n)
    for seed in STR_SEEDS:
        label = seed.decode()
        yield f"sha256[{label}]", sha256_ctr(seed, n)
        yield f"rc4[{label}]", rc4(seed, n)
        yield f"mt19937[{label}]", mt19937(int.from_bytes(
            hashlib.sha256(seed).digest()[:8], "big"), n)


# ---------------------------------------------------------------- corpus
def load_pages() -> list[list[int]]:
    with open(DATA) as f:
        raw = f.read()
    pages = [[R2I[ch] for ch in p if ch in R2I] for p in raw.split("%")]
    return [p for p in pages if p][:-2]


def load_ll() -> np.ndarray:
    uni: collections.Counter = collections.Counter()
    with open("src/aldegonde/data/ngrams/runeglish/unigrams.txt") as f:
        for line in f:
            g, cnt = line.split()
            uni[R2I[g.replace("ᛂ", "ᛄ")]] += int(cnt)
    tot = sum(uni.values())
    return np.array([math.log((uni[i] + 1) / tot) for i in range(N)])


def main() -> None:
    pages = load_pages()
    lens = [len(p) for p in pages]
    corpus = np.array([r for p in pages for r in p], dtype=np.int64)
    n = len(corpus)
    starts = np.cumsum([0] + lens[:-1])
    ll = load_ll()
    mu, sd = float(ll.mean()), float(ll.std())

    with open(CATALOG) as f:
        cat = json.load(f)
    nulls: set[int] = set()
    for i in cat["d1_events"]:
        nulls.update((i + 5, i + 6))
    for i in cat["d4_events"]:
        nulls.update((i + 5, i + 9))
    keep_strict = np.ones(n, dtype=bool)
    keep_nulls = np.array([i not in nulls for i in range(n)])

    def z_of(dec: np.ndarray) -> float:
        return ((float(ll[dec].sum()) - len(dec) * mu)
                / (sd * math.sqrt(len(dec))))

    best_corpus: list[tuple] = []
    best_page: list[tuple] = []
    count = 0
    for name, k in all_streams(n):
        count += 1
        for mode, keep in (("strict", keep_strict), ("nulls", keep_nulls)):
            cs = corpus[keep]
            key = k[: len(cs)]
            for sign in (-1, 1):
                best_corpus.append((z_of((cs + sign * key) % N),
                                    name, mode, sign))
            # per-page: generator restarts each page
            for sign in (-1, 1):
                zbest = (-99.0, -1)
                for pj, (st, ln) in enumerate(zip(starts, lens)):
                    idx = [st + t for t in range(ln)
                           if keep[st + t]]
                    cs_p = corpus[idx]
                    dec = (cs_p + sign * k[: len(cs_p)]) % N
                    zz = z_of(dec)
                    if zz > zbest[0]:
                        zbest = (zz, pj)
                best_page.append((zbest[0], name, mode, sign, zbest[1]))

    n_page_tests = count * 2 * 2 * len(pages)
    best_corpus.sort(reverse=True)
    best_page.sort(reverse=True)
    print(f"{count} keystreams tested; {n_page_tests} page-tests "
          f"(threshold ~4.8) plus {count*4} corpus-tests\n")
    print("top corpus-wide:")
    for zz, name, mode, sign in best_corpus[:6]:
        print(f"  z={zz:+5.2f} {name:>28} {mode:6s} "
              f"{'-' if sign < 0 else '+'}")
    print("top per-page:")
    for zz, name, mode, sign, pj in best_page[:8]:
        print(f"  z={zz:+5.2f} {name:>28} {mode:6s} "
              f"{'-' if sign < 0 else '+'} page {pj}")


if __name__ == "__main__":
    main()
