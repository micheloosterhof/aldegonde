# ABOUTME: Checks empirically that within-block triples carry no invariant beyond the
# ABOUTME: equality pattern, which the base family's classification predicts.
"""The classification says triples are empty. This checks it against the corpus.

`base-family-is-the-symmetric-group.md` closes the classification: degree 29 is prime, a
transitive group of prime degree is 2-transitive or Frobenius, the Frobenius subgroups and
AGL(1,29) are both excluded by measurement, and the 2-transitive groups of degree 29 are
only A29 and S29. **Both are 27-transitive.**

That has a consequence I stated wrongly last tick. `key-local-channel-is-empty.md` bounds
the local channel by 2-transitivity, which settles pairs: the only invariant of a
within-block pair under an unknown base is whether the two runes are equal. I wrote that
the remaining gap was triples. **It is not.** Under A29 or S29 every ordered triple of
distinct runes lies in one orbit, so triples carry nothing either, and the same holds for
every k-tuple up to 27.

The local channel is therefore exactly the equality pattern at every order, not just at
order two.

## Why measure something a theorem already settles

Because the theorem rests on a measured premise -- that the family is transitive and not
Frobenius or affine -- and a direct triple test is an independent way for that chain to
fail. If triples showed structure, the classification would be contradicted somewhere, and
it is cheaper to look than to assume.

## The statistic, and it does not work

For disjoint consecutive triples inside a block, the two differences
`(c_j - c_i, c_k - c_j) mod 29`, scored by mutual information against a permutation null.
The reasoning was that under a 3-transitive family the two differences are independent,
and under a smaller family they are not.

| corpus | MI (nats) | permuted | z |
|---|---|---|---|
| the body | 0.1148 | 0.1167 +- 0.0061 | -0.30 |
| **planted AFFINE base per block** | | | **-0.33** (range -1.4 to +1.9) |
| planted general base per block | | | -0.40 (range -0.9 to +0.1) |

**The control fails.** Affine is 2-transitive and not 3-transitive, so it is precisely the
case this test must catch, and it reads the same as a general base. The body's -0.30 is
therefore worth nothing.

The reason is visible once the algebra is written out. Under an affine base `x -> a*x + b`
the two differences are `a*(u - t)` and `a*(v - u)`: the same unknown multiplier scales
both. What survives is their **ratio**, which is plaintext-determined -- and if the
plaintext ratio is near-uniform over the 28 values, the two scaled differences are very
nearly independent. Mutual information measures independence, so it looks straight past
the one thing the affine family preserves.

**The right statistic is the ratio itself**, and `base-is-not-affine.md` already uses it:
lambda = (c_c - c_a)(c_b - c_a)^-1, with the body at chi2 89.7 against planted affine at
620-1,252 and planted general at 31.5-141.2. That test is decisive where this one is
blind.

## The correction this file exists for

`key-local-channel-is-empty.md` bounds the local channel by 2-transitivity, which settles
pairs. I recorded the remaining gap as **triples**. That was wrong.

`base-family-is-the-symmetric-group.md` completes the classification: the family is A29 or
S29, and **both are 27-transitive**. Every ordered triple of distinct runes lies in one
orbit, so triples carry nothing -- and neither does any k-tuple up to 27. The local
channel is exactly the equality pattern at every order, not only at order two.

So there is no order-k gap to look for. The chain rests on measured premises -- transitive
by `flat-ioc.md` and `no-block-partition.md`, not Frobenius by
`base-family-is-2-transitive.md`, not affine by `base-is-not-affine.md` -- and attacking
one of those is the only way in, not a higher-order statistic.

    python do_triples_carry_anything.py
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import M, lp_words  # noqa: E402

DRAWS = 300
TRIALS = 8


def triples(blocks):
    """Disjoint consecutive triples, as (first difference, second difference)."""
    out = []
    for w in blocks:
        for i in range(0, len(w) - 2, 3):
            a, b, c = w[i], w[i + 1], w[i + 2]
            if a == b or b == c:
                continue
            out.append(((b - a) % M, (c - b) % M))
    return out


def mutual_information(pairs) -> float:
    n = len(pairs)
    joint = Counter(pairs)
    left = Counter(x for x, _ in pairs)
    right = Counter(y for _, y in pairs)
    total = 0.0
    for (x, y), c in joint.items():
        total += (c / n) * np.log((c / n) / ((left[x] / n) * (right[y] / n)))
    return float(total)


def scored(pairs, rng, draws=DRAWS):
    obs = mutual_information(pairs)
    lefts = [x for x, _ in pairs]
    rights = [y for _, y in pairs]
    null = []
    for _ in range(draws):
        rng.shuffle(rights)
        null.append(mutual_information(list(zip(lefts, rights))))
    null = np.array(null)
    return obs, float(null.mean()), float(null.std(ddof=1))


def affine_cipher(blocks, rng):
    """Re-encipher each block under a fresh affine base, which is not 3-transitive."""
    out = []
    for w in blocks:
        a = rng.choice([x for x in range(1, M) if np.gcd(x, M) == 1])
        b = rng.randrange(M)
        out.append([(a * x + b) % M for x in w])
    return out


def general_cipher(blocks, rng):
    out = []
    for w in blocks:
        perm = rng.sample(range(M), M)
        out.append([perm[x] for x in w])
    return out


def main() -> None:
    rng = random.Random(3301)
    body = lp_words()
    pairs = triples(body)
    obs, mean, sd = scored(pairs, rng)
    print(f"{len(pairs):,} disjoint non-degenerate triples in the body.\n")
    print(f"{'corpus':<34}{'MI (nats)':>12}{'permuted':>20}{'z':>8}")
    print(
        f"{'the body':<34}{obs:>12.4f}"
        f"{f'{mean:.4f} +- {sd:.4f}':>20}{(obs - mean) / sd:>+8.2f}"
    )

    for label, cipher in (
        ("planted AFFINE base per block", affine_cipher),
        ("planted general base per block", general_cipher),
    ):
        zs = []
        for t in range(TRIALS):
            r = random.Random(400 + t)
            p = triples(cipher(body, r))
            o, m, s = scored(p, r, draws=120)
            zs.append((o - m) / s)
        print(
            f"{label:<34}{'':>12}{'':>20}{np.mean(zs):>+8.2f}"
            f"   (range {min(zs):+.1f} to {max(zs):+.1f})"
        )

    print(
        "\nAffine is 2-transitive and not 3-transitive, so it is the case this test"
        "\nmust catch. A general base is 3-transitive and must read as nothing."
    )


if __name__ == "__main__":
    main()
