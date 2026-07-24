#!/usr/bin/env python3
# ABOUTME: Simulates the length-clocked walk with sigma = g^k versus sigma
# ABOUTME: outside <g>: the five-alphabet collapse leaves census/unigram/kappa
# ABOUTME: signatures the LP corpus does not have (sigma-power-step.md).
"""Is the space step sigma a power of g? Simulation of the kill signatures.

If sigma is in <g> (cyclic, order 5), every per-word base is base0 . g^m:
the cipher uses only five alphabets, scheduled by the word lengths. Two
observable consequences, measured here on a register-plaintext corpus of
LP size for sigma = g^0..g^4, a random mixed sigma, and a near-power
sigma = g^2 . (one transposition):

  1. IDENTITY CENSUS: repeated plaintext words whose bases collide
     (~1/5 of repeated pairs) encrypt identically. LP observed: identity
     pairs at chance (17 vs 10.7 +/- 3.3, word-transform-census.md).
  2. UNIGRAM FLATNESS: a mixture of five permuted English distributions
     is not flat unless the five alphabets are a designed flattening
     quintet. LP observed nIoC 1.000.

Also printed: mono kappa-5 and the period-5 positional Friedman signal
(the sigma = g case collapses to a strict period-5 polyalphabetic).
"""

from __future__ import annotations

import random
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish
from doublet_position_profile import IDX_ENG
from ea_direction_test import PROSE_CACHE, PROSE_URL, prose_words

M = 29
NWORDS = 2928  # LP-sized corpus


def compose(a: list[int], b: list[int]) -> list[int]:
    """(a . b)[i] = a[b[i]]."""
    return [a[x] for x in b]


def random_order5(rng: random.Random) -> list[int]:
    """Rich order-5 permutation: five 5-cycles + 4 fixed points."""
    pts = list(range(M))
    rng.shuffle(pts)
    g = list(range(M))
    for c in range(5):
        cyc = pts[c * 5:(c + 1) * 5]
        for i in range(5):
            g[cyc[i]] = cyc[(i + 1) % 5]
    return g


def encrypt(words: list[list[int]], base0: list[int], g: list[int],
            sigma: list[int]) -> list[list[int]]:
    gpow = [list(range(M))]
    for _ in range(4):
        gpow.append(compose(g, gpow[-1]))
    base = base0[:]
    out = []
    for w in words:
        out.append([base[gpow[j % 5][p]] for j, p in enumerate(w)])
        base = compose(base, compose(gpow[(len(w) - 1) % 5], sigma))
    return out


def identity_pairs(words: list[list[int]]) -> int:
    c = Counter(tuple(w) for w in words if len(w) >= 3)
    return sum(v * (v - 1) // 2 for v in c.values())


def nioc(stream: list[int]) -> float:
    c = Counter(stream)
    n = len(stream)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * M


def kappa(stream: list[int], d: int) -> float:
    n = len(stream) - d
    hits = sum(1 for i in range(n) if stream[i] == stream[i + d])
    return hits / n * M


def friedman5(stream: list[int]) -> float:
    """Mean column nIoC at period 5 (positional)."""
    return sum(nioc(stream[r::5]) for r in range(5)) / 5


def main() -> None:
    rng = random.Random(3301)
    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    if not prose_path.exists():
        print(f"downloading {PROSE_URL} -> {prose_path}")
        urllib.request.urlretrieve(PROSE_URL, prose_path)
    all_words = [[IDX_ENG[t] for t in to_runeglish(w)]
                 for w in prose_words(prose_path)]
    all_words = [w for w in all_words if w]
    start = rng.randrange(len(all_words) - NWORDS)
    words = all_words[start:start + NWORDS]
    pt_pairs = identity_pairs(words)
    n_runes = sum(map(len, words))
    print(f"plaintext: {NWORDS} words, {n_runes} runes, "
          f"{pt_pairs} repeated identical word pairs (len >= 3)")
    print(f"LP reference: identity pairs 17 (chance 10.7 ± 3.3), "
          f"unigram nIoC 1.000, kappa5 1.073, Friedman5 ~1.00\n")

    g = random_order5(rng)
    base0 = list(range(M))
    rng.shuffle(base0)
    gpow = [list(range(M))]
    for _ in range(4):
        gpow.append(compose(g, gpow[-1]))

    sig_rand = list(range(M))
    rng.shuffle(sig_rand)
    near = gpow[2][:]
    a, b = rng.sample(range(M), 2)
    near[a], near[b] = near[b], near[a]

    cases = [(f"sigma = g^{k}", gpow[k]) for k in range(5)]
    cases += [("sigma = g^2 . (a b)", near), ("sigma random mixed", sig_rand)]

    print(f"{'sigma':<22} {'ident pairs':>11} {'pred n/5':>8} "
          f"{'uni nIoC':>9} {'kappa5':>7} {'Fried5':>7}")
    for name, sigma in cases:
        ct = encrypt(words, base0, g, sigma)
        stream = [r for w in ct for r in w]
        print(f"{name:<22} {identity_pairs(ct):>11} {pt_pairs / 5:>8.0f} "
              f"{nioc(stream):>9.3f} {kappa(stream, 5):>7.3f} "
              f"{friedman5(stream):>7.3f}")


if __name__ == "__main__":
    main()
