# ABOUTME: The walk where a would-be doublet makes the letter clock skip a step, so the
# ABOUTME: same rule suppresses doublets and partly breaks the period-5 echo.
"""Michel's rule: the doublet avoidance IS what breaks the distance-5 echo.

`interrupted-walk.md` failed because its interrupt fired at random marked runes and
injected the g-squared relation into adjacent positions, lifting the doublet rate.
This fires only where a doublet WOULD have formed, so it removes doublets instead of
adding them, and its rate is set by the corpus rather than by a free parameter.

    c_j = base_w( g^(k_j)( p_j ) )
    k_(j+1) = k_j + 1, and one step more whenever the emission would have repeated

The algebra pays off three times over. Inside a word the base is constant, so a
would-be doublet is `g(p_j) = p_(j-1)`; after the extra step the emission repeats only
if `g^2(p_j) = p_(j-1)`, and combining the two a doublet SURVIVES only when

    g(p_j) = p_j = p_(j-1)

a plaintext double sitting on a fixed point of `g`. That gives, without tuning any
permutation's diagonal:

  * a doublet rate of (plaintext doubles) x (fixed points), 0.0263 x 4/29 = 0.0036
    against the corpus's 0.0063, and tunable from 0.0000 to 0.0174 by choosing WHICH
    four runes are fixed -- structural, where the walk needs a tuned 29-permutation;
  * doublets that ARE plaintext doubles, hence late in words: the corpus reads 0.553
    where the walk gives 0.40;
  * a seam rate equal to the within-word rate by construction, since the same rule
    fires across a boundary -- the corpus reads 0.0079 against 0.0063, an equality
    `length-clocked-walk.md` explicitly says the walk does not predict.

Run with no arguments for the self-test, `--fit` to score it on the held-out battery.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import (  # noqa: E402
    M,
    compare,
    compose,
    fingerprint,
    lp_words,
    ppow,
    prose_corpora,
    rich_order5,
)

# Nothing is fitted to a diagonal: g and sigma are drawn at random and only the choice
# of which runes g fixes is selected, against the doublet rate.
FITTED = {"d1w"}


def encipher(plain, base0, g, sigma):
    """Emit, and skip an extra clock step whenever the emission would have repeated."""
    gp = [ppow(g, k) for k in range(5)]
    base = list(base0)
    out = []
    clock = 0
    previous = None
    for word in plain:
        cipher_word = []
        for p in word:
            c = base[gp[clock % 5][p]]
            if c == previous:
                clock += 1
                c = base[gp[clock % 5][p]]
            cipher_word.append(c)
            previous = c
            clock += 1
        out.append(cipher_word)
        # the walk's own step: the g-power carries the letter clock through the space,
        # so the products vary per word and the base visits a large group. Stepping by
        # a bare sigma instead leaves only ord(sigma) bases, which shows up at once as
        # a non-flat IoC and hundreds of identical cipher words.
        base = compose(base, compose(gp[(clock - 1) % 5], sigma))
    return out


def decode_ambiguity(base0, g, sigma):
    """Two plaintexts, one ciphertext: the rule is not uniquely decodable.

    A skip makes the emission `base(g^(k+1)(p_(j-1)))`, which is exactly what the
    UNSKIPPED clock emits for a repeated plaintext rune. So `... x x ...` and
    `... x g^-1(x) ...` produce identical output, and a decoder holding the key
    cannot tell them apart.
    """
    gp = [ppow(g, k) for k in range(5)]
    for x in range(M):
        if g[x] == x:
            continue  # a fixed point does not move, so no collision arises there
        first = [x, x]
        second = [x, gp[4][x]]  # g^-1(x), since g has order 5
        a = encipher([first], base0, g, sigma)
        b = encipher([second], base0, g, sigma)
        if a == b and first != second:
            return first, second, a[0]
    return None


def generator(g, sigma):
    def generate(plain, rng):
        return encipher(plain, rng.sample(range(M), M), g, sigma)

    return generate


def fixed_points(g):
    return [x for x in range(M) if g[x] == x]


def order5_fixing(keep, rng):
    """An order-5 permutation whose fixed points are exactly `keep`."""
    movers = [x for x in range(M) if x not in keep]
    rng.shuffle(movers)
    g = list(range(M))
    for c in range(5):
        cycle = movers[5 * c : 5 * c + 5]
        for t in range(5):
            g[cycle[t]] = cycle[(t + 1) % 5]
    return g


def self_test() -> None:
    rng = random.Random(3301)
    plain = prose_corpora(2928, 1)[0]
    lp = fingerprint(lp_words())
    g = rich_order5(rng)
    sigma = rng.sample(range(M), M)
    base0 = rng.sample(range(M), M)
    cipher = encipher(plain, base0, g, sigma)

    # the suppression is structural: no diagonal of g or sigma was tuned
    got = fingerprint(cipher)
    print(
        f"untuned g and sigma:  d1w {got['d1w']:.4f}   seam {got['seam']:.4f}"
        f"   (corpus {lp['d1w']:.4f}, {lp['seam']:.4f}; chance {1 / M:.4f})"
    )
    assert got["d1w"] < 0.012, "the rule should suppress doublets with no tuning"
    assert abs(got["d1w"] - got["seam"]) < 0.012, (
        "seam should track the within-word rate"
    )

    # every surviving doublet must be a plaintext double on a fixed point of g
    fixed = set(fixed_points(g))
    bad = 0
    for wp, wc in zip(plain, cipher):
        for j in range(len(wc) - 1):
            if wc[j] == wc[j + 1] and not (wp[j] == wp[j + 1] and wp[j] in fixed):
                bad += 1
    print(f"surviving doublets that are NOT a plaintext double on a fixed point: {bad}")
    assert bad == 0, "the algebra says every survivor is a plaintext double"

    collision = decode_ambiguity(base0, g, sigma)
    print(
        f"\ndecodability: {collision[0]} and {collision[1]} both encipher to "
        f"{collision[2]}"
    )
    assert collision is not None, "the collision argument should exhibit one"
    print("so the rule as stated is NOT uniquely decodable -- see the verdict")
    print("self-test passed")


def fit() -> None:
    rng = random.Random(3301)
    lp = fingerprint(lp_words())
    plain = prose_corpora(2928, 1)[0]
    # the only thing chosen: which four runes g fixes, against the doublet rate
    best = None
    for _ in range(400):
        keep = rng.sample(range(M), 4)
        g = order5_fixing(keep, rng)
        sigma = rng.sample(range(M), M)
        rate = fingerprint(encipher(plain, rng.sample(range(M), M), g, sigma))["d1w"]
        if best is None or abs(rate - lp["d1w"]) < best[0]:
            best = (abs(rate - lp["d1w"]), g, sigma, keep)
    _err, g, sigma, keep = best
    print(f"chose g's four fixed points {sorted(keep)}; g and sigma otherwise random\n")
    compare(generator(g, sigma), 60, FITTED, "doublet-dodging walk")


if __name__ == "__main__":
    if "--fit" in sys.argv:
        fit()
    else:
        self_test()
