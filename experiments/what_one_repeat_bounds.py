# ABOUTME: Calibrates how the block-repeat count scales with base-pool size, turning the
# ABOUTME: single DJU-BEI repeat into an interval on the state space rather than a verdict.
"""One repeat is worth an interval, not a verdict. Here is the interval.

`dju_bei_chance_rate_simulated.py` fixed the chance rate for a block-aligned whole-block
repeat of 6+ runes under the open walk at **0.00033**, confirming the recorded figure.
The complementary question is what a *compact* base pool would predict, because that is
what the repeat is evidence for if it is evidence for anything.

Calibrating by simulation, with the base drawn **i.i.d.** from a pool of S states:

| base states | mean repeats | lambda x S |
|---|---|---|
| 100 | 0.480 | 48 |
| 200 | 0.310 | 62 |
| 406 | 0.083 | 34 |
| 812 | 0.060 | 49 |
| 2,000 | 0.027 | 53 |
| open walk | 0.00033 | — |

A clean 1/S law: **lambda ~ 50 / S**.

## What one repeat supports

The corpus has exactly one. Read as a Poisson count that gives lambda-hat = 1 with a 95%
interval of [0.025, 5.6], so

    S in [about 10, about 2,000]

and the open walk, at lambda = 0.00033, sits outside it. At S = 406 the likelihood ratio
against the open walk is a couple of hundred to one, and it moves by a factor of two
between runs because lambda at that pool size rests on a handful of simulated repeats.

**That is one observation and it should not move much.** The number is a likelihood ratio
from a single count, and the repo's independent evidence runs the other way:
`rotor-machine-compact-state.md` disproves transitive compact groups of degree 29 by
Burnside, and `two-rune-depth-no-base-reuse.md` excludes pools below ~300 by a far
better-powered route -- 465 two-rune words rather than one repeat. What survives both is
a narrow window, roughly 300 to 2,000, in which AGL(1,29) and its subgroup of order 406
happen to sit.

## A cross-check that has no power

The obvious test is base reuse among two-rune blocks: with S = 406 each base serves about
seven blocks. Counting blocks identical at both positions does not separate the models --
406 gives 0.00133, 812 gives 0.00130, the open walk 0.00142, and the corpus 0.00106, all
within about 2.5 sigma of each other. The conditional form of that test in
`two-rune-depth-no-base-reuse.md` is the one with power; this crude version has none and
is recorded so it is not retried.

## The modelling trap this walked into

The first version cycled the base deterministically through the pool, so blocks S apart
shared a base. That made the answer depend on whether the runes in S blocks summed to a
multiple of five, and the result was not monotonic in S at all: 600 states gave exactly
zero repeats, 812 gave 0.267, 1,200 gave zero again. A lattice artifact between the cycle
and the clock, not a property of the state space. Drawing i.i.d. removes it and restores
the 1/S law.

    python what_one_repeat_bounds.py [--draws 120]
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import N_RUNES, order5, prose_corpora  # noqa: E402
from dju_bei_chance_rate_simulated import minimal_runs  # noqa: E402
from does_the_cipher_restart import body_blocks  # noqa: E402

POOLS = (100, 200, 406, 812, 2000)
OPEN_WALK_RATE = 0.00033  # measured over 6,000 draws in dju_bei_chance_rate_simulated


def compose(p, q):
    return [p[q[i]] for i in range(len(p))]


def power(p, k):
    out = list(range(len(p)))
    for _ in range(k):
        out = compose(p, out)
    return out


def encipher(plain, seed, states, phi=0.90):
    """Base drawn i.i.d. from `states` bases, or the open walk when states is None.

    i.i.d. rather than cycling: a deterministic cycle makes blocks S apart share a base,
    and whether they also share a clock phase then depends on the runes in S blocks
    summing to a multiple of five, which is a lattice artifact and not a state count.
    """
    rng = random.Random(seed)
    g = order5(rng)
    powers = [power(g, k) for k in range(5)]
    sigma = rng.sample(range(N_RUNES), N_RUNES)
    pool = (
        [rng.sample(range(N_RUNES), N_RUNES) for _ in range(states)] if states else None
    )
    base = rng.sample(range(N_RUNES), N_RUNES)
    out, clock, previous = [], 0, None
    for word in plain:
        b = pool[rng.randrange(states)] if states else base
        emitted = []
        for p in word:
            c = b[powers[clock % 5][p]]
            if c == previous and rng.random() < phi:
                clock += 1
                c = b[powers[clock % 5][p]]
            emitted.append(c)
            previous = c
            clock += 1
        out.append(emitted)
        if not states:
            base = compose(base, compose(powers[(clock - 1) % 5], sigma))
    return out


def repeat_count(blocks) -> int:
    seen, total = set(), 0
    for _, key in minimal_runs(blocks):
        if key in seen:
            total += 1
        else:
            seen.add(key)
    return total


def main() -> None:
    draws = 120
    for i, arg in enumerate(sys.argv):
        if arg == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    observed = repeat_count([b for b, _ in body_blocks(set())])
    plain = prose_corpora(2896, 1)[0]

    print(f"The body has {observed} block-aligned repeat of 6+ runes.\n")
    print(
        f"{'base states':>12}{'draws':>7}{'mean repeats':>14}{'se':>8}"
        f"{'lambda x S':>12}{'P(exactly 1)':>14}"
    )
    fitted = []
    for states in POOLS:
        counts = np.array(
            [repeat_count(encipher(plain, 7000 + s, states)) for s in range(draws)],
            float,
        )
        lam = counts.mean()
        fitted.append((states, lam))
        print(
            f"{states:>12,}{draws:>7}{lam:>14.3f}"
            f"{counts.std(ddof=1) / math.sqrt(draws):>8.3f}"
            f"{lam * states:>12,.0f}{lam * math.exp(-lam):>14.4f}"
        )
    print(
        f"{'open walk':>12}{6000:>7}{OPEN_WALK_RATE:>14.5f}{'':>8}{'':>12}"
        f"{OPEN_WALK_RATE * math.exp(-OPEN_WALK_RATE):>14.5f}"
    )

    constant = float(np.mean([lam * s for s, lam in fitted if lam > 0]))
    print(f"\n  lambda ~ {constant:.0f} / S, so one repeat puts lambda-hat at 1")
    print("  95% Poisson interval for one count: [0.025, 5.6]")
    print(f"  which is S in [{constant / 5.6:.0f}, {constant / 0.025:,.0f}]")
    at_406 = next(lam for s, lam in fitted if s == 406)
    ratio = (at_406 * math.exp(-at_406)) / (OPEN_WALK_RATE * math.exp(-OPEN_WALK_RATE))
    print(f"\n  likelihood ratio at S = 406 against the open walk: {ratio:,.0f} to 1")

    print(
        "\nOne observation. The ratio is a likelihood from a single count, and the"
        "\nindependent evidence runs the other way: Burnside disproves transitive compact"
        "\ngroups of degree 29, and the two-rune depth test excludes pools below ~300 on"
        "\n465 words rather than one repeat. The window surviving both is roughly 300 to"
        "\n2,000 -- where AGL(1,29) and its order-406 subgroup happen to sit. Treat this"
        "\nas a calibration of what the repeat can support, not as support."
    )


if __name__ == "__main__":
    main()
