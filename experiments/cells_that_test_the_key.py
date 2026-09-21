# ABOUTME: Splits the fingerprint battery's cells into those that test the cipher's shape
# ABOUTME: and those that only test which key was drawn, by varying g as well as the corpus.
"""Every battery run in this directory has held one key and varied the corpus.

That answers "is the corpus a plausible draw from this model with this key". It does not
answer "is the corpus a plausible draw from this model", and the difference has bitten
twice:

  seam/d1w ratio   excluded the whole preventer family, until varying g moved the ratio
                   from 0.52 to 9.77 and the corpus's 1.25 turned out to be ordinary
  returns          scored against every model and missed by all, until the arithmetic
                   showed no unfitted key can produce it at all

Both are the same error in different clothes: a cell whose value is decided by the key was
read as a verdict on the mechanism. This measures the split directly, for all 19 cells at
once.

Draw K keys. Under each, generate D corpora and fingerprint them. Then for every cell:

    within   sd across corpora at one key      -- the spread the battery already uses
    between  sd of the per-key means across K  -- the spread the battery never sees

    key ratio = between / within

A cell with ratio near zero is set by the mechanism: every key agrees, so the corpus
either matches the shape or it does not. A cell with a large ratio is set by the key, and
a miss there says only that this key was the wrong one.

The reachable-informative set is only meaningful if its cells sit on the mechanism side.

    python cells_that_test_the_key.py [--keys 20] [--draws 8]
"""

from __future__ import annotations

import collections
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import generator as dodge_generator, order5_fixing  # noqa: E402
from fingerprint_battery import (  # noqa: E402
    M,
    compose,
    fingerprint,
    lp_words,
    ppow,
    prose_corpora,
)
from probabilistic_preventer import preventer as prob_preventer  # noqa: E402
from substitution_preventer import preventer as sub_preventer, tau_fixing  # noqa: E402

REACHABLE = ("d1w", "seam", "doublet_gap_min", "d6w")


def main() -> None:
    keys, draws = 20, 8
    for i, a in enumerate(sys.argv):
        if a == "--keys" and i + 1 < len(sys.argv):
            keys = int(sys.argv[i + 1])
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lp = fingerprint(lp_words())
    corpora = list(prose_corpora(2928, draws))
    rng = random.Random(99)

    per_key: list[dict[str, np.ndarray]] = []
    for _ in range(keys):
        g = order5_fixing(rng.sample(range(M), 4), rng)
        sigma = rng.sample(range(M), M)
        tau = tau_fixing(rng.sample(range(M), 8), rng)
        gen = sub_preventer(g, sigma, tau)
        r = random.Random(3301)
        sims = [fingerprint(gen(p, r)) for p in corpora]
        per_key.append({k: np.array([s[k] for s in sims], float) for k in lp})

    print(f"{keys} keys x {draws} corpora, substitution preventer with tau fixing 8.\n")
    print(f"{'cell':<16}{'corpus':>10}{'mean':>11}{'within':>10}{'between':>10}"
          f"{'key ratio':>11}{'hit':>6}  verdict")
    mechanism, keyed = [], []
    for k in lp:
        cols = [pk[k][np.isfinite(pk[k])] for pk in per_key]
        cols = [c for c in cols if len(c) >= 2]
        if len(cols) < 3:
            continue
        means = np.array([c.mean() for c in cols])
        within = float(np.mean([c.std(ddof=1) for c in cols]))
        between = float(means.std(ddof=1))
        ratio = between / within if within > 1e-12 else float("inf")
        # how many of the K keys put the corpus inside their own 0.05 tail
        hits = 0
        for c in cols:
            below = float((c <= lp[k]).mean())
            t = 2 * min(below, 1 - below + 1 / len(c))
            if c.std() < 1e-12 and abs(c.mean() - lp[k]) < 1e-9:
                t = 1.0
            hits += t > 0.05
        verdict = "key" if ratio > 1.0 else "mechanism"
        (keyed if ratio > 1.0 else mechanism).append(k)
        star = "*" if k in REACHABLE else " "
        print(f"{k:<16}{lp[k]:>10.4f}{means.mean():>11.4f}{within:>10.4f}"
              f"{between:>10.4f}{ratio:>11.2f}{f'{hits}/{len(cols)}':>6}  {verdict}{star}")

    print("\n* = currently in the reachable-informative set.")
    print(f"\nmechanism cells ({len(mechanism)}): {', '.join(mechanism)}")
    print(f"key cells ({len(keyed)}): {', '.join(keyed)}")
    bad = [k for k in REACHABLE if k in keyed]
    print(
        f"\nOf the four reachable-informative cells, {len(bad)} are key-determined: "
        f"{', '.join(bad) if bad else 'none'}."
    )

    print(
        "\nSo 'this model lands N cells' is a statement about one key. The mechanism-level"
        "\nquestion is what fraction of keys land them, which is the histogram below."
    )
    print(f"\n{'shape':<15}" + "".join(f"{k} of 4".rjust(9) for k in range(5)) + "   median")
    for label, make in (
        ("substitution", lambda g, s, t: sub_preventer(g, s, t)),
        ("probabilistic", lambda g, s, t: prob_preventer(g, s, 0.75)),
        ("dodge", lambda g, s, t: dodge_generator(g, s)),
    ):
        r2 = random.Random(99)
        counts = []
        for _ in range(keys):
            g = order5_fixing(r2.sample(range(M), 4), r2)
            sigma = r2.sample(range(M), M)
            tau = tau_fixing(r2.sample(range(M), 8), r2)
            rr = random.Random(3301)
            sims = [fingerprint(make(g, sigma, tau)(p, rr)) for p in corpora]
            landed = 0
            for k in REACHABLE:
                c = np.array([s[k] for s in sims], float)
                c = c[np.isfinite(c)]
                if len(c) < 2:
                    continue
                below = float((c <= lp[k]).mean())
                t = 2 * min(below, 1 - below + 1 / len(c))
                if c.std() < 1e-12 and abs(c.mean() - lp[k]) < 1e-9:
                    t = 1.0
                landed += t > 0.05
            counts.append(landed)
        hist = collections.Counter(counts)
        row = "".join(str(hist[k]).rjust(9) for k in range(5))
        print(f"{label:<15}{row}{float(np.median(counts)):>10.1f}")
    print(
        "\nThe tail formula is one-sided below 40 draws (a corpus above every draw scores"
        "\n2/n, a corpus below every draw scores 0), so run this at --draws 60 or more."
    )


if __name__ == "__main__":
    main()
