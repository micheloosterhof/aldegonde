# ABOUTME: Audits whether the body is one uniform text across its ten sections on every
# ABOUTME: key-free observable, with planted heterogeneity to measure what it could see.
"""Every pooled statistic in this directory assumes the body is one text. It is.

Nothing here has tested that directly. `does_g_change_mid_book.py` compares the halves'
d-profiles and gets 7:1 for one g; `short-units-are-written-joined.md` checks the joining
rate over nine sections. Neither covers the rest, and every result that pools 2,896
blocks or 12,956 runes rests on the assumption.

The observables have to be **key-free**, or the audit measures the key instead of the
text -- which is how `collision-dispersion-is-key-noise.md` ended. Block lengths, mark
rates and within-block lag-k coincidence all qualify: the base cancels from a lag-k
coincidence, and lengths and marks never involve it.

## Result

Across the ten sections the `$` markers define:

| observable | chi2 | df | P |
|---|---|---|---|
| blocks of length 2 | 3.45 | 8 | 0.903 |
| 4-dot marks per rune | 11.57 | 8 | 0.171 |
| lag-1 doublets | 4.78 | 7 | 0.687 |
| lag-5 coincidences | 4.34 | 7 | 0.740 |
| mean block length | 3.43 | 9 | 0.945 |

Uniform on all five.

## What the audit could have seen

Planting heterogeneity in section 8, the largest at 669 blocks and 3,008 runes:

| observable | planted | chi2 | P |
|---|---|---|---|
| blocks of length 2 | that section at 0.20 | 8.84 | 0.356 |
| blocks of length 2 | **at 0.24, the author's unjoined rate** | **23.32** | **0.003** |
| 4-dot per rune | that section x 1.5 | 22.61 | 0.004 |
| lag-1 doublets | that section at 0.010 | 29.47 | 0.000 |

So a section that did not join at all would be caught, as would a half-again mark rate or
a suppression 1.6x weaker. A section joining at 0.20 against the body's 0.15 would not.
The audit excludes a section behaving like the front matter; it does not exclude mild
drift.

## The gap a chi-square leaves

Chi-square tests scatter, not gradient: a slow drift across the book spreads its
departure over every cell and scores poorly. The trend test below correlates each
observable with section order, which is the shape a changing hand or a lengthening
exemplar would take.

    python is_the_body_homogeneous.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from does_the_cipher_restart import ANNOTATION, RUNE, STANDALONE  # noqa: E402
from sentences_do_not_end_long import BODY  # noqa: E402

from aldegonde import c3301  # noqa: E402

INDEX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
TARGET = 8  # the largest section, where effects are planted
MIN_EXPECTED = 3


def sectioned_blocks():
    """Each block as rune indices, with its section number and closing separator."""
    text = "\n".join(
        line
        for line in BODY.read_text().replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )
    out, current, section = [], [], 0
    for ch in text:
        if RUNE.match(ch):
            current.append(INDEX[ch])
        elif ch == "\n":
            continue
        elif ch in STANDALONE:
            if ch == "$":
                section += 1
        elif ch in c3301.WORD_BOUNDARY:
            if current:
                out.append([current, section, ch])
                current = []
    if current:
        out.append([current, section, None])
    return out


def counts_by_section(blocks, kind):
    """(hits, opportunities) per section for one observable."""
    sections = sorted({s for _, s, _ in blocks})
    hits, totals = [], []
    for s in sections:
        inside = [(b, c) for b, q, c in blocks if q == s]
        if kind == "length2":
            hits.append(sum(1 for b, _ in inside if len(b) == 2))
            totals.append(len(inside))
        elif kind == "mark":
            hits.append(sum(1 for _, c in inside if c == "④"))
            totals.append(sum(len(b) for b, _ in inside))
        else:
            lag = 1 if kind == "d1" else 5
            h = t = 0
            for b, _ in inside:
                for i in range(len(b) - lag):
                    t += 1
                    h += b[i] == b[i + lag]
            hits.append(h)
            totals.append(t)
    return np.array(hits, float), np.array(totals, float)


def homogeneity(hits, totals):
    rate = hits.sum() / totals.sum()
    expected = totals * rate
    keep = expected > MIN_EXPECTED
    chi = float(((hits[keep] - expected[keep]) ** 2 / expected[keep]).sum())
    df = int(keep.sum()) - 1
    return chi, df, float(1 - stats.chi2.cdf(chi, df))


def plant(blocks, kind, level, rng):
    """Give the target section a different rate, leaving every other section alone."""
    out = [[list(b), s, c] for b, s, c in blocks]
    index = [i for i, e in enumerate(out) if e[1] == TARGET]
    if kind == "length2":
        have = sum(1 for i in index if len(out[i][0]) == 2)
        want = int(level * len(index))
        pool = [i for i in index if len(out[i][0]) > 2]
        for i in rng.sample(pool, max(0, min(want - have, len(pool)))):
            out[i][0] = out[i][0][:2]
    elif kind == "mark":
        have = sum(1 for i in index if out[i][2] == "④")
        pool = [i for i in index if out[i][2] != "④"]
        for i in rng.sample(pool, min(int(have * (level - 1)), len(pool))):
            out[i][2] = "④"
    else:
        for i in index:
            b = out[i][0]
            for j in range(1, len(b)):
                if rng.random() < level:
                    b[j] = b[j - 1]
    return out


def main() -> None:
    blocks = sectioned_blocks()
    sections = sorted({s for _, s, _ in blocks})
    print(f"{len(blocks)} blocks in {len(sections)} sections.\n")
    print(
        f"{'section':>8}{'blocks':>8}{'runes':>8}{'mean len':>10}{'frac at 2':>11}"
        f"{'4-dot':>8}"
    )
    for s in sections:
        inside = [(b, c) for b, q, c in blocks if q == s]
        lengths = [len(b) for b, _ in inside]
        print(
            f"{s:>8}{len(inside):>8}{sum(lengths):>8}{np.mean(lengths):>10.2f}"
            f"{np.mean([n == 2 for n in lengths]):>11.3f}"
            f"{sum(1 for _, c in inside if c == '④'):>8}"
        )

    print("\nHomogeneity across sections.\n")
    print(f"{'observable':<26}{'chi2':>8}{'df':>5}{'P':>9}")
    kinds = (
        ("length2", "blocks of length 2"),
        ("mark", "4-dot marks per rune"),
        ("d1", "lag-1 doublets"),
        ("d5", "lag-5 coincidences"),
    )
    for kind, label in kinds:
        chi, df, p = homogeneity(*counts_by_section(blocks, kind))
        print(f"{label:<26}{chi:>8.2f}{df:>5}{p:>9.3f}")
    lengths = np.array([len(b) for b, _, _ in blocks], float)
    weights = np.array(
        [sum(1 for _, q, _ in blocks if q == s) for s in sections], float
    )
    means = np.array(
        [np.mean([len(b) for b, q, _ in blocks if q == s]) for s in sections]
    )
    grand = (weights * means).sum() / weights.sum()
    chi = float((weights * (means - grand) ** 2).sum() / lengths.var(ddof=1))
    print(
        f"{'mean block length':<26}{chi:>8.2f}{len(sections) - 1:>5}"
        f"{1 - stats.chi2.cdf(chi, len(sections) - 1):>9.3f}"
    )

    print(f"\nWhat it could have seen. Heterogeneity planted in section {TARGET}.\n")
    print(f"{'observable':<26}{'planted':<30}{'chi2':>8}{'P':>9}")
    rng = random.Random(3301)
    for kind, label, levels in (
        (
            "length2",
            "blocks of length 2",
            ((0.20, "that section at 0.20"), (0.24, "at 0.24, the author's rate")),
        ),
        ("mark", "4-dot per rune", ((1.5, "that section x 1.5"), (2.0, "x 2.0"))),
        (
            "d1",
            "lag-1 doublets",
            ((0.010, "that section at 0.010"), (0.020, "at 0.020")),
        ),
    ):
        for level, note in levels:
            chi, _, p = homogeneity(
                *counts_by_section(plant(blocks, kind, level, rng), kind)
            )
            print(f"{label:<26}{note:<30}{chi:>8.2f}{p:>9.3f}")

    print("\nTrend with section order, which a chi-square scores poorly.\n")
    print(f"{'observable':<26}{'Spearman r':>12}{'P':>9}{'sections':>10}")
    for kind, label in kinds:
        hits, totals = counts_by_section(blocks, kind)
        keep = totals > 50
        rates = hits[keep] / totals[keep]
        r, p = stats.spearmanr(np.arange(len(hits))[keep], rates)
        print(f"{label:<26}{r:>12.3f}{p:>9.3f}{int(keep.sum()):>10}")

    print(
        "\nNo trend either, though nine usable sections resolve only a strong one."
        "\n\nThe body is one uniform text on every key-free observable, and the audit would"
        "\ncatch a section that failed to join, or one with half again the mark rate, or a"
        "\nsuppression 1.6x weaker. It would not catch a section joining at 0.20 against"
        "\nthe body's 0.15, so mild drift stays open. Pooling the body is sound."
    )


if __name__ == "__main__":
    main()
