# ABOUTME: Scores a ciphertext autokey whose identity element is a rune the plaintext never
# ABOUTME: uses, through a per-word mixed alphabet, on the body's cells and the preceding-rune split.
"""A ciphertext autokey with a dead identity rune produces no doublets by construction.

    c_j = K_w( K_w^-1(c_{j-1}) + p_j - e )          decrypt: p_j = K_w^-1(c_j) - K_w^-1(c_{j-1}) + e

A doublet needs p_j = e. If e is a rune the plaintext never writes (the author's register
has J, EO, OE, AE at five occurrences in 2,882 runes), the cipher emits no doublet and no
triplet, inside words or at seams, with no rule and no tuning. Feedback flattens the
unigrams on its own, so no large pool of bases is needed; a per-word key K_w is needed only
for the preceding-rune split (`ciphertext-autokey.md` excludes one fixed table), and a
per-word rotation of one mixed alphabet already brings the split's group nIoC near the
body's 1.026. The within-word lag cells become plaintext statistics, the mass of k-letter
sums landing on k·e, and depend on e; EO lands on the body's, J, OE and AE do not.

What the cipher cannot supply is the 86 doublets the page has; they must be runes written
twice, 0.66% of the stream.

    python experiments/dead_rune_autokey.py
"""

from __future__ import annotations

import collections
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from cipher_zoo_fingerprint import HEADER, fingerprint, plaintext, row  # noqa: E402
from lp_corpus import load_tokenized  # noqa: E402
from lp_plaintext_register import corpus as register  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
NAMES = c3301.CICADA_ENGLISH_ALPHABET
Words = list[list[int]]


def inverse(p: list[int]) -> list[int]:
    q = [0] * M
    for i, v in enumerate(p):
        q[v] = i
    return q


def split_ioc(words: Words) -> float:
    """Mean nIoC of the runes following each rune: 1.78 for one fixed table, 1.0 for none."""
    stream = [r for w in words for r in w]
    groups: dict[int, list[int]] = collections.defaultdict(list)
    for a, b in zip(stream, stream[1:], strict=False):
        groups[a].append(b)
    vals = []
    for g in groups.values():
        c = collections.Counter(g)
        n = len(g)
        vals.append(M * sum(v * (v - 1) for v in c.values()) / (n * (n - 1)))
    return sum(vals) / len(vals)


def autokey(words: Words, rng: random.Random, e: int, *, per_word: str) -> Words:
    key = rng.sample(range(M), M)
    prev = rng.randrange(M)
    out: Words = []
    for w_index, w in enumerate(words):
        if per_word == "mixed":
            kw = rng.sample(range(M), M)
        elif per_word == "dial":
            a = (w_index * 7) % M
            kw = [(key[x] + a) % M for x in range(M)]
        else:
            kw = key
        kwi = inverse(kw)
        cw = []
        for p in w:
            c = kw[(kwi[prev] + p - e) % M]
            cw.append(c)
            prev = c
        out.append(cw)
    return out


def written_twice(words: Words, n: int, rng: random.Random) -> Words:
    out = [list(w) for w in words]
    positions = [(i, j) for i, w in enumerate(out) for j in range(len(w))]
    for i, j in rng.sample(positions, n):
        out[i].insert(j, out[i][j])
    return out


def lag_cells(reg: Words, e: int) -> list[float]:
    cells = []
    for k in (2, 3, 4):
        hits = pairs = 0
        for w in reg:
            for j in range(len(w) - k):
                pairs += 1
                hits += sum(w[j + i] - e for i in range(1, k + 1)) % M == 0
        cells.append(M * hits / pairs)
    return cells


def main() -> None:
    rng = random.Random(3301)
    body = load_tokenized().words()
    plain = plaintext(rng, len(body))
    reg = register()
    counts = collections.Counter(r for w in reg for r in w)
    dead = [r for r in range(M) if counts[r] <= 3]
    print(
        "runes the author's plaintext writes three times or fewer:",
        [NAMES[r] for r in dead],
    )
    print(
        "\nwithin-word lag cells the autokey predicts for each identity rune (plaintext sums landing on k*e):"
    )
    print(f"{'e':<6}{'lag 2':>8}{'lag 3':>8}{'lag 4':>8}")
    body_fp = fingerprint(body)
    print(f"{'body':<6}{body_fp['d2']:>8.2f}{body_fp['d3']:>8.2f}{body_fp['d4']:>8.2f}")
    for r in dead:
        cells = lag_cells(reg, r)
        print(f"{NAMES[r]:<6}" + "".join(f"{x:>8.2f}" for x in cells))
    eo = NAMES.index("EO")
    print("\n" + HEADER + "  split")
    print(row("Liber Primus body", body_fp) + f"  {split_ioc(body):.3f}")
    for label, kind in (
        ("one fixed table (the disproved case)", "none"),
        ("one table, per-word rotation", "dial"),
        ("fresh mixed alphabet per word", "mixed"),
    ):
        fps, splits = [], []
        for _ in range(4):
            ct = autokey(plain, rng, eo, per_word=kind)
            fps.append(fingerprint(ct))
            splits.append(split_ioc(ct))
        mean = {k: sum(f[k] for f in fps) / 4 for k in fps[0]}
        print(row(f"autokey, identity EO, {label}", mean) + f"  {sum(splits) / 4:.3f}")
    fps, splits = [], []
    for _ in range(4):
        ct = written_twice(autokey(plain, rng, eo, per_word="dial"), 86, rng)
        fps.append(fingerprint(ct))
        splits.append(split_ioc(ct))
    mean = {k: sum(f[k] for f in fps) / 4 for k in fps[0]}
    print(
        row("same, per-word rotation, 86 runes written twice", mean)
        + f"  {sum(splits) / 4:.3f}"
    )
    print(
        "\nident is not comparable with the body's 17: the cycled plaintext repeats every word four times."
    )


if __name__ == "__main__":
    main()
