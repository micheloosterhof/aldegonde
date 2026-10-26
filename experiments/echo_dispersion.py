# ABOUTME: Asks whether every block shares its alphabet five apart at one attenuated rate, or
# ABOUTME: only a subset shares fully, by the dispersion of per-block distance-5 match counts.
"""Is the distance-5 sharing universal, or confined to a subset of blocks?

The pooled within-block d5 rate (0.0492) sits below English's (0.0550 after drift). Two
readings give the same pooled number: every block shares and the preventer's drift
attenuates the relation uniformly; or a fraction f of blocks share fully at English's
rate while the rest sit at chance, with f pinned by the pooled rate. The pooled rate
cannot separate them. The spread of per-block match counts can, in principle: a mixture
is over-dispersed relative to a single rate.

Both arms are simulated from prose words drawn to the body's own block-length multiset,
so the plaintext's own heterogeneity (words with repeated letters) is in both:

  universal   every pair keeps the plaintext relation with probability (1-q)^5, else chance
  subset      a block keeps the plaintext relation with probability f, else every pair is
              chance; f chosen so the arm's pooled rate equals the body's

Statistics, each priced under both arms:

  D      dispersion index: sum over blocks of (m - n r_L)^2 / (n r_L (1 - r_L)), with r_L
         the per-length-class mean of the same corpus, divided by the number of blocks
  W2     blocks holding two or more matches
  W3     blocks holding three or more

    python experiments/echo_dispersion.py [--draws 2000]
"""

from __future__ import annotations

import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from echo_gradient_vs_english import CLASSES, LAG, Q, label  # noqa: E402
from frame_count_baseline import prose_books  # noqa: E402
from within_word_d5 import M, parse_clean_sections  # noqa: E402

SEED = 20261028
MIN_LENGTH = 6


def length_class(length: int) -> tuple[int, int] | None:
    for c in CLASSES:
        if c[0] <= length <= c[1]:
            return c
    return None


def match_counts(words: list[list[int]]) -> list[tuple[int, int, tuple[int, int]]]:
    """(matches, pairs, length class) per block of at least MIN_LENGTH runes."""
    out = []
    for w in words:
        c = length_class(len(w))
        if c is None:
            continue
        pairs = len(w) - LAG
        out.append((sum(w[i] == w[i + LAG] for i in range(pairs)), pairs, c))
    return out


def statistics(counts: list[tuple[int, int, tuple[int, int]]]) -> dict[str, float]:
    by_class: dict[tuple[int, int], list[int]] = defaultdict(lambda: [0, 0])
    for m, n, c in counts:
        by_class[c][0] += m
        by_class[c][1] += n
    rate = {c: m / n for c, (m, n) in by_class.items()}
    d = 0.0
    for m, n, c in counts:
        r = rate[c]
        d += (m - n * r) ** 2 / (n * r * (1 - r))
    return {
        "D": d / len(counts),
        "W2": sum(m >= 2 for m, _, _ in counts),
        "W3": sum(m >= 3 for m, _, _ in counts),
        "rate": sum(m for m, _, _ in counts) / sum(n for _, n, _ in counts),
    }


def simulate(
    pools: dict[int, list[list[int]]],
    lengths: list[int],
    rng: random.Random,
    *,
    keep_pair: float,
    keep_block: float,
) -> list[tuple[int, int, tuple[int, int]]]:
    """Per-block match counts for prose words drawn to the body's lengths.

    A block that is not kept has every pair at chance; in a kept block each pair keeps
    the plaintext relation with probability keep_pair and is at chance otherwise.
    """
    out = []
    for length in lengths:
        w = rng.choice(pools[length])
        pairs = length - LAG
        shared = rng.random() < keep_block
        m = 0
        for i in range(pairs):
            if shared and rng.random() < keep_pair:
                m += w[i] == w[i + LAG]
            else:
                m += rng.random() < 1 / M
        out.append((m, pairs, length_class(length)))
    return out


def arm(name: str, draws: int, observed: dict[str, float], **kw) -> None:
    rng = random.Random(SEED)
    pools, lengths = arm.pools, arm.lengths
    sims = defaultdict(list)
    for _ in range(draws):
        for k, v in statistics(simulate(pools, lengths, rng, **kw)).items():
            sims[k].append(v)
    print(f"\n{name}: {draws} draws")
    for k in ("rate", "D", "W2", "W3"):
        s = np.array(sims[k])
        above = (np.sum(s >= observed[k]) + 1) / (draws + 1)
        below = (np.sum(s <= observed[k]) + 1) / (draws + 1)
        print(
            f"  {k:<5} observed {observed[k]:>8.4f}   arm {s.mean():>8.4f} ± {s.std():.4f}"
            f"   z {(observed[k] - s.mean()) / s.std():>+6.2f}   P(>=) {above:.3f}  P(<=) {below:.3f}"
        )
    arm.results[name] = {k: np.array(v) for k, v in sims.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=2000)
    args = ap.parse_args()

    sections = parse_clean_sections(str(ROOT / "data/page0-56.txt"))
    body_words = [w for s in sections for w in s if length_class(len(w))]
    lengths = [len(w) for w in body_words]
    observed = statistics(match_counts(body_words))
    print(
        f"body: {len(body_words)} blocks of {MIN_LENGTH}+ runes, pooled d5 rate {observed['rate']:.4f}"
    )
    print(
        "per-class blocks: "
        + ", ".join(
            f"{label(c)}: {sum(length_class(n) == c for n in lengths)}" for c in CLASSES
        )
    )

    pools: dict[int, list[list[int]]] = defaultdict(list)
    for book in prose_books():
        for w in book:
            if length_class(len(w)):
                pools[len(w)].append(w)
    missing = [n for n in set(lengths) if not pools[n]]
    assert not missing, f"no prose words of length {missing}"
    # lengths the body has that prose lacks would stop here; 12+ is pooled by the class
    arm.pools, arm.lengths, arm.results = pools, lengths, {}

    keep_pair = (1 - Q) ** LAG
    # the subset arm's f: pooled plaintext rate of the drawn prose at these lengths
    rng = random.Random(SEED)
    plain = statistics(simulate(pools, lengths, rng, keep_pair=1.0, keep_block=1.0))[
        "rate"
    ]
    f = (observed["rate"] - 1 / M) / (plain - 1 / M)
    print(
        f"\nprose rate at the body's lengths {plain:.4f}; universal arm keeps (1-q)^5 = {keep_pair:.3f}"
        f" of each pair; subset arm keeps a fraction f = {f:.3f} of blocks fully"
    )

    arm(
        "universal sharing, drift-attenuated",
        args.draws,
        observed,
        keep_pair=keep_pair,
        keep_block=1.0,
    )
    arm("subset sharing, fraction f", args.draws, observed, keep_pair=1.0, keep_block=f)

    u, s = (
        arm.results["universal sharing, drift-attenuated"],
        arm.results["subset sharing, fraction f"],
    )
    print("\nseparation of the two arms (difference of means over pooled sd):")
    for k in ("D", "W2", "W3"):
        sep = (s[k].mean() - u[k].mean()) / np.sqrt((s[k].var() + u[k].var()) / 2)
        print(
            f"  {k:<5} universal {u[k].mean():>8.3f}   subset {s[k].mean():>8.3f}   {sep:>+5.2f} sigma"
        )


if __name__ == "__main__":
    main()
