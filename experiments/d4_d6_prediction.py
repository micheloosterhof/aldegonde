# ABOUTME: Fits an order-5 g to the observed within-word d1-d4 cells and lets it
# ABOUTME: predict d6 out of sample, testing the claimed d4/d6 puzzle.
"""Does the order-5 walk really predict d4 = d6?

`mixed-cycle-progression.md` and `length-clocked-walk.md` state the d4-d6 split
is sharp "because pure order-5 predicts the two cells EQUAL: g^4 = g^-1 and
g^6 = g share the same leading-order diagonal frequency algebra
(sum q(x) q(g(x)) both ways)".

That equality is the independence approximation, in which the rate depends only
on the unigram distribution q. The real rate is

    r_d = P(p[i] = g^d(p[i+d])) = sum_{a,b} P_d(a, b) [a == g^d(b)]

the g^d diagonal evaluated on the *distance-d within-word pair table* P_d. The
same file already retracted exactly this argument for d1 vs d6
(`d5-partial-alphabet-leak.md`: "An earlier draft here claimed this
'contradicts pure order-5-g (g^6=g^1)' -- that was wrong"), because P_1 and P_6
differ. P_4 and P_6 differ too, and g^4 = g^-1 equals sum P(g(y), y) rather than
sum P(y, g(y)) -- equal only if P were symmetric.

So this script does not assume anything about the algebra. It fits g to the
observed d1..d4 and reports what the fitted g predicts for d6, which no cell in
the fit constrains. If the observed d6 lands inside the predicted spread, the
"d6 has no mechanism" gap closes.

Ratios are reported alongside absolute rates because the plaintext reference is
dictionary words at the LP length distribution, not the LP's own register, and
a register offset largely cancels in d4/d6.
"""

from __future__ import annotations

import random
import statistics

from experiments.mechanism_discriminator import real_words
from experiments.stay_slot_cipher import (
    diag_rate,
    pair_matrices,
    perm_from_cycles,
    ppow,
    tune,
)

SEED = 3301
RESTARTS = 40
DMAX = 6
FIT_CELLS = (1, 2, 3, 4)
OBSERVED = {1: 0.0064, 2: 0.0347, 3: 0.0370, 4: 0.0410, 5: 0.0492, 6: 0.0245}
# matches / pairs on the clean corpus, for the cells whose error matters
COUNTS = {4: (131, 3197), 5: (102, 2073), 6: (31, 1267)}


def predicted(mats: dict, g: list[int]) -> dict[int, float]:
    """Within-word profile implied by g: r_d = diagonal of g^d on P_d."""
    return {d: diag_rate(mats[d][0], ppow(g, d % 5)) for d in range(1, DMAX + 1)}


def fit_one(
    mats: dict, rng: random.Random, cells: tuple[int, ...] = FIT_CELLS
) -> tuple[list[int], dict[int, float]]:
    """Tune an order-5 g to the given cells, leaving the rest free."""

    def obj(g: list[int]) -> float:
        total = 0.0
        for d in cells:
            r = diag_rate(mats[d][0], ppow(g, d % 5))
            total += ((r - OBSERVED[d]) / OBSERVED[d]) ** 2
        return total

    g = tune(perm_from_cycles([5] * 5 + [1] * 4, rng), obj, rng)
    return g, predicted(mats, g)


def main() -> None:
    rng = random.Random(SEED)
    words = real_words(rng)
    mats = pair_matrices(words, dmax=DMAX)
    print(f"real runeglish words: {len(words)}, fitted on d{FIT_CELLS}, "
          f"d5 and d6 left free\n")

    plain = {d: diag_rate(mats[d][0], list(range(29))) for d in range(1, DMAX + 1)}
    print("plaintext reference: " + "  ".join(f"d{d} {plain[d]:.4f}" for d in plain))

    fits = [fit_one(mats, rng) for _ in range(RESTARTS)]
    profiles = [p for _, p in fits]

    print(f"\n{'cell':>5}{'observed':>10}{'fitted mean':>13}{'sd':>9}"
          f"{'min':>9}{'max':>9}   in fit?")
    for d in range(1, DMAX + 1):
        vals = [p[d] for p in profiles]
        mark = "fitted" if d in FIT_CELLS else "PREDICTED"
        print(f"{'d' + str(d):>5}{OBSERVED[d]:>10.4f}{statistics.mean(vals):>13.4f}"
              f"{statistics.pstdev(vals):>9.4f}{min(vals):>9.4f}{max(vals):>9.4f}"
              f"   {mark}")

    d6 = [p[6] for p in profiles]
    covered = sum(1 for v in d6 if v <= OBSERVED[6])
    print("\nd6 is the out-of-sample cell.")
    print(f"   observed {OBSERVED[6]:.4f}; fitted g predicts "
          f"{statistics.mean(d6):.4f} +- {statistics.pstdev(d6):.4f}")
    print(f"   {covered} of {len(d6)} fits predict d6 at or below the observed value")

    ratios = [p[4] / p[6] for p in profiles if p[6] > 0]
    obs_ratio = OBSERVED[4] / OBSERVED[6]
    print("\nd4/d6 ratio (register offsets largely cancel)")
    print(f"   observed {obs_ratio:.2f}")
    print(f"   fitted   {statistics.mean(ratios):.2f} +- {statistics.pstdev(ratios):.2f}"
          f"  range {min(ratios):.2f}-{max(ratios):.2f}")
    print("   the independence approximation that motivated the puzzle predicts 1.00")

    # The LP cells carry their own binomial error, and d6 rests on 31 events.
    # Comparing a cell to the model means carrying both errors.
    print("\nobserved vs the model's own prediction, both errors carried")
    se = {d: (OBSERVED[d] * (1 - OBSERVED[d]) / n) ** 0.5 for d, (_, n) in COUNTS.items()}
    for d, (k, n) in sorted(COUNTS.items()):
        print(f"   d{d}: {k}/{n} = {OBSERVED[d]:.4f} +- {se[d]:.4f} (binomial)")

    pred6, spread6 = statistics.mean(d6), statistics.pstdev(d6)
    z6 = (pred6 - OBSERVED[6]) / (se[6] ** 2 + spread6**2) ** 0.5
    print(f"\n   d6      observed {OBSERVED[6]:.4f} +- {se[6]:.4f} vs model "
          f"{pred6:.4f} +- {spread6:.4f}  ->  z = {z6:+.2f}")

    rel = ((se[4] / OBSERVED[4]) ** 2 + (se[6] / OBSERVED[6]) ** 2) ** 0.5
    se_ratio = obs_ratio * rel
    m_ratio, s_ratio = statistics.mean(ratios), statistics.pstdev(ratios)
    zr = (obs_ratio - m_ratio) / (se_ratio**2 + s_ratio**2) ** 0.5
    print(f"   d4/d6   observed {obs_ratio:.2f} +- {se_ratio:.2f} vs model "
          f"{m_ratio:.2f} +- {s_ratio:.2f}  ->  z = {zr:+.2f}")

    # Sharper than "is d6 predicted": can any order-5 g hit every cell at once?
    joint = tuple(sorted(FIT_CELLS + (6,)))
    best = min(
        (fit_one(mats, rng, joint)[1] for _ in range(RESTARTS)),
        key=lambda p: sum(abs(p[d] - OBSERVED[d]) / OBSERVED[d] for d in joint),
    )
    print(f"\nfitting d{joint} jointly -- is the whole profile reachable?")
    for d in joint:
        off = (best[d] - OBSERVED[d]) / se[d] if d in se else float("nan")
        tail = f"  ({off:+.1f} binomial sd)" if d in se else ""
        print(f"   d{d}: observed {OBSERVED[d]:.4f}  best fit {best[d]:.4f}{tail}")


if __name__ == "__main__":
    main()
