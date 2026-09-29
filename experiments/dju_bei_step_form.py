# ABOUTME: Shows that no bare-sigma base step can produce the DJU-BEI state return, by
# ABOUTME: intersecting the word gap's divisors with the base-reuse floor.
"""If the return is real, the base step cannot be a bare sigma. That follows from two
measurements already on the books.

`dju-bei-is-more-surprising-than-recorded.md` puts the chance of the DJU-BEI repeat at
1 in 2,700 under the framing a state return predicts, so it is worth asking what a genuine
return would require.

A state return needs the base to come back: `base_(w+1449) = base_w`. If the step between
blocks were a bare permutation sigma, that means `sigma^1449 = id`, so

    ord(sigma) divides 1449 = 3^2 x 7 x 23

which leaves twelve candidates, the largest being 1449 itself.

But a bare-sigma step visits exactly ord(sigma) distinct bases, and `base_pool_floor.py`
measures how small a base pool the corpus allows. A pool of N predicts 10,853/N excess
joint-agreement pairs among two-rune blocks, against an observed 95% upper bound of +4.0 --
so any pool below about 2,713 is excluded. Every divisor of 1449 is below that.

The conclusion needs no assumption about sigma's order: a bare-sigma step cannot produce
the return at all.

    python dju_bei_step_form.py
"""

from __future__ import annotations

GAP = 1449
PREDICTED_EXCESS = 10853.0  # base_pool_floor.py: excess pairs for a pool of N is this/N
OBSERVED_UPPER = 4.0  # 95% upper bound on the observed excess


def main() -> None:
    divisors = [d for d in range(1, GAP + 1) if GAP % d == 0]
    ceiling = PREDICTED_EXCESS / OBSERVED_UPPER
    print(f"DJU-BEI word gap {GAP} = 3^2 x 7 x 23")
    print(f"divisors: {divisors}\n")
    print(
        f"base_pool_floor.py: a pool of N predicts {PREDICTED_EXCESS:.0f}/N excess pairs"
    )
    print(
        f"observed 95% upper bound {OBSERVED_UPPER:+.1f}, so pools below"
        f" {ceiling:,.0f} are excluded\n"
    )
    print(f"{'ord(sigma)':>11}{'predicted excess':>18}{'verdict':>12}")
    for d in divisors:
        e = PREDICTED_EXCESS / d
        print(f"{d:>11}{e:>18.1f}{'EXCLUDED' if e > OBSERVED_UPPER else 'allowed':>12}")
    print(
        "\nEvery divisor is excluded, so no bare-sigma step produces the return. If the"
        "\nrepeat is a genuine state return, the base step must be a product that returns"
        "\nto the identity without any single factor having small order -- the walk's"
        "\n`g^a o sigma`, whose exponents depend on the BLOCK LENGTHS between the two"
        "\noccurrences. That ties the return to visible data rather than to sigma alone."
        "\n\nThe argument needs no sigma order floor: the largest divisor, 1449, is itself"
        f"\nwell below the {ceiling:,.0f} the base-reuse measurement allows."
    )


if __name__ == "__main__":
    main()
