# ABOUTME: Tests whether the body looks like it was enciphered with keyword-mixed
# ABOUTME: alphabets, which the 38-bit costing assumes, and finds it looks free instead.
"""The 38-bit costing rests on keyword-derived permutations. Those are visible.

`how-big-is-the-key-really.md` costs the search at 38 bits by assuming sigma and base_0
are keyword-mixed alphabets rather than free permutations, on the grounds that the
author's solved pages use DIVINITY and FIRFUMFERENFE. That assumption is load-bearing and
was recorded as untested.

It is testable. A keyword-mixed alphabet -- the keyword's runes first, then the rest in
alphabet order -- is nothing like a random permutation: most of it is a long run in order.
Composed into the walk, that correlation survives into the ciphertext as residual
structure, and several battery cells see it.

One distinction matters and cuts against the assumption before any test. The author's
demonstrated habit is keyword KEYSTREAMS -- DIVINITY repeating with period 8 -- not
keyword-mixed ALPHABETS. The walk needs permutations, so "he uses keywords" was already a
leap from one kind of object to another.

    python is_the_key_keyword_built.py [--keys 30]
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

CELLS = ("ioc", "entropy", "bigram_chi2", "d4w", "clock")


def keyword_alphabet(word) -> list[int]:
    """The classic mixed alphabet: keyword runes first, then the rest in order."""
    seen: list[int] = []
    for r in word:
        if r not in seen:
            seen.append(r)
    return seen + [x for x in range(M) if x not in seen]


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
    keys = 30
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
    for label in ("keyword", "free"):
        rows = []
        for t in range(keys):
            g = order5_fixing(rk.sample(range(M), 4), rk)
            if label == "keyword":
                sigma = keyword_alphabet(keywords[rk.randrange(len(keywords))])
                base = keyword_alphabet(keywords[rk.randrange(len(keywords))])
            else:
                sigma = rk.sample(range(M), M)
                base = rk.sample(range(M), M)
            rows.append(
                fingerprint(walk(g, sigma, base, corpora[t], random.Random(50 + t)))
            )
        arms[label] = {k: np.array([r[k] for r in rows], float) for k in CELLS}

    body = fingerprint(lp_words())
    print(f"{len(keywords):,} usable keywords, {keys} keys per arm\n")
    print(f"{'cell':<14}{'body':>11}{'keyword-built':>23}{'z':>7}"
          f"{'free permutations':>23}{'z':>7}")
    zk, zf = [], []
    for k in CELLS:
        a, b = arms["keyword"][k], arms["free"][k]
        za, zb = (body[k] - a.mean()) / a.std(), (body[k] - b.mean()) / b.std()
        zk.append(za)
        zf.append(zb)
        print(f"{k:<14}{body[k]:>11.4f}{f'{a.mean():.4f} +- {a.std():.4f}':>23}"
              f"{za:>7.2f}{f'{b.mean():.4f} +- {b.std():.4f}':>23}{zb:>7.2f}")
    zk, zf = np.array(zk), np.array(zf)
    print(f"\nmean |z| against keyword-built {np.abs(zk).mean():.2f}, "
          f"against free {np.abs(zf).mean():.2f}")

    free = arms["free"]
    target = float(np.abs(zf).mean())
    hits = 0
    for i in range(keys):
        d = np.mean([
            abs((arms["keyword"][k][i] - free[k].mean()) / free[k].std())
            for k in CELLS
        ])
        if d <= target:
            hits += 1
    print(f"\nkeyword-built corpora that look as free-like as the body: "
          f"{hits} of {keys}  (P = {hits / keys:.3f})")
    print(
        "\nA keyword-mixed alphabet is mostly a long run in alphabet order, so base o g^k"
        "\nmaps many runes in a correlated way and the ciphertext keeps residual"
        "\nstructure -- higher IoC, higher off-diagonal bigram chi2, lower entropy. The"
        "\nbody is flat and sits on the free arm."
        "\n\nWhat this excludes is the SIMPLEST keyword construction. A columnar-mixed or"
        "\nreversed-rest alphabet is flatter and is untouched. And the author's actual"
        "\nhabit -- a repeating keyword KEYSTREAM -- is not a permutation at all, so the"
        "\nevidence for the assumption was weaker than it looked."
    )


if __name__ == "__main__":
    main()
