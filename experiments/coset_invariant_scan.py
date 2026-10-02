# ABOUTME: Tests whether the per-word base family preserves a multiplicative coset of the
# ABOUTME: rune difference, which is the sharpest remaining way the 2-transitivity condition
# ABOUTME: behind the orbit theorem could fail.
"""The orbit theorem rests on one condition. This tests it where it is weakest.

`local-channel-is-exactly-coincidence.md` proves that if the per-word base family acts
2-transitively on the 29 runes, the only base-invariant statistic of a within-word pair
is whether the two runes are equal. Everything the project can learn locally is then
13 bits, and no further local test can exist.

It checks the condition by measuring the within-word DIFFERENCE distribution: a base
family of pure shifts would preserve b - a, and the differences are uniform, so the
family is not shifts. That check is sound but blunt. It spreads any signal over 27
degrees of freedom, and the natural non-2-transitive families are not shifts.

The natural ones are the proper subgroups of AGL(1,29). For a base x -> m*x + c with m
drawn from a multiplicative subgroup H of order k, the family is transitive but is
2-transitive only when H is the whole group F_29*. The invariant is not the difference:
it is the COSET H*(b - a) in F_29*. With 28/k cosets, a chi2 on 28/k - 1 degrees of
freedom concentrates the same signal the 27-df test dilutes -- by a factor of 27 at the
quadratic-residue split.

Subgroups of F_29* (cyclic of order 28): k = 1, 2, 4, 7, 14, 28. k = 1 is the plain
difference test already on record; k = 28 is the 2-transitive case with nothing to find.

A second family is tested alongside: x -> m*x with no additive part fixes rune 0 and
preserves the RATIO b/a, so that is measured too.

A test with no positive control is worth nothing, so `--power` plants each subgroup
family into the LP's own plaintext and reports what the scan then sees.

    python coset_invariant_scan.py [--draws 400] [--power]
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

M = 29
DIVISORS = (1, 2, 4, 7, 14, 28)


def subgroup(k: int) -> list[int]:
    """The multiplicative subgroup of F_29* of order k."""
    g = 2  # 2 is a primitive root mod 29
    step = pow(g, 28 // k, M)
    out, x = [], 1
    for _ in range(k):
        out.append(x)
        x = x * step % M
    return out


def coset_map(k: int) -> dict[int, int]:
    """Nonzero residue -> index of its coset under the order-k subgroup."""
    h = subgroup(k)
    labels: dict[int, int] = {}
    nxt = 0
    for x in range(1, M):
        if x in labels:
            continue
        for u in h:
            labels[x * u % M] = nxt
        nxt += 1
    return labels


def within_word_pairs(stream: list[int], wid: list[int], lag: int):
    for i in range(len(stream) - lag):
        if wid[i] == wid[i + lag]:
            yield stream[i], stream[i + lag]


def chi2(counts: list[int]) -> float:
    n = sum(counts)
    e = n / len(counts)
    return sum((c - e) ** 2 / e for c in counts) if e else 0.0


def scan(stream: list[int], wid: list[int], op: str) -> dict:
    """chi2 per (lag, subgroup order) for the difference or ratio invariant."""
    out: dict = {}
    for lag in range(1, 6):
        pairs = list(within_word_pairs(stream, wid, lag))
        if op == "diff":
            vals = [(b - a) % M for a, b in pairs if (b - a) % M]
        else:
            # a == b gives ratio 1, and doublets are suppressed; excluding them
            # matches the difference test, which already drops the zero cell
            vals = [b * pow(a, M - 2, M) % M for a, b in pairs if a and b and a != b]
        for k in DIVISORS:
            lab = coset_map(k)
            counts = collections.Counter(lab[v] for v in vals)
            cells = 28 // k
            out[lag, k] = (
                chi2([counts[i] for i in range(cells)]),
                cells - 1,
                len(vals),
            )
    return out


def plant(words: list[list[int]], nwords: int, k: int, seed: int):
    """Encipher LP plaintext with base x -> m*x + c, m in H_k, composed after one
    fixed g of order 5. The base family is 2-transitive only when k = 28."""
    import random  # noqa: PLC0415

    rng = random.Random(seed)
    h = [pow(pow(2, 28 // k, M), i, M) for i in range(k)]
    perm = list(range(M))
    cycle = [3, 17, 8, 22, 11]
    for a, b in zip(cycle, cycle[1:] + cycle[:1]):
        perm[a] = b

    def g(x: int, j: int) -> int:
        for _ in range(j % 5):
            x = perm[x]
        return x

    out: list[int] = []
    wid: list[int] = []
    for i in range(nwords):
        word = words[i % len(words)]
        m, c = rng.choice(h), rng.randrange(M)
        for j, r in enumerate(word):
            out.append((m * g(r, j) + c) % M)
            wid.append(i)
    return out, wid


def power(nwords: int) -> None:
    """What each subgroup family would look like, at the body's size."""
    from lp_plaintext_register import corpus  # noqa: PLC0415

    words = corpus()
    print("\npower: the same scan on planted ciphertext, lag 1, chi2 / df")
    print(f"{'base family':>16}" + "".join(f"{'k=' + str(k):>12}" for k in DIVISORS))
    for k in DIVISORS[1:]:
        s, w = plant(words, nwords, k, 9)
        res = scan(s, w, "diff")
        row = "".join(f"{res[1, kk][0]:>8.0f}/{res[1, kk][1]:<3}" for kk in DIVISORS)
        tag = f"H_{k}{' (2-transitive)' if k == 28 else ''}"
        print(f"{tag:>16}{row}")
    print(
        "H_28 is the 2-transitive case the orbit theorem assumes: no signal by design."
    )
    print(
        "\nH_14 is the blind spot, and the reason is g, not the sample size. The"
        "\ninvariant an H_14 base exposes is the quadratic-residue class of"
        "\ng^j(p_j) - g^i(p_i), not of p_j - p_i. With g the identity the plant scores"
        "\n18.6 on 1 df; with a non-affine g of order 5 it scores 0.79, because g"
        "\nscrambles the residue classes before the base ever applies."
    )


def main() -> None:
    draws = 400
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    stream, wid = load_clean()
    if "--power" in sys.argv:
        power(wid[-1] + 1)
        return
    import random  # noqa: PLC0415

    rng = random.Random(3301)

    for op, title in (("diff", "difference b - a"), ("ratio", "ratio b / a")):
        print(f"\n=== invariant: {title} ===")
        obs = scan(stream, wid, op)
        # surrogate null: shuffle runes across the corpus, word lengths preserved
        nulls: dict = collections.defaultdict(list)
        for _ in range(draws):
            sh = stream[:]
            rng.shuffle(sh)
            for key, (c, _df, _n) in scan(sh, wid, op).items():
                nulls[key].append(c)
        print(
            f"{'lag':>4}{'k':>4}{'cells':>7}{'pairs':>8}{'chi2':>9}{'null mu':>9}{'sd':>7}{'z':>7}"
        )
        for lag in range(1, 6):
            for k in DIVISORS:
                c, df, n = obs[lag, k]
                s = nulls[lag, k]
                mu = sum(s) / len(s)
                sd = (sum((x - mu) ** 2 for x in s) / len(s)) ** 0.5
                z = (c - mu) / sd if sd else 0.0
                flag = "  <-- signal" if z > 3 else ""
                print(
                    f"{lag:>4}{k:>4}{df + 1:>7}{n:>8}{c:>9.1f}{mu:>9.1f}{sd:>7.1f}{z:>+7.2f}{flag}"
                )


if __name__ == "__main__":
    main()
