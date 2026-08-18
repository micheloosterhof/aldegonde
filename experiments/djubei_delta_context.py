# ABOUTME: Scans index manipulations (delta, affine, sum, gematria) of the runes
# ABOUTME: preceding both DJU-BEI occurrences; family-blind against a matched null.
"""Is the ciphertext before the two DJU-BEI occurrences related by some
transformation of the rune indices?

`repeated-phrase-dju-bei.md` records that the runes before the phrase are not
EQUAL, and `djubei_context.py` shows nothing is shared on the word-length clock
either. This asks the looser question: are the two preceding streams related by
a shift, a Beaufort flip, an affine map, or a gematria-value relation?

Motivation from the model: at a shared state a constant-offset relation between
the two preceding streams would mean the earlier bases were related by a fixed
translation -- a Vigenere-like structure the walk does not predict, and a real
handle if present.

**Every statistic is calibrated against the same statistic over random
word-start pairs from the corpus, and the family is corrected by the null's OWN
maximum** -- the repo's standing rule after the d4/lag-5 scan-noise episodes.
A per-test p is not a finding; only the family-blind column is.

Note delta-stream agreement over a window IS constant-offset over that window
(d[i]=c[i+1]-c[i] agrees iff c1[i]-c2[i] is constant), so those are one test,
reported once. `alignment_scan.py` already searched the delta stream GLOBALLY
for repeats and found only this phrase at shift 0; this is the local version.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from walk_verifier import (  # noqa: E402
    BEI,
    DJU,
    M,
    compose,
    inverse,
    load_words,
    perm_from_cycles,
    ppow,
    step_products,
)

from aldegonde import c3301  # noqa: E402

KMAX = 25  # runes of context examined before each occurrence
TRIALS = 40000


def flat_and_starts() -> tuple[np.ndarray, list[int]]:
    words = load_words()
    flat: list[int] = []
    starts: list[int] = []
    for w in words:
        starts.append(len(flat))
        flat.extend(w)
    return np.array(flat), starts


def suffix_len(a: np.ndarray, b: np.ndarray, ok) -> int:
    """Longest run, counting back from the end, on which ok(a_tail, b_tail) holds."""
    n = 0
    while n < len(a) and ok(a[len(a) - 1 - n :], b[len(b) - 1 - n :]):
        n += 1
    return n


def const_offset(a: np.ndarray, b: np.ndarray) -> bool:
    return len(set(((a - b) % M).tolist())) == 1


def const_sum(a: np.ndarray, b: np.ndarray) -> bool:
    return len(set(((a + b) % M).tolist())) == 1


def affine_rel(a: np.ndarray, b: np.ndarray) -> bool:
    """Does some x -> mult*x + add mod 29 send b to a on this whole window?"""
    return any(
        np.array_equal((mult * b + add) % M, a)
        for mult in range(1, M)
        for add in range(M)
    )


def identity(a: np.ndarray, b: np.ndarray) -> bool:
    return np.array_equal(a, b)


def reversed_rel(a: np.ndarray, b: np.ndarray) -> bool:
    return np.array_equal(a, b[::-1])


TESTS = {
    "identity": identity,
    "constant offset (= delta match)": const_offset,
    "constant sum (Beaufort)": const_sum,
    "affine  a*x+b": affine_rel,
    "reversed": reversed_rel,
}


def cumulative_stats(flat: np.ndarray, p1: int, p2: int) -> list[tuple[str, int, int]]:
    """Value-style summaries of the preceding runes: do any coincide?"""
    out = []
    for k in (3, 5, 10, 20):
        a, b = flat[p1 - k : p1], flat[p2 - k : p2]
        out.append((f"sum of last {k} mod 29", int(a.sum() % M), int(b.sum() % M)))
        out.append(
            (f"product of last {k} mod 29", int(np.prod(a) % M), int(np.prod(b) % M))
        )
    return out


def backward_reach() -> None:
    """How far back of the state return survives, and what it forces.

    From base_{w+1} = base_w o g^a_w o sigma we get
    base_w = base_{w+1} o sigma^-1 o g^-a_w, so stepping k words back from each
    occurrence multiplies by S_i = sigma^-1 g^-a for the two a-sequences. The
    two products agree up to a power of g only while those sequences agree,
    EXCEPT in the oldest term -- sigma and g generically do not commute, so a
    mismatch anywhere earlier leaves a g-power sandwiched between sigma's,
    which does not simplify."""
    words = load_words()
    a1 = [(len(words[DJU - i]) - 1) % 5 for i in range(1, 11)]
    a2 = [(len(words[BEI - i]) - 1) % 5 for i in range(1, 11)]
    print("\nbackward reach of the state return")
    print(f"  a-sequence back from occ1: {a1}")
    print(f"  a-sequence back from occ2: {a2}")
    k = 0
    while k < len(a1) and a1[k] == a2[k]:
        k += 1
    print(
        f"  sequences first differ at {k + 1} word(s) back "
        f"({a1[k]} vs {a2[k]}), so the relation survives exactly {k + 1} word(s)"
    )

    # verify the one-word algebra numerically for arbitrary keys
    rng = random.Random(11)
    lengths = [len(w) for w in words]
    ok = True
    for _ in range(20):
        g = np.array(perm_from_cycles([5] * 5 + [1] * 4, rng))
        sigma = np.array(perm_from_cycles([9, 7, 7, 3, 3], rng))
        Ms = step_products(g, sigma, lengths)
        si = inverse(sigma)
        for w in (DJU, BEI):
            a = (lengths[w - 1] - 1) % 5
            lhs = Ms[w - 1]
            rhs = compose(compose(Ms[w], si), inverse(ppow(g, a)))
            ok &= np.array_equal(lhs, rhs)
    print(f"  identity base_w = base_w+1 o sigma^-1 o g^-a verified: {ok}")

    aw1, aw2 = (len(words[DJU - 1]) - 1) % 5, (len(words[BEI - 1]) - 1) % 5
    print(
        f"\n  a(occ1-1) = {aw1}, a(occ2-1) = {aw2}  =>  "
        f"base_{DJU - 1} = base_{BEI - 1} o g^{aw2 - aw1}"
    )
    print(
        "  so c1[j] = c2[j'] whenever (j + "
        f"{aw2 - aw1}) mod 5 == j' mod 5 IFF the plaintext letters are equal "
        "(key-free)"
    )
    w1, w2 = words[DJU - 1], words[BEI - 1]
    A = c3301.CICADA_ALPHABET
    shift = (aw2 - aw1) % 5
    print(
        f"  word before occ1: {''.join(A[r] for r in w1)}  "
        f"word before occ2: {''.join(A[r] for r in w2)}"
    )
    tests = 0
    for j in range(len(w1)):
        for jp in range(len(w2)):
            if (j + shift) % 5 == jp % 5:
                tests += 1
                same = w1[j] == w2[jp]
                print(
                    f"    c1[{j}]={A[w1[j]]} vs c2[{jp}]={A[w2[jp]]}  -> plaintext "
                    f"letters {'EQUAL' if same else 'differ'}"
                )
    print(f"  {tests} key-free plaintext comparisons available from this pair")


def main() -> None:
    flat, starts = flat_and_starts()
    p1, p2 = starts[DJU], starts[BEI]
    print(f"corpus {len(flat)} runes; occ1 rune offset {p1}, occ2 {p2}\n")

    rng = random.Random(7)
    valid = [s for s in starts if s >= KMAX]
    pairs = [(rng.choice(valid), rng.choice(valid)) for _ in range(TRIALS)]
    pairs = [(x, y) for x, y in pairs if x != y]

    print(f"{'test':34} {'observed':>8} {'null mean':>10} {'P(>=obs)':>9}")
    obs_all, null_all = {}, {}
    for name, ok in TESTS.items():
        a, b = flat[p1 - KMAX : p1], flat[p2 - KMAX : p2]
        obs = suffix_len(a, b, ok)
        vals = [
            suffix_len(flat[x - KMAX : x], flat[y - KMAX : y], ok) for x, y in pairs
        ]
        arr = np.array(vals)
        p = float((arr >= obs).mean())
        obs_all[name], null_all[name] = obs, arr
        print(f"{name:34} {obs:>8} {arr.mean():>10.2f} {p:>9.3f}")

    # family-blind: is the best of our five tests better than the null's best?
    stacked = np.vstack([null_all[k] for k in TESTS])
    null_max = stacked.max(axis=0)
    obs_max = max(obs_all.values())
    fam_p = float((null_max >= obs_max).mean())
    best = [k for k, v in obs_all.items() if v == obs_max]
    print(
        f"\nfamily-blind: best observed = {obs_max} ({', '.join(best)}); "
        f"P(null's best >= {obs_max}) = {fam_p:.3f}"
    )

    print("\nvalue summaries of the preceding runes (occ1 vs occ2):")
    for name, v1, v2 in cumulative_stats(flat, p1, p2):
        print(f"  {name:28} {v1:3} vs {v2:3} {'MATCH' if v1 == v2 else ''}")

    print("\nthe two preceding streams, last 12 runes (index form):")
    print(f"  occ1 {flat[p1 - 12 : p1].tolist()}")
    print(f"  occ2 {flat[p2 - 12 : p2].tolist()}")
    print(f"  diff {((flat[p1 - 12 : p1] - flat[p2 - 12 : p2]) % M).tolist()}")
    print(f"  sum  {((flat[p1 - 12 : p1] + flat[p2 - 12 : p2]) % M).tolist()}")

    backward_reach()


if __name__ == "__main__":
    main()
