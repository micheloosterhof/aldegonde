# ABOUTME: Which classical relation, GF(29) map, autokey or self-mutating machine gives
# ABOUTME: the body's doublet rate for free, measured on the author's own plaintext.
"""Does any natural cipher suppress adjacent repeats without being tuned to?

`doublet-suppression-requires-design.md`: for a cipher that is a bijection at every
position, a ciphertext doublet is p_j = R(p_{j+1}) for one relation R, so the doublet
rate is the plaintext bigram mass on R's graph. This script evaluates that mass on the
author's register (`lp_plaintext_register.corpus`) for every relation a cipher designer
might reach for without tuning, then simulates the machines that have no fixed R.

  relations   shifts, GF(29) multipliers, power maps, every affine map, atbash, the
              step of a 5x5 Polybius square under four natural fills, and the random
              baselines (random squares, random permutations)
  autokeys    Vigenere and Beaufort plaintext autokey, second-order, ciphertext autokey
  machines    Chaocipher on 29 symbols, move-to-front and transpose lists, on the
              register's words with their order shuffled
  homophones  how much of the would-be doublet mass spare symbols could dodge

Chance is 1/29 = 0.0345; the body reads 0.0063 inside words and 0.0079 at seams.

    python experiments/natural_relations_doublet_rate.py
"""

from __future__ import annotations

import collections
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_tokenized  # noqa: E402
from lp_plaintext_register import corpus as register  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
NAMES = c3301.CICADA_ENGLISH_ALPHABET
Perm = list[int]


def body_targets() -> tuple[float, float]:
    """The body's within-word and seam doublet rates, measured rather than typed."""
    words = load_tokenized().words()
    within = sum(w[i] == w[i + 1] for w in words for i in range(len(w) - 1))
    pairs = sum(len(w) - 1 for w in words)
    seam = sum(a[-1] == b[0] for a, b in zip(words, words[1:], strict=False))
    return within / pairs, seam / (len(words) - 1)


def inverse(p: Perm) -> Perm:
    q = [0] * M
    for i, v in enumerate(p):
        q[v] = i
    return q


def square_step(order: list[int]) -> Perm:
    """Down one row in a 5x5 square filled row-major with order[:25]; the rest fixed."""
    g = list(range(M))
    for col in range(5):
        column = [order[r * 5 + col] for r in range(5)]
        for r in range(5):
            g[column[r]] = column[(r + 1) % 5]
    return g


def relation_rate(pairs: list[tuple[int, int]], rel: Perm) -> float:
    """Doublet rate when c_j == c_{j+1} iff p_j == rel[p_{j+1}]."""
    return sum(1 for a, b in pairs if a == rel[b]) / len(pairs)


def relations(
    pairs: list[tuple[int, int]],
    freq: collections.Counter[int],
    rng: random.Random,
    target: float,
) -> None:
    rate = lambda rel: relation_rate(pairs, rel)  # noqa: E731
    rows: list[tuple[str, float, str]] = []
    best = min((rate([(b + s) % M for b in range(M)]), s) for s in range(1, M))
    rows.append(
        (
            "shift by s (Trithemius, progressive Beaufort), best of 28",
            best[0],
            f"s={best[1]}",
        )
    )
    best = min((rate([(r * b) % M for b in range(M)]), r) for r in range(2, M))
    rows.append(("multiply by r in GF(29), best of 27", best[0], f"r={best[1]}"))
    ks = [k for k in range(2, 28) if math.gcd(k, 28) == 1]
    best = min((rate([pow(b, k, M) if b else 0 for b in range(M)]), k) for k in ks)
    rows.append(("power map b^k on GF(29)*, best of 11", best[0], f"k={best[1]}"))
    affine = sorted(
        (rate([(a * b + s) % M for b in range(M)]), a, s)
        for a in range(1, M)
        for s in range(M)
        if (a, s) != (1, 0)
    )
    rows.append(
        (
            "affine a*b+s, best of 811",
            affine[0][0],
            f"a={affine[0][1]} s={affine[0][2]}; median {affine[len(affine) // 2][0]:.4f}",
        )
    )
    rows.append(("atbash b -> 28-b", rate([M - 1 - b for b in range(M)]), ""))
    futhark = list(range(M))
    byfreq = [r for r, _ in freq.most_common()] + [r for r in range(M) if r not in freq]
    unused = [r for r in range(M) if freq[r] <= 3]
    fills = (
        ("Futhark order, row-major", futhark),
        (
            "Futhark order, column-major",
            [futhark[(i % 5) * 5 + i // 5] for i in range(25)] + futhark[25:],
        ),
        ("frequency order, row-major", byfreq),
        (
            "used runes in Futhark order, the unused four outside",
            [r for r in futhark if r not in unused] + unused,
        ),
    )
    for label, order in fills:
        g = square_step(order)
        rows.append(
            (
                f"5x5 square step, {label}",
                min(rate(g), rate(inverse(g))),
                f"other direction {max(rate(g), rate(inverse(g))):.4f}",
            )
        )
    squares = sorted(
        min(rate(g), rate(inverse(g)))
        for g in (square_step(rng.sample(range(M), M)) for _ in range(4000))
    )
    rows.append(
        (
            "random 5x5 square, median of 4,000",
            squares[2000],
            f"share at or below the body: {sum(x <= target for x in squares) / 4000:.2%}",
        )
    )
    perms = sorted(rate(rng.sample(range(M), M)) for _ in range(20000))
    rows.append(
        (
            "random permutation, median of 20,000",
            perms[10000],
            f"share at or below the body: {sum(x <= target for x in perms) / 20000:.2%}; minimum {perms[0]:.4f}",
        )
    )

    print(f"{'relation R: doublet iff p_j == R(p_j+1)':<64}{'rate':>8}  note")
    reach = 0
    for name, r, note in rows:
        print(f"{name:<64}{r:>8.4f}  {note}")
        reach += r <= target * 1.5 and "random" not in name
    print(
        f"natural relations within 1.5x of the body's {target:.4f}: {reach} of {len(rows) - 2} (affine and power maps, which have no element of order 5)"
    )


def autokeys(
    words: list[list[int]], freq: collections.Counter[int], total: int
) -> None:
    tri = [(w[i - 1], w[i], w[i + 1]) for w in words for i in range(1, len(w) - 1)]
    quad = [(w[i - 2], w[i + 1]) for w in words for i in range(2, len(w) - 1)]
    print(
        f"Vigenere plaintext autokey  c = p_j + p_j-1: doublet iff p_j+1 == p_j-1:    {sum(a == c for a, _, c in tri) / len(tri):.4f}"
    )
    print(
        f"Beaufort plaintext autokey  c = p_j-1 - p_j: doublet iff p_j+1 == 2p_j - p_j-1: {sum(c == (2 * b - a) % M for a, b, c in tri) / len(tri):.4f}"
    )
    print(
        f"second-order autokey        c = p_j + p_j-1 + p_j-2: doublet iff p_j+1 == p_j-2: {sum(a == b for a, b in quad) / len(quad):.4f}"
    )
    rarest = min(range(M), key=lambda r: freq[r])
    print(
        f"ciphertext autokey          c = p_j + c_j-1: doublet iff p_j+1 is the identity: F {freq[0] / total:.4f}, rarest {NAMES[rarest]} {freq[rarest] / total:.4f}"
    )
    print(
        "(the preceding-rune split excludes ciphertext autokey outright, `ciphertext-autokey.md`)"
    )


def chaocipher(
    words: list[list[int]], left: list[int], right: list[int]
) -> list[list[int]]:
    left, right = list(left), list(right)
    nadir = M // 2
    out = []
    for w in words:
        cw = []
        for p in w:
            i = right.index(p)
            cw.append(left[i])
            left = left[i:] + left[:i]
            left.insert(nadir, left.pop(1))
            right = right[i:] + right[:i]
            right = right[1:] + right[:1]
            right.insert(nadir, right.pop(2))
        out.append(cw)
    return out


def self_organizing(words: list[list[int]], *, move_to_front: bool) -> list[list[int]]:
    """The index of each rune in a list that mutates after use; a per-word base after it changes no rate here."""
    lst = list(range(M))
    out = []
    for w in words:
        cw = []
        for p in w:
            i = lst.index(p)
            cw.append(i)
            if move_to_front:
                lst.insert(0, lst.pop(i))
            elif i:
                lst[i - 1], lst[i] = lst[i], lst[i - 1]
        out.append(cw)
    return out


def profile(words: list[list[int]]) -> tuple[float, float, float, list[float]]:
    stream = [r for w in words for r in w]
    doublets = sum(a == b for a, b in zip(stream, stream[1:], strict=False)) / (
        len(stream) - 1
    )
    counts = collections.Counter(stream)
    n = len(stream)
    nioc = M * sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))
    lags = []
    for lag in range(1, 7):
        hits = sum(w[i] == w[i + lag] for w in words for i in range(len(w) - lag))
        pairs = sum(max(0, len(w) - lag) for w in words)
        lags.append(M * hits / pairs)
    seam = sum(a[-1] == b[0] for a, b in zip(words, words[1:], strict=False)) / (
        len(words) - 1
    )
    return doublets, seam, nioc, lags


def machines(reg: list[list[int]], rng: random.Random, n_words: int) -> None:
    words: list[list[int]] = []
    while len(words) < n_words:
        block = list(reg)
        rng.shuffle(block)
        words += block
    words = words[:n_words]
    runs = (
        ("plaintext itself", words),
        (
            "Chaocipher-29, Futhark alphabets",
            chaocipher(words, list(range(M)), list(range(M))),
        ),
        (
            "Chaocipher-29, random alphabets",
            chaocipher(words, rng.sample(range(M), M), rng.sample(range(M), M)),
        ),
        ("move-to-front list", self_organizing(words, move_to_front=True)),
        ("transpose-forward list", self_organizing(words, move_to_front=False)),
    )
    print(
        f"{'machine, on the register with word order shuffled':<42}{'doublets':>9}{'seam':>8}{'nIoC':>7}  within-word lags 1..6 (x chance)"
    )
    for name, ct in runs:
        d, seam, nioc, lags = profile(ct)
        print(
            f"{name:<42}{d:>9.4f}{seam:>8.4f}{nioc:>7.3f}  "
            + " ".join(f"{x:.2f}" for x in lags)
        )
    print(
        "every machine sits at chance on doublets and shows no lag-5 echo; the lists are not even flat"
    )


def homophones(freq: collections.Counter[int], total: int) -> None:
    unused = [NAMES[r] for r in range(M) if freq[r] <= 3]
    print(f"runes the author writes three times or fewer in {total} runes: {unused}")
    cum = 0.0
    for k, (_, c) in enumerate(freq.most_common(10), 1):
        cum += c / total
        if k in (4, 5, 7, 10):
            print(
                f"  {k} spare symbols as homophones of the {k} commonest letters: phi <= {cum:.2f}"
            )
    print(
        "the body needs phi about 0.90 (`how_strong_is_the_preventer.py`); a null symbol instead gives 1 - 1/29 = 0.966"
    )


def main() -> None:
    rng = random.Random(3301)
    reg = register()
    pairs = [(w[i], w[i + 1]) for w in reg for i in range(len(w) - 1)]
    freq = collections.Counter(r for w in reg for r in w)
    total = sum(freq.values())
    within, seam = body_targets()
    print(
        f"register: {len(reg)} words, {total} runes, {len(pairs)} within-word pairs; chance {1 / M:.4f}; body within {within:.4f}, seam {seam:.4f}"
    )
    print(
        f"plaintext doublets as written: {relation_rate(pairs, list(range(M))):.4f}\n"
    )
    relations(pairs, freq, rng, within)
    print()
    autokeys(reg, freq, total)
    print()
    machines(reg, rng, 2928)
    print()
    homophones(freq, total)


if __name__ == "__main__":
    main()
