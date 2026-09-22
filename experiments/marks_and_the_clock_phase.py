# ABOUTME: Tests whether the scribe's marks sit at a preferred cipher clock phase, and
# ABOUTME: shows the cumulative rune count cannot see one even when it is planted.
"""The marks show no clock preference, and the test could not have found one.

If the four-dot marks were placed where the cipher's clock stood at a particular phase,
that would tie the scribe's punctuation to the mechanism -- the first such link. The
cumulative rune count at each mark is the obvious probe: the clock advances one per rune,
so the count mod 5 should be the phase.

It is not, and that is the whole result.

## The measurement

The 136 four-dot marks in the body, by cumulative rune count mod 5:

    every block-closing boundary   [562, 563, 589, 593, 588]
    closed by a four-dot           [ 19,  26,  22,  35,  34]

Against a null that places 136 marks at random block-closing boundaries -- which carries
the block-length distribution, and so the residue structure the cumulative sums inherit --
this is **chi2 = 6.55, P = 0.15**. The thirteen-dot marks read P = 0.98 on 25 marks.
Nothing.

## Why the test cannot work

The dodge advances the clock an extra step every time it fires, at about 3.4% of
positions, so over 12,956 runes the clock runs some 440 steps ahead of the rune count and
the two decorrelate within a page. Planting the effect confirms it: marks placed at the
generator's **true** clock phase are detected 6 times in 30, against 3 in 30 for marks
placed at random block ends.

    marks placed at true clock phase 0     chi2 5.36 +- 4.12   6/30 significant
    marks placed at random block ends      chi2 4.34 +- 3.74   3/30 significant

Twenty percent detection against a ten percent false-positive rate. The channel is closed
for the same reason the doublet-position test was
(`doublet_gaps_conditioned.py`): anything measured against absolute rune position is
measuring a quantity the clock has already drifted away from.

## Two wrong nulls caught on the way

Both would have been reportable findings:

- **Uniform mod 5.** Testing the marks against a flat distribution gives P = 0.062, with
  modulus 5 the only one of seven showing anything (the others run 0.36 to 0.99). But
  block lengths are not uniform mod 5, so cumulative sums are not either, and the flat
  null is wrong.
- **A boundary set including separators that close no block.** Counting every separator,
  including those following another separator, repeats the same cumulative count and
  doubles one residue: [566, 567, 595, 597, **1118**] over 3,443 "boundaries" for 2,896
  blocks. Against that null the marks read P = 0.0485. Requiring runes since the last
  boundary gives 2,895 boundaries and a flat profile.

    python marks_and_the_clock_phase.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import N_RUNES, order5, prose_corpora  # noqa: E402
from does_the_cipher_restart import ANNOTATION, RUNE, STANDALONE  # noqa: E402
from sentences_do_not_end_long import BODY  # noqa: E402

from aldegonde import c3301  # noqa: E402

PERIOD = 5
DRAWS = 4000
PLANTED_RUNS = 30


def boundaries():
    """(cumulative runes, closing separator) for every boundary that closes a block."""
    text = "\n".join(
        line
        for line in BODY.read_text().replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )
    out, runes, since = [], 0, 0
    for ch in text:
        if RUNE.match(ch):
            runes += 1
            since += 1
        elif ch == "\n" or ch in STANDALONE:
            continue
        elif ch in c3301.WORD_BOUNDARY:
            if since:
                out.append((runes, ch))
                since = 0
    return out


def residues(values) -> np.ndarray:
    return np.bincount([v % PERIOD for v in values], minlength=PERIOD).astype(float)


def chi_against(sample, population) -> float:
    expected = residues(population) / len(population) * len(sample)
    return float(((residues(sample) - expected) ** 2 / expected).sum())


def compose(p, q):
    return [p[q[i]] for i in range(len(p))]


def power_of(p, k):
    out = list(range(len(p)))
    for _ in range(k):
        out = compose(p, out)
    return out


def planted(seed, mark_phase, n_marks, phi=0.90):
    """Encipher, track the TRUE clock at each block end, and place marks at a phase."""
    rng = random.Random(seed)
    g = order5(rng)
    powers = [power_of(g, k) for k in range(PERIOD)]
    sigma = rng.sample(range(N_RUNES), N_RUNES)
    base = rng.sample(range(N_RUNES), N_RUNES)
    clock = runes = 0
    previous = None
    ends = []
    for word in prose_corpora(2896, 1)[0]:
        for p in word:
            c = base[powers[clock % PERIOD][p]]
            if c == previous and rng.random() < phi:
                clock += 1
                c = base[powers[clock % PERIOD][p]]
            previous = c
            clock += 1
            runes += 1
        ends.append((runes, clock % PERIOD))
        base = compose(base, compose(powers[(clock - 1) % PERIOD], sigma))
    counts = [r for r, _ in ends]
    pool = (
        [r for r, ph in ends if ph == mark_phase] if mark_phase is not None else counts
    )
    return counts, rng.sample(pool, min(n_marks, len(pool)))


def main() -> None:
    bounds = boundaries()
    everything = [c for c, _ in bounds]
    marks = [c for c, g in bounds if g == "④"]
    thirteen = [c for c, g in bounds if g == "⑬"]
    print(
        f"{len(everything):,} block-closing boundaries, {len(marks)} closed by a "
        f"four-dot, {len(thirteen)} by a thirteen-dot.\n"
    )
    print(f"{'set':<34}{'counts mod 5':>30}")
    print(
        f"{'every block-closing boundary':<34}"
        f"{str([int(x) for x in residues(everything)]):>30}"
    )
    print(f"{'closed by a four-dot':<34}{str([int(x) for x in residues(marks)]):>30}")

    rng = random.Random(3301)
    print("\nAgainst a null placing the marks at random block-closing boundaries.\n")
    print(f"{'marks':<20}{'n':>5}{'chi2':>8}{'null':>16}{'P':>9}")
    for label, sample in (("four-dot", marks), ("thirteen-dot", thirteen)):
        if len(sample) < 20:
            continue
        observed = chi_against(sample, everything)
        null = np.array(
            [
                chi_against(rng.sample(everything, len(sample)), everything)
                for _ in range(DRAWS)
            ]
        )
        print(
            f"{label:<20}{len(sample):>5}{observed:>8.2f}"
            f"{f'{null.mean():.2f} +- {null.std(ddof=1):.2f}':>16}"
            f"{float((null >= observed).mean()):>9.4f}"
        )

    print("\nCould it have found one? Plant the effect and see.\n")
    print(f"{'marks placed':<34}{'chi2 over 30 runs':>20}{'P < 0.05':>10}")
    for phase, label in (
        (0, "at the true clock phase 0"),
        (None, "at random block ends"),
    ):
        values, significant = [], 0
        for s in range(PLANTED_RUNS):
            counts, sample = planted(100 + s, phase, len(marks))
            observed = chi_against(sample, counts)
            null = np.array(
                [
                    chi_against(
                        random.Random(s * 99 + i).sample(counts, len(sample)), counts
                    )
                    for i in range(200)
                ]
            )
            values.append(observed)
            significant += float((null >= observed).mean()) < 0.05
        print(
            f"{label:<34}"
            f"{f'{np.mean(values):.2f} +- {np.std(values, ddof=1):.2f}':>20}"
            f"{f'{significant}/{PLANTED_RUNS}':>10}"
        )

    print(
        "\nTwenty percent detection against a ten percent false-positive rate. The dodge"
        "\nadvances the clock an extra step at about 3.4% of positions, so over 12,956"
        "\nrunes the clock runs some 440 steps ahead of the rune count and the two"
        "\ndecorrelate within a page. The marks' null result says nothing about the"
        "\nmechanism -- the channel is closed, not the question answered."
    )


if __name__ == "__main__":
    main()
