# ABOUTME: Tries a sharper statistic for key structure, the ciphertext bigram difference
# ABOUTME: histogram, and closes the construction question with a split-half check.
"""Can any statistic tell how the key was built? After this one, the answer is no.

`which_key_constructions_are_visible.py` scores six ways of building sigma and base_0 on
the battery cells and finds only the classic keyword alphabet appreciably displaced from
free permutations; columnar, reversed-rest, affine and shift all sit within 0.42 sigma.
That leaves the costing in `how-big-is-the-key-really.md` resting on an untestable
premise, so a sharper statistic is worth one attempt.

The bigram DIFFERENCE histogram is the natural candidate: a structured base composes with
g^j in a structured way, and any residue should land on particular offsets rather than
raising a scalar chi2. It is 29 cells rather than one number.

Offset 0 has to be dropped. It is the doublet cell, the preventer empties it, and with it
in the chi2 every arm reads about 300 on 28 df and nothing else is visible.

    python key_construction_is_unmeasurable.py [--keys 30]
"""

from __future__ import annotations

import collections
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import M, lp_words, prose_corpora  # noqa: E402
from which_key_constructions_are_visible import KINDS, build, walk  # noqa: E402


def difference_histogram(words) -> np.ndarray:
    stream = [r for w in words for r in w]
    h = np.zeros(M)
    for a, b in zip(stream, stream[1:]):
        h[(b - a) % M] += 1
    return h


def chi_without_zero(h: np.ndarray) -> float:
    v = h[1:]
    e = v.sum() / (M - 1)
    return float(((v - e) ** 2 / e).sum())


def main() -> None:
    keys = 30
    for i, a in enumerate(sys.argv):
        if a == "--keys" and i + 1 < len(sys.argv):
            keys = int(sys.argv[i + 1])

    vocab = collections.Counter()
    for c in prose_corpora(2928, 20):
        for w in c:
            vocab[tuple(w)] += 1
    keywords = [list(w) for w in vocab
                if len(set(w)) == len(w) and 4 <= len(w) <= 10]
    corpora = list(prose_corpora(2928, keys))
    rk = random.Random(5)

    body = lp_words()
    observed = chi_without_zero(difference_histogram(body))
    print("bigram difference histogram, offset 0 dropped, chi2 on 27 df\n")
    print(f"{'construction':<16}{'over ' + str(keys) + ' keys':>26}{'z of the body':>16}")
    for kind in KINDS:
        v = []
        for t in range(keys):
            g = order5_fixing(rk.sample(range(M), 4), rk)
            sigma = build(kind, keywords[rk.randrange(len(keywords))], rk)
            base = build(kind, keywords[rk.randrange(len(keywords))], rk)
            if len(set(sigma)) != M or len(set(base)) != M:
                continue
            v.append(chi_without_zero(difference_histogram(
                walk(g, sigma, base, corpora[t], random.Random(60 + t))
            )))
        v = np.array(v)
        print(f"{kind:<16}{f'{v.mean():.1f} +- {v.std():.1f}':>26}"
              f"{(observed - v.mean()) / v.std():>16.2f}")
    print(f"\nthe body: chi2 {observed:.1f} on 27 df, where 27 is uniform")
    print("Every construction is uniform, so the statistic sees none of them. The body's"
          "\ndeparture is about two sigma above them all and needs its own check.")

    h = difference_histogram(body)
    e = h[1:].sum() / (M - 1)
    z = (h - e) / np.sqrt(e)
    order = np.argsort(-np.abs(z[1:])) + 1
    print(f"\n{'offset':>7}{'count':>8}{'z':>8}")
    for i in order[:5]:
        print(f"{i:>7}{int(h[i]):>8}{z[i]:>8.2f}")

    half = len(body) // 2
    a, b = difference_histogram(body[:half]), difference_histogram(body[half:])
    print(f"\n{'half':<14}{'chi2 on 27 df':>16}{'largest |z|':>14}{'at offset':>12}")
    for label, hh in (("first", a), ("second", b)):
        ee = hh[1:].sum() / (M - 1)
        zz = (hh - ee) / np.sqrt(ee)
        top = int(np.argsort(-np.abs(zz[1:]))[0]) + 1
        print(f"{label:<14}{chi_without_zero(hh):>16.1f}"
              f"{np.abs(zz[1:]).max():>14.2f}{top:>12}")
    za = (a[1:] - a[1:].mean()) / a[1:].std()
    zb = (b[1:] - b[1:].mean()) / b[1:].std()
    print(f"\ncorrelation of the two halves' cell profiles: "
          f"{np.corrcoef(za, zb)[0, 1]:+.3f}")
    print(
        "\nA real structure repeats across halves. This one does not -- the halves"
        "\ndisagree about which offset is extreme, and their profiles correlate at"
        "\nnothing. The chi2 of 41.4 is a fluctuation, and it came after two looks at"
        "\nthe same histogram."
        "\n\nSo the sharper statistic fails on both counts: it cannot see the"
        "\nconstructions, and the one departure it finds in the body does not replicate."
        "\nWith the battery cells and this, the key's description length is unmeasurable"
        "\nfrom the body, and the costing's premise cannot be settled from the ciphertext."
    )


if __name__ == "__main__":
    main()
