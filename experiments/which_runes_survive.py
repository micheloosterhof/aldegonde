# ABOUTME: Asks which runes the body's 86 surviving doublets use, which separates the
# ABOUTME: preventer families without a key, a model fit or a surrogate corpus.
"""The preventer families differ in WHICH would-be doublets they let through.

`nothing-else-in-the-book-suppresses-repeats.md` establishes that the body's cipher
inspects its own output and refuses to repeat, and that it fails about one time in five:
86 doublets survive where 447 are expected.

The three candidate rules disagree sharply about those 86.

  substitution   emit `tau(c)` instead of `c`. A doublet survives exactly when
                 `tau(c) = c`, so every survivor is a FIXED POINT of tau. With 81%
                 suppression tau fixes about 5.6 of the 29 runes, so the 86 survivors
                 should use at most six distinct runes.
  clock dodge    re-run the clock. Whether the second emission repeats has nothing to
                 do with which rune it is, so survivors should spread over all 29 in
                 proportion to rune frequency.
  probabilistic  skip with probability phi. Rune-independent by construction, same
                 prediction as the dodge.

That is a discriminator the battery does not have: it needs no key, no model fit and no
surrogate corpus. The corpus answers it directly.

A second half checks placement -- whether the survivors cluster in the stream or sit at
particular positions inside a block -- since a rule that fails in bursts would show it.

    python which_runes_survive.py
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402
from lp_corpus import load_clean  # noqa: E402

ENG = c3301.CICADA_ENGLISH_ALPHABET
M = 29


def main() -> None:
    stream, wid = load_clean()
    n = len(stream)
    positions = [i for i in range(n - 1) if stream[i] == stream[i + 1]]
    survivors = collections.Counter(stream[i] for i in positions)
    total = len(positions)
    freq = collections.Counter(stream)
    expected = np.array([(freq[r] / n) ** 2 * (n - 1) for r in range(M)])
    observed = np.array([survivors[r] for r in range(M)], float)

    print(
        f"{total} surviving doublets in {n:,} runes, against "
        f"{expected.sum():.0f} expected if the cipher were flat"
    )
    print(f"suppression {100 * (1 - total / expected.sum()):.0f}%\n")
    print(
        f"they use {int((observed > 0).sum())} of the 29 runes; "
        f"the one missing is "
        f"{', '.join(ENG[r] for r in range(M) if observed[r] == 0) or 'none'}"
    )

    share = expected / expected.sum()
    exp_counts = total * share
    chi = float((((observed - exp_counts) ** 2) / exp_counts).sum())
    print(f"spread over runes in proportion to frequency: chi2 {chi:.1f} on 28 df\n")

    rng = np.random.default_rng(5)
    draws = rng.multinomial(total, share, size=20000)
    sorted_draws = -np.sort(-draws, axis=1)
    print(f"{'statistic':<34}{'observed':>10}{'null':>18}{'z':>8}")
    top = -np.sort(-observed)
    for k in (6, 8, 12):
        null = sorted_draws[:, :k].sum(axis=1) / total
        got = top[:k].sum() / total
        print(
            f"{'share held by the top ' + str(k) + ' runes':<34}{got:>10.3f}"
            f"{f'{null.mean():.3f} +- {null.std():.3f}':>18}"
            f"{(got - null.mean()) / null.std():>+8.2f}"
        )
    null_zero = (draws == 0).sum(axis=1).astype(float)
    got_zero = int((observed == 0).sum())
    print(
        f"{'runes with no survivor':<34}{got_zero:>10}"
        f"{f'{null_zero.mean():.1f} +- {null_zero.std():.1f}':>18}"
        f"{(got_zero - null_zero.mean()) / null_zero.std():>+8.2f}"
    )

    print(
        "\nThe survivors are spread across essentially every rune, exactly as a"
        "\nrune-blind rule predicts."
        "\n\nThat refutes the substitution preventer outright, and the refutation is"
        "\narithmetic rather than statistical. The number of distinct runes among the"
        f"\nsurvivors is a lower bound on |fix(tau)|: it must be at least "
        f"{int((observed > 0).sum())}."
        "\nThe suppression rate is an upper bound on the same quantity: 81% suppression"
        "\nneeds |fix(tau)| = 0.19 x 29 = 5.6. No permutation satisfies both."
    )

    gaps = np.diff(positions)
    print(
        f"\n\nplacement: {len(gaps)} gaps, mean {gaps.mean():.1f}, minimum {gaps.min()}"
    )
    mins, shorts, cvs = [], [], []
    for _ in range(20000):
        p = np.sort(rng.choice(n - 1, total, replace=False))
        g = np.diff(p)
        mins.append(g.min())
        shorts.append((g <= 20).sum())
        cvs.append(g.std() / g.mean())
    mins, shorts, cvs = (np.array(x, float) for x in (mins, shorts, cvs))
    print(f"{'statistic':<34}{'observed':>10}{'null':>18}{'z':>8}")
    # a minimum is nowhere near normal, so quote the empirical tail rather than a z
    tail = float((mins >= gaps.min()).mean())
    print(
        f"{'smallest gap':<34}{gaps.min():>10}"
        f"{f'{mins.mean():.1f} +- {mins.std():.1f}':>18}"
        f"{f'P={tail:.3f}':>8}"
    )
    print(
        f"{'gaps of 20 or less':<34}{int((gaps <= 20).sum()):>10}"
        f"{f'{shorts.mean():.1f} +- {shorts.std():.1f}':>18}"
        f"{((gaps <= 20).sum() - shorts.mean()) / shorts.std():>+8.2f}"
    )
    cv = gaps.std() / gaps.mean()
    print(
        f"{'gap coefficient of variation':<34}{cv:>10.3f}"
        f"{f'{cvs.mean():.3f} +- {cvs.std():.3f}':>18}"
        f"{(cv - cvs.mean()) / cvs.std():>+8.2f}"
    )
    deciles = np.array_split(np.arange(n - 1), 10)
    seen = set(positions)
    counts = [sum(1 for p in d if int(p) in seen) for d in deciles]
    e = total / 10
    print(f"\nby decile of the corpus: {counts}")
    print(f"  chi2 against uniform {sum((c - e) ** 2 / e for c in counts):.1f} on 9 df")
    print(
        "\nPlacement is unremarkable. The survivors sit where chance puts them, with a"
        "\nmild reluctance to fall close together that reaches only about 1.5 sigma."
    )


if __name__ == "__main__":
    main()
