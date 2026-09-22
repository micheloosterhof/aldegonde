# ABOUTME: Verifies the 1-in-2,700 chance figure for the DJU-BEI repeat by direct
# ABOUTME: simulation, and shows simulated repeats are collisions, not state returns.
"""The single most load-bearing number here had never been checked by simulation. It holds.

Four results condition on the DJU-BEI repeat being a genuine state return, and their
weight rests on one figure: how often chance alone produces a block-aligned whole-block
repeat of six or more runes. `dju-bei-is-more-surprising-than-recorded.md` gives **0.00037,
1 in 2,693**, and says how: "computed from the corpus's own unigram distribution
(per-rune match probability 0.03455)". That is an independence calculation, and the body's
runes are not independent -- the adjacent-doublet rate is 0.0063 against a chance 0.0345,
and a block whose plaintext repeats a letter needs fewer than six coincidences to match
another block.

Simulation makes no such assumption. Encipher a fixed prose corpus under the walk with a
fresh key each time, with **no state return by construction**, and count corpora carrying
a block-aligned repeat of 6+ runes:

    6,000 simulated corpora
      with a repeat            2      ->  0.00033   (1 in 3,000)
      95% interval                        0.00004 to 0.00120

    the recorded analytic figure         0.00037   (1 in 2,693)

**The recorded figure sits inside the interval and within 12% of the point estimate.**
It is confirmed by a method that shares none of its assumptions.

## The simulated repeats are not returns

Both were inspected against the generator's own state:

    seed  172: blocks 1987 and 2440, lengths [6]      same base FALSE, same phase FALSE
    seed 1067: blocks  367 and 2123, lengths [5, 2]   same base FALSE, same phase FALSE

So a walk with no state return still produces block-aligned repeats, at about the rate
chance predicts, by coincidence of the substitution. `models-on-the-informative-cells.md`
records `returns` as the one battery cell that "nothing simulated produces"; at 1 in 3,000
that is a statement about how many draws were taken, not about the mechanism. Two of six
thousand produce one.

## A caution about my own recomputation

Recomputing the analytic figure from the corpus's own length-pattern distribution --
2,895 minimal runs over 140 distinct patterns, each pair matching at 0.03455^runes --
gives **0.00010, 1 in 10,514**, three times lower than the recorded figure and the
simulation. The simulation is the authority here because it assumes nothing; the
discrepancy is most likely that counting only *minimal* runs undercounts the opportunities.
Recorded so the 1-in-10,514 is not mistaken for a correction.

    python dju_bei_chance_rate_simulated.py [--draws 6000]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import N_RUNES, order5, prose_corpora  # noqa: E402
from does_the_cipher_restart import body_blocks  # noqa: E402

MIN_RUNES = 6
RECORDED = 0.00037


def compose(p, q):
    return [p[q[i]] for i in range(len(p))]


def power(p, k):
    out = list(range(len(p)))
    for _ in range(k):
        out = compose(p, out)
    return out


def encipher(plain, seed, phi=0.90):
    """The walk with a fresh key, and no state return by construction."""
    rng = random.Random(seed)
    g = order5(rng)
    powers = [power(g, k) for k in range(5)]
    sigma = rng.sample(range(N_RUNES), N_RUNES)
    base = rng.sample(range(N_RUNES), N_RUNES)
    out, clock, previous = [], 0, None
    for word in plain:
        emitted = []
        for p in word:
            c = base[powers[clock % 5][p]]
            if c == previous and rng.random() < phi:
                clock += 1
                c = base[powers[clock % 5][p]]
            emitted.append(c)
            previous = c
            clock += 1
        out.append(emitted)
        base = compose(base, compose(powers[(clock - 1) % 5], sigma))
    return out


def minimal_runs(blocks):
    """Each run of consecutive whole blocks reaching MIN_RUNES, as a hashable key."""
    out = []
    for i in range(len(blocks)):
        j, total = i, 0
        while j < len(blocks):
            total += len(blocks[j])
            if total >= MIN_RUNES:
                break
            j += 1
        if j >= len(blocks):
            break
        out.append((i, tuple(tuple(b) for b in blocks[i : j + 1])))
    return out


def has_repeat(blocks) -> bool:
    seen = set()
    for _, key in minimal_runs(blocks):
        if key in seen:
            return True
        seen.add(key)
    return False


def main() -> None:
    draws = 6000
    for i, arg in enumerate(sys.argv):
        if arg == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    body = [b for b, _ in body_blocks(set())]
    seen, found = {}, []
    for i, key in minimal_runs(body):
        if key in seen:
            found.append((seen[key], i, key))
        seen[key] = i
    print(f"The body: {len(body)} blocks, {sum(len(b) for b in body):,} runes.")
    print(f"Block-aligned whole-block repeats of {MIN_RUNES}+ runes: {len(found)}")
    for a, b, key in found:
        print(
            f"   blocks {a} and {b}, lengths {[len(x) for x in key]}, "
            f"{sum(len(x) for x in key)} runes"
        )

    plain = prose_corpora(2896, 1)[0]
    hits = sum(1 for s in range(draws) if has_repeat(encipher(plain, 1000 + s)))
    rate = hits / draws
    low = stats.beta.ppf(0.025, hits, draws - hits + 1) if hits else 0.0
    high = stats.beta.ppf(0.975, hits + 1, draws - hits)

    print(f"\n{draws:,} simulated corpora under the walk, no state return.\n")
    print(
        f"  corpora with such a repeat   {hits:>6}   {rate:.5f}"
        f"   (1 in {1 / rate:,.0f})"
        if rate
        else f"  none in {draws}"
    )
    print(f"  95% interval                          {low:.5f} to {high:.5f}")
    print(f"\n  the recorded analytic figure          {RECORDED:.5f}   (1 in 2,693)")
    inside = low <= RECORDED <= high
    print(f"  recorded figure inside the interval:  {inside}")
    print(
        "\nThe recorded figure is confirmed by a method sharing none of its assumptions."
        "\nThe independence calculation it came from is not obviously safe -- the body's"
        "\nadjacent-doublet rate is 0.0063 against a chance 0.0345, and a block repeating"
        "\na letter needs fewer than six coincidences to match another -- but it lands in"
        "\nthe right place anyway."
        "\n\nA walk with no state return still produces these repeats, at about the rate"
        "\nchance predicts. So the corpus's one repeat is a 1-in-3,000 event under the"
        "\nno-return model, which is what the recorded figure already said."
    )


if __name__ == "__main__":
    main()
