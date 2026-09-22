# ABOUTME: Measures how far each small-description key construction sits from a free
# ABOUTME: permutation, and finds only the classic keyword alphabet is visible at all.
"""If the key has a short description, does the ciphertext show it?

`is_the_key_keyword_built.py` finds the body disfavours a classic keyword-mixed alphabet
at P = 0.033, which bears on the 38-bit costing in `how-big-is-the-key-really.md`. But
"keyword alphabet" is one construction among several, and the costing only needs the key
to have SOME short description.

So measure them all. Six ways to build sigma and base_0, thirty keys each, scored on the
battery cells that saw the keyword construction: IoC, entropy, off-diagonal bigram chi2,
the clock reading, d3 and d4.

Two questions, and they need different tests.

  how visible   how far does each construction's centre sit from the free-permutation
                arm, in that arm's own units
  is it the body  among a construction's own corpora, how many look as free-like as the
                body does -- a directional test against the alternative

A distance from a construction's OWN centre answers neither: the arms overlap heavily and
the body sits near the middle of every one of them, which is reported here so the
mistake is not repeated.

    python which_key_constructions_are_visible.py [--keys 40]
"""

from __future__ import annotations

import collections
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import (  # noqa: E402
    M,
    compose,
    fingerprint,
    lp_words,
    ppow,
    prose_corpora,
)

CELLS = ("ioc", "entropy", "bigram_chi2", "clock", "d3w", "d4w")
KINDS = ("random", "keyword", "keyword-rev", "columnar", "affine", "shift")


def dedup(word):
    seen = []
    for r in word:
        if r not in seen:
            seen.append(r)
    return seen


def build(kind: str, word, rng) -> list[int]:
    if kind == "shift":
        k = rng.randrange(1, M)
        return [(i + k) % M for i in range(M)]
    if kind == "affine":
        a = rng.choice([x for x in range(1, M) if np.gcd(x, M) == 1])
        b = rng.randrange(M)
        return [(a * i + b) % M for i in range(M)]
    seen = dedup(word)
    rest = [x for x in range(M) if x not in seen]
    if kind == "keyword":
        return seen + rest
    if kind == "keyword-rev":
        return seen + rest[::-1]
    if kind == "columnar":
        full = seen + rest
        w = len(seen)
        rows = [full[i : i + w] for i in range(0, len(full), w)]
        order = sorted(range(w), key=lambda j: seen[j])
        return [r[j] for j in order for r in rows if j < len(r)]
    return rng.sample(range(M), M)


def walk(g, sigma, base, plain, rng, phi: float = 0.9):
    gp = [ppow(g, i) for i in range(5)]
    b = list(base)
    out, clock, prev = [], 0, None
    for word in plain:
        cw = []
        for p in word:
            c = b[gp[clock % 5][p]]
            if c == prev and rng.random() < phi:
                clock += 1
                c = b[gp[clock % 5][p]]
            cw.append(c)
            prev = c
            clock += 1
        out.append(cw)
        b = compose(b, compose(gp[(clock - 1) % 5], sigma))
    return out


def main() -> None:
    keys = 40
    for i, a in enumerate(sys.argv):
        if a == "--keys" and i + 1 < len(sys.argv):
            keys = int(sys.argv[i + 1])

    vocab = collections.Counter()
    for c in prose_corpora(2928, 20):
        for w in c:
            vocab[tuple(w)] += 1
    keywords = [list(w) for w in vocab
                if len(set(w)) == len(w) and 4 <= len(w) <= 10]
    corpora = list(prose_corpora(2928, keys))
    rk = random.Random(3)

    arms = {}
    for kind in KINDS:
        rows = []
        for t in range(keys):
            g = order5_fixing(rk.sample(range(M), 4), rk)
            sigma = build(kind, keywords[rk.randrange(len(keywords))], rk)
            base = build(kind, keywords[rk.randrange(len(keywords))], rk)
            if len(set(sigma)) != M or len(set(base)) != M:
                continue
            rows.append(
                fingerprint(walk(g, sigma, base, corpora[t], random.Random(50 + t)))
            )
        arms[kind] = np.array([[r[k] for k in CELLS] for r in rows], float)

    body = np.array([fingerprint(lp_words())[k] for k in CELLS], float)
    free = arms["random"]
    fmu, fsd = free.mean(0), free.std(0, ddof=1)
    body_free = float(np.abs((body - fmu) / fsd).mean())

    print(f"{'construction':<16}{'n':>4}{'distance from free':>21}"
          f"{'as free-like as the body':>27}")
    for kind, A in arms.items():
        dist = float(np.abs((A.mean(0) - fmu) / fsd).mean())
        per = np.abs((A - fmu) / fsd).mean(axis=1)
        p = float((per <= body_free).mean())
        print(f"{kind:<16}{len(A):>4}{dist:>21.2f}{f'{p:.3f}':>27}")
    print(f"\nthe body's own mean |z| against the free arm: {body_free:.2f}")
    print(
        "\nThe random row is the control the statistic needs: it says how often a corpus"
        "\nGENUINELY from the free arm looks as free-like as the body. A construction is"
        "\nonly disfavoured insofar as its figure falls below that one."
    )

    print("\n\nthe test that does NOT work, recorded so it is not repeated:\n")
    print(f"{'construction':<16}{'body mean |z|':>15}{'its own members':>20}{'P':>8}")
    for kind, A in arms.items():
        mu, sd = A.mean(0), A.std(0, ddof=1)
        bz = float(np.abs((body - mu) / sd).mean())
        own = []
        for i in range(len(A)):
            o = np.delete(A, i, 0)
            own.append(float(np.abs((A[i] - o.mean(0)) / o.std(0, ddof=1)).mean()))
        own = np.array(own)
        print(f"{kind:<16}{bz:>15.2f}{f'{own.mean():.2f} +- {own.std():.2f}':>20}"
              f"{float((own >= bz).mean()):>8.3f}")
    print(
        "\nThe body is an ordinary member of every arm at P above 0.92. That is not"
        "\nevidence for any of them: a distance from an arm's own centre asks whether the"
        "\nbody is typical, and with arms this broad everything is. Asking which arm the"
        "\nbody came from needs a statistic pointed at the ALTERNATIVE, which the first"
        "\ntable uses."
        "\n\nThe result is that only the classic keyword alphabet is visible at all. The"
        "\nother four sit within a third of a sigma of free permutations, so the battery"
        "\ncannot rule them in or out, and the costing's premise -- that the key has SOME"
        "\nshort description -- survives everything except its simplest form."
        "\n\nAffine is excluded anyway by C1, on the 2-transitivity of the base family."
    )


if __name__ == "__main__":
    main()
