# ABOUTME: A block-structured (intransitive) state group leaks plaintext
# ABOUTME: block-bigram correlations into the ciphertext. Is that visible?
"""The last escape from the compact-state dichotomy is an intransitive state
group <g, sigma>: the runes split into blocks no base ever mixes, so |G| can
be small enough to index and the machine becomes hand-runnable (e.g. five
5-position wheels plus a 4-position wheel, 5^5 x 4 = 12500 states).

intransitive_block_cost.py shows unigram masses do not close it.

But blocks leak more than masses. If a plaintext rune always enciphers to a
rune of its own block, then for any two blocks B, B'

    P(c_i in B, c_{i+1} in B')  ==  P(p_i in B, p_{i+1} in B')

exactly. The plaintext's block-level bigram table passes through UNCHANGED,
whatever the wiring inside the blocks. English/runeglish adjacent letters are
strongly dependent (vowel-consonant alternation above all), so unless the
designer found a partition whose block-bigram table happens to be
independent, this shows in the ciphertext.

The ciphertext's off-diagonal bigram matrix is measured uniform
(bigram-ioc.md, chi2 p = 0.22). So the test is: can ANY admissible partition
make the runeglish block-bigram table look independent? Searched here, not
assumed.
"""

from __future__ import annotations

import random
import sys
from functools import lru_cache
from pathlib import Path

from aldegonde.c3301 import CICADA_ALPHABET as ALPHABET

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

N = 29
NG = ROOT / "src" / "aldegonde" / "data" / "ngrams" / "runeglish"


# The shipped runeglish ngram tables spell J as U+1682 while
# c3301.CICADA_ALPHABET uses U+1684. Indexing the tables by the alphabet
# therefore drops that rune silently; normalise instead.
NGRAM_ALIAS = {"ᛂ": "ᛄ"}


def bigram_matrix() -> list[list[float]]:
    idx = {r: i for i, r in enumerate(ALPHABET)}
    m = [[0.0] * N for _ in range(N)]
    kept = dropped = 0
    for line in (NG / "bigrams.txt").read_text().split("\n"):
        if not line.strip():
            continue
        bg, c = line.split()
        bg = "".join(NGRAM_ALIAS.get(ch, ch) for ch in bg)
        if len(bg) != 2 or bg[0] not in idx or bg[1] not in idx:
            dropped += int(c) if c.isdigit() else 0
            continue
        m[idx[bg[0]]][idx[bg[1]]] += int(c)
        kept += int(c)
    assert dropped == 0, f"dropped {dropped} bigram counts -- alphabet mismatch"
    assert kept > 0
    tot = sum(sum(r) for r in m)
    return [[v / tot for v in row] for row in m]


def block_chi2(mat: list[list[float]], assign: list[int], nb: int, n_obs: int) -> float:
    """Chi2 of the block-aggregated bigram table against independence."""
    agg = [[0.0] * nb for _ in range(nb)]
    for a in range(N):
        for b in range(N):
            agg[assign[a]][assign[b]] += mat[a][b]
    rows = [sum(r) for r in agg]
    cols = [sum(agg[i][j] for i in range(nb)) for j in range(nb)]
    chi = 0.0
    for i in range(nb):
        for j in range(nb):
            e = rows[i] * cols[j]
            if e > 0:
                chi += (agg[i][j] - e) ** 2 / e
    return chi * n_obs


def observed_block_chi2(assign: list[int], nb: int) -> tuple[float, int]:
    stream, _ = load_clean()
    agg = [[0.0] * nb for _ in range(nb)]
    for a, b in zip(stream, stream[1:]):
        agg[assign[a]][assign[b]] += 1
    n = sum(sum(r) for r in agg)
    mat = [[v / n for v in row] for row in agg]
    rows = [sum(r) for r in mat]
    cols = [sum(mat[i][j] for i in range(nb)) for j in range(nb)]
    chi = 0.0
    for i in range(nb):
        for j in range(nb):
            e = rows[i] * cols[j]
            if e > 0:
                chi += (mat[i][j] - e) ** 2 / e
    return chi * n, int(n)


def main() -> None:
    mat = bigram_matrix()
    tot = sum(sum(r) for r in mat)
    assert abs(tot - 1.0) < 1e-9, tot
    stream, _ = load_clean()
    n_obs = len(stream) - 1
    sizes = [5, 5, 5, 5, 5, 4]
    nb = len(sizes)
    df = (nb - 1) ** 2
    print(f"blocks {sizes}, {nb} blocks, df = {df}, corpus adjacencies = {n_obs}")

    # How dependent is runeglish at block level, for a RANDOM admissible partition?
    rng = random.Random(3301)
    base = []
    for b, s in enumerate(sizes):
        base += [b] * s
    rand_chi = []
    for _ in range(300):
        a = base[:]
        rng.shuffle(a)
        rand_chi.append(block_chi2(mat, a, nb, n_obs))
    rand_chi.sort()
    print(
        f"\nrandom partitions: plaintext block chi2 median {rand_chi[150]:.0f}, "
        f"min {rand_chi[0]:.0f}, max {rand_chi[-1]:.0f}"
    )

    # Best case for the designer: minimise the leak.
    assign = base[:]
    rng.shuffle(assign)
    best = block_chi2(mat, assign, nb, n_obs)
    for _ in range(200000):
        i, j = rng.randrange(N), rng.randrange(N)
        if assign[i] == assign[j]:
            continue
        assign[i], assign[j] = assign[j], assign[i]
        c = block_chi2(mat, assign, nb, n_obs)
        if c <= best:
            best = c
        else:
            assign[i], assign[j] = assign[j], assign[i]
    print(f"best partition found (200k local moves): plaintext block chi2 = {best:.1f}")

    print(f"chi2 critical value at df={df}: 5% ~ {chi2_crit(df):.1f}")
    print(f"  its unigram mass error: {mass_error(assign, sizes) * 100:.1f}%")

    # The design must satisfy BOTH constraints at once: block masses = size/29
    # (else the flat ciphertext is impossible) AND a near-independent block
    # bigram table (else the leak shows). Search under the mass constraint.
    print("\n--- joint search: minimise block chi2 subject to mass error <= 2% ---")
    assign = base[:]
    rng.shuffle(assign)

    def score(a: list[int]) -> tuple[float, float]:
        return mass_error(a, sizes), block_chi2(mat, a, nb, n_obs)

    me, ch = score(assign)
    for _ in range(300000):
        i, j = rng.randrange(N), rng.randrange(N)
        if assign[i] == assign[j]:
            continue
        assign[i], assign[j] = assign[j], assign[i]
        me2, ch2 = score(assign)
        # lexicographic: get mass under 2% first, then minimise chi2
        cur_bad = max(me - 0.02, 0.0)
        new_bad = max(me2 - 0.02, 0.0)
        if (new_bad, ch2) <= (cur_bad, ch):
            me, ch = me2, ch2
        else:
            assign[i], assign[j] = assign[j], assign[i]
    print(
        f"  best joint partition: mass error {me * 100:.2f}%, plaintext block chi2 = {ch:.1f}"
    )
    obs, _ = observed_block_chi2(assign, nb)
    print(f"  observed CIPHERTEXT block chi2 under that partition = {obs:.1f}")

    # The observed value is inflated by the doublet suppression (the block
    # diagonal is depleted), which is the trap README warns about. Calibrate
    # against a doublet-preserving surrogate rather than against chi2 tables.
    from aldegonde.stats.nulls import doublet_shuffle

    rate = sum(1 for a, b in zip(stream, stream[1:]) if a == b) / (len(stream) - 1)
    resample = doublet_shuffle(rate)
    nrng = random.Random(90210)
    surrogate_streams = [resample(stream, nrng) for _ in range(200)]
    sur = []
    for s in surrogate_streams:
        agg = [[0.0] * nb for _ in range(nb)]
        for a, b in zip(s, s[1:]):
            agg[assign[a]][assign[b]] += 1
        n = sum(sum(r) for r in agg)
        m2 = [[v / n for v in row] for row in agg]
        rows = [sum(r) for r in m2]
        cols = [sum(m2[i][j] for i in range(nb)) for j in range(nb)]
        sur.append(
            sum(
                (m2[i][j] - rows[i] * cols[j]) ** 2 / (rows[i] * cols[j])
                for i in range(nb)
                for j in range(nb)
                if rows[i] * cols[j] > 0
            )
            * n
        )
    mu = sum(sur) / len(sur)
    sd = (sum((x - mu) ** 2 for x in sur) / len(sur)) ** 0.5
    print(
        f"\n  doublet-preserving surrogate (no block structure): {mu:.1f} +/- {sd:.1f}"
    )
    print(f"    observed ciphertext {obs:.1f}  -> z = {(obs - mu) / sd:+.2f}")
    print(f"    required by a block machine {ch:.1f}  -> z = {(ch - mu) / sd:+.2f}")

    # Completeness: blocks are unions of g-orbits (five 5-cycles, four fixed
    # points), so sweep every admissible block-size shape. Merging blocks
    # shrinks the leak but grows the group -- that is the whole trade-off.
    print("\n--- every admissible block shape (blocks = unions of g-orbits) ---")
    print("  NB: the surrogate mean depends on the BLOCK COUNT (chi2 has")
    print("  df = (nb-1)^2), so each shape is calibrated separately. An earlier")
    print("  version reused one calibration for every shape and its z column")
    print("  was wrong for any shape without 6 blocks.")
    print("\n  shape                        nb  surr mean   massErr   leak chi2      z")
    for shape in admissible_shapes():
        if len(shape) == 1:
            note = "transitive -> the dichotomy case"
            print(
                f"  {str(shape):<28} {'-':>3} {'-':>10}   {'-':>7}   {'-':>9}   {note}"
            )
            continue
        nb2 = len(shape)
        me2, ch2 = joint_best(mat, shape, n_obs, iters=60000)
        a2 = []
        for b, s in enumerate(shape):
            a2 += [b] * s
        random.Random(3).shuffle(a2)
        vals = []
        for s in surrogate_streams[:80]:
            agg = [[0.0] * nb2 for _ in range(nb2)]
            for x, y in zip(s, s[1:]):
                agg[a2[x]][a2[y]] += 1
            nn = sum(sum(r) for r in agg)
            m2 = [[v / nn for v in row] for row in agg]
            rr = [sum(r) for r in m2]
            cc = [sum(m2[i][j] for i in range(nb2)) for j in range(nb2)]
            vals.append(
                sum(
                    (m2[i][j] - rr[i] * cc[j]) ** 2 / (rr[i] * cc[j])
                    for i in range(nb2)
                    for j in range(nb2)
                    if rr[i] * cc[j] > 0
                )
                * nn
            )
        mu2 = sum(vals) / len(vals)
        sd2 = (sum((v - mu2) ** 2 for v in vals) / len(vals)) ** 0.5
        zz = (ch2 - mu2) / sd2
        flag = "  <- test has no power here" if zz < 2 else ""
        print(
            f"  {str(shape):<28} {nb2:>3} {mu2:>10.1f}   {me2 * 100:6.2f}%   "
            f"{ch2:9.1f}   {zz:+6.1f}{flag}"
        )

    print(
        "\nReading: the plaintext block chi2 is what a block-structured machine\n"
        "MUST deposit in the ciphertext. Shapes with MANY small blocks leak\n"
        "heavily and are excluded. Shapes with few large blocks leak so little\n"
        "that the required leak falls under the surrogate's own noise -- there\n"
        "the test is uninformative rather than confirming. It discriminates\n"
        "only at roughly 5 blocks or more."
    )


def admissible_shapes() -> list[list[int]]:
    """Block sizes from grouping five 5-orbits and four 1-orbits."""
    out = set()

    def parts(n: int, mx: int) -> list[list[int]]:
        if n == 0:
            return [[]]
        res = []
        for k in range(min(n, mx), 0, -1):
            for rest in parts(n - k, k):
                res.append([k] + rest)
        return res

    for fives in parts(5, 5):  # how the 5-cycles group
        for ones in parts(4, 4):  # how the fixed points group
            base = [5 * f for f in fives]
            # attach each group of fixed points either standalone or onto a block
            out.add(tuple(sorted(base + list(ones), reverse=True)))
            for i in range(len(base)):
                merged = base[:]
                merged[i] += sum(ones)
                out.add(tuple(sorted(merged, reverse=True)))
    return [list(s) for s in sorted(out, key=lambda t: (len(t), t), reverse=True)]


def joint_best(
    mat: list[list[float]], sizes: list[int], n_obs: int, iters: int = 60000
) -> tuple[float, float]:
    rng = random.Random(11)
    nb = len(sizes)
    assign = []
    for b, s in enumerate(sizes):
        assign += [b] * s
    rng.shuffle(assign)
    me, ch = mass_error(assign, sizes), block_chi2(mat, assign, nb, n_obs)
    for _ in range(iters):
        i, j = rng.randrange(N), rng.randrange(N)
        if assign[i] == assign[j]:
            continue
        assign[i], assign[j] = assign[j], assign[i]
        me2, ch2 = mass_error(assign, sizes), block_chi2(mat, assign, nb, n_obs)
        if (max(me2 - 0.02, 0.0), ch2) <= (max(me - 0.02, 0.0), ch):
            me, ch = me2, ch2
        else:
            assign[i], assign[j] = assign[j], assign[i]
    return me, ch


@lru_cache(maxsize=1)
def _freq_vector() -> tuple[float, ...]:
    from intransitive_block_cost import unigram_freqs

    raw = unigram_freqs()
    f = {NGRAM_ALIAS.get(k, k): v for k, v in raw.items()}
    assert set(f) == set(ALPHABET), set(ALPHABET) ^ set(f)
    return tuple(f[r] for r in ALPHABET)


def mass_error(assign: list[int], sizes: list[int]) -> float:
    fv = _freq_vector()
    masses = [0.0] * len(sizes)
    for i, b in enumerate(assign):
        masses[b] += fv[i]
    return max(abs(m - s / N) / (s / N) for m, s in zip(masses, sizes))


def chi2_crit(df: int) -> float:
    """5% upper critical value, Wilson-Hilferty."""
    z = 1.6449
    return df * (1 - 2 / (9 * df) + z * (2 / (9 * df)) ** 0.5) ** 3


if __name__ == "__main__":
    main()
