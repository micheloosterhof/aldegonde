# ABOUTME: Sweeps the linear autokey family (ciphertext and plaintext taps at lags
# ABOUTME: 1 and 5) to find which architectures can suppress d1 and d6 together.
"""Which autokey lag structure can fit the LP profile at all?

`dual-autokey-lag1-lag5.md` records a mixed-feedback cipher that reaches the
fitted cells and returns chance on every held-out distance. That is not a tuning
failure, it is what lag-1 ciphertext feedback does. Writing `D_j = c_j - c_{j-1}`,
the recursion makes `D_j` a function of the plaintext taps alone, so

    c_j - c_{j-d} = D_{j-d+1} + ... + D_j        (d consecutive terms)

At d = 1 that is ONE plaintext term: structured, and tunable to any rate. At
d >= 2 it is a sum of two or more near-independent values mod 29, and summing mod
29 convolves toward uniform. Every cell past d1 goes to chance by construction.

That is fatal here, because the LP's signature is d1 AND d6 both far below chance
(0.0063 and 0.0245) while d5 sits far above (0.0492). Distances 1 and 6 differ by
5, so a period-5 relation suppresses both with one mechanism; lag-1 feedback
cannot reach d6 at all.

So this sweeps the lag structure instead of the labelling:

    c_j = v(p_j) + a1*c_{j-1} + a5*c_{j-5} + b1*v(p_{j-1}) + b5*v(p_{j-5})

with each coefficient in {0, 1} and, for the survivors, the per-word reset variant
Michel proposed (ciphertext feedback continuous across words, plaintext tap
restarting).

The scoring separates ARCHITECTURE from TUNING, which is the lesson of the
retraction in `dual-autokey-lag1-lag5.md`: a single labelling's number says
nothing. Each architecture is run over many RANDOM labellings and reported as a
reachable range. An architecture is only interesting if the LP's (d1, d5, d6)
sits inside the range it reaches without design.
"""

from __future__ import annotations

import random
from collections import Counter

import numpy as np

from experiments.d5_unit_model import dict_words
from experiments.walk_verifier import load_words

M = 29
SEED = 3301
NLAB = 48
TARGET_RUNES = 60000

LP = {
    1: 0.0063,
    2: 0.0347,
    3: 0.0370,
    4: 0.0410,
    5: 0.0492,
    6: 0.0245,
}
LP_SEAM = 0.0079


def build_plaintext(rng: random.Random) -> tuple[np.ndarray, np.ndarray]:
    """Runeglish words at the LP length histogram, as a flat stream plus starts."""
    lp_hist = Counter(len(w) for w in load_words())
    by_len = dict_words()
    words: list[list[int]] = []
    total = 0
    while total < TARGET_RUNES:
        for length, count in lp_hist.items():
            pool = by_len.get(length)
            if not pool:
                continue
            for _ in range(count):
                words.append(pool[rng.randrange(len(pool))])
                total += length
            if total >= TARGET_RUNES:
                break
    rng.shuffle(words)
    stream: list[int] = []
    starts: list[int] = []
    for w in words:
        starts.append(len(stream))
        stream += w
    return np.array(stream, dtype=np.int64), np.array(starts, dtype=np.int64)


def encipher(
    p: np.ndarray,
    starts: np.ndarray,
    labels: np.ndarray,
    a1: int,
    a5: int,
    b1: int,
    b5: int,
    *,
    pt_reset: bool,
) -> np.ndarray:
    """Vectorised over labellings: labels has shape (nlab, 29), returns (nlab, n)."""
    n = len(p)
    nlab = labels.shape[0]
    word_start = np.zeros(n, dtype=np.int64)
    cur = 0
    starts_set = set(starts.tolist())
    for j in range(n):
        if j in starts_set:
            cur = j
        word_start[j] = cur

    val = labels[:, p]  # (nlab, n)
    c = np.zeros((nlab, n), dtype=np.int64)
    for j in range(n):
        acc = val[:, j].copy()
        if a1 and j >= 1:
            acc += c[:, j - 1]
        if a5 and j >= 5:
            acc += c[:, j - 5]
        if b1 and j >= 1 and (not pt_reset or j - 1 >= word_start[j]):
            acc += val[:, j - 1]
        if b5 and j >= 5 and (not pt_reset or j - 5 >= word_start[j]):
            acc += val[:, j - 5]
        c[:, j] = acc % M
    return c


def profile(c: np.ndarray, p: np.ndarray, starts: np.ndarray) -> np.ndarray:
    """Within-word rates d1..d6 plus the seam rate, per labelling."""
    n = c.shape[1]
    word_id = np.zeros(n, dtype=np.int64)
    word_id[starts] = 1
    word_id = np.cumsum(word_id) - 1

    out = np.zeros((c.shape[0], 7))
    for d in range(1, 7):
        same = word_id[: n - d] == word_id[d:]
        if not same.any():
            continue
        eq = c[:, : n - d] == c[:, d:]
        out[:, d - 1] = (eq & same).sum(axis=1) / same.sum()
    seam = starts[starts > 0]
    out[:, 6] = (c[:, seam - 1] == c[:, seam]).mean(axis=1)
    return out


def main() -> None:
    rng = random.Random(SEED)
    p, starts = build_plaintext(rng)
    print(f"plaintext: {len(p)} runes, {len(starts)} words at the LP histogram")
    print(f"chance = {1 / M:.4f}\n")
    print("LP target:  " + "  ".join(f"d{d} {LP[d]:.4f}" for d in range(1, 7)))
    print(f"            seam {LP_SEAM:.4f}\n")

    nrng = np.random.default_rng(SEED)
    labels = np.array([nrng.permutation(M) for _ in range(NLAB)])

    archs = []
    for a1 in (0, 1):
        for a5 in (0, 1):
            for b1 in (0, 1):
                for b5 in (0, 1):
                    if a1 == a5 == b1 == b5 == 0:
                        continue
                    archs.append((a1, a5, b1, b5))

    print(
        f"{'a1':>3}{'a5':>3}{'b1':>3}{'b5':>3}   "
        + "".join(f"{'d' + str(d):>16}" for d in (1, 5, 6))
    )
    print(f"{'':>12}   " + "".join(f"{'mean [min,max]':>16}" for _ in range(3)))
    hits = []
    for a1, a5, b1, b5 in archs:
        c = encipher(p, starts, labels, a1, a5, b1, b5, pt_reset=False)
        prof = profile(c, p, starts)
        cells = []
        inside = True
        for d in (1, 5, 6):
            col = prof[:, d - 1]
            cells.append(f"{col.mean():.4f}[{col.min():.3f},{col.max():.3f}]")
            if not (col.min() <= LP[d] <= col.max()):
                inside = False
        mark = "  <== reaches d1,d5,d6" if inside else ""
        print(
            f"{a1:>3}{a5:>3}{b1:>3}{b5:>3}   "
            + "".join(f"{x:>16}" for x in cells)
            + mark
        )
        if inside:
            hits.append((a1, a5, b1, b5))

    print("\nReachable range is over 48 RANDOM labellings -- what the architecture")
    print("does without design. Tuning can push a cell past this range, but an")
    print("architecture that cannot even bracket the LP without design is the")
    print("wrong shape, and one that brackets it is only a candidate.")

    if not hits:
        print("\nNo architecture in the family brackets d1, d5 and d6 together.")
        print("Diagnostic -- how each lag structure behaves at d >= 2:")
        for a1, a5, b1, b5 in [(1, 0, 0, 1), (1, 0, 1, 0), (0, 1, 1, 0), (1, 1, 0, 0)]:
            c = encipher(p, starts, labels, a1, a5, b1, b5, pt_reset=False)
            prof = profile(c, p, starts)
            tag = f"a1={a1} a5={a5} b1={b1} b5={b5}"
            print(
                f"   {tag:24} "
                + "  ".join(f"d{d} {prof[:, d - 1].mean():.4f}" for d in range(1, 7))
            )
        print(f"\n   chance is {1 / M:.4f}; a cell pinned there is the convolution,")
        print("   not a tuning shortfall.")
    else:
        print(f"\ncandidates: {hits}")


if __name__ == "__main__":
    main()
