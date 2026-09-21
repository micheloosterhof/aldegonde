# ABOUTME: Searches directly for the rune partition an intransitive block cipher would
# ABOUTME: leave behind, closing the few-block gap the block-bigram leak test cannot reach.
"""The intransitive escape is open at four blocks or fewer. This closes it.

`rotor-machine-compact-state.md` prices intransitivity: if the base group never mixes
certain runes, the runes split into blocks and the cipher becomes hand-runnable again.
Block membership passes through untouched -- a plaintext rune and its ciphertext always
share a block -- so the plaintext's block-level structure is deposited in the ciphertext
whatever the wiring.

That file tests the consequence one block SHAPE at a time, against a fixed partition
implied by the shape, and finds the test loses all power below five blocks: the leak a
2- to 4-block machine would deposit is smaller than the surrogate's own noise. The
conclusion recorded there is "untested", not "excluded".

The reason for the power loss is the degrees of freedom, not the effect. A k-block
partition reduces the 29x29 bigram table to k x k, which at k = 2 is one degree of
freedom. But the partition itself was never searched. Turn it round: instead of asking
whether a NAMED partition leaks, ask whether ANY partition does.

    for each k in 2, 3, 4:
        maximise the block-sequence mutual information over all assignments
        of the 29 runes to k blocks

and compare the maximum against the same optimisation run on doublet-preserving
surrogates. A real block cipher has a partition that scores far above anything the
optimiser can find in structureless text; if the observed maximum sits inside the
surrogate distribution, no partition of that size exists.

The surrogate must preserve the doublet deficit. Lag-1 block structure is exactly what
the deficit produces, and calibrating against a plain shuffle would report the
suppression as a block signal -- the trap `bigram-ioc.md` documents.

Power is measured by planting block ciphers over the LP's own plaintext and running the
same optimiser. It depends on WHICH runes a partition groups, not only on how many
blocks there are, so it is quoted as a detection rate over random partitions of each
shape rather than as a single number.

    python block_partition_search.py [--blocks 2,3,4] [--surrogates 20] [--control]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

M = 29
LAGS = (1, 2, 3)


def within_word_pairs(stream: list[int], wid: list[int]) -> dict[int, np.ndarray]:
    """Index pairs (i, j) of runes in the same word, one array per lag."""
    out = {}
    for lag in LAGS:
        a, b = [], []
        for i in range(len(stream) - lag):
            if wid[i] == wid[i + lag]:
                a.append(stream[i])
                b.append(stream[i + lag])
        out[lag] = np.array([a, b], dtype=np.int64)
    return out


def mutual_information(assign: np.ndarray, pairs: dict[int, np.ndarray], k: int) -> float:
    """Summed G^2 of the block-pair tables over the lags, in nats."""
    total = 0.0
    for arr in pairs.values():
        ba, bb = assign[arr[0]], assign[arr[1]]
        tab = np.zeros((k, k))
        np.add.at(tab, (ba, bb), 1.0)
        n = tab.sum()
        if n == 0:
            continue
        exp = np.outer(tab.sum(1), tab.sum(0)) / n
        mask = tab > 0
        total += 2.0 * float((tab[mask] * np.log(tab[mask] / exp[mask])).sum())
    return total


def optimise(pairs: dict[int, np.ndarray], k: int, rng: random.Random,
             restarts: int = 12) -> tuple[float, np.ndarray]:
    """Best G^2 over assignments, by restarts plus greedy single-rune moves."""
    best, best_a = -1.0, None
    for _ in range(restarts):
        a = np.array([rng.randrange(k) for _ in range(M)], dtype=np.int64)
        score = mutual_information(a, pairs, k)
        improved = True
        while improved:
            improved = False
            for r in range(M):
                cur = a[r]
                for v in range(k):
                    if v == cur:
                        continue
                    a[r] = v
                    s = mutual_information(a, pairs, k)
                    if s > score + 1e-9:
                        score, cur, improved = s, v, True
                    else:
                        a[r] = cur
        if score > best:
            best, best_a = score, a.copy()
    return best, best_a


def doublet_preserving_shuffle(stream: list[int], rng: random.Random) -> list[int]:
    """Reorder the runes but keep the within-word doublet count, by rejecting swaps
    that create or destroy an adjacent equal pair."""
    s = stream[:]
    n = len(s)
    for _ in range(8 * n):
        i, j = rng.randrange(n), rng.randrange(n)
        if i == j or s[i] == s[j]:
            continue
        before = _local_doublets(s, i) + _local_doublets(s, j)
        s[i], s[j] = s[j], s[i]
        if _local_doublets(s, i) + _local_doublets(s, j) != before:
            s[i], s[j] = s[j], s[i]
    return s


def _local_doublets(s: list[int], i: int) -> int:
    d = 0
    if i and s[i - 1] == s[i]:
        d += 1
    if i + 1 < len(s) and s[i] == s[i + 1]:
        d += 1
    return d


def main() -> None:
    blocks = [2, 3, 4]
    nsur = 20
    for i, a in enumerate(sys.argv):
        if a == "--blocks" and i + 1 < len(sys.argv):
            blocks = [int(x) for x in sys.argv[i + 1].split(",")]
        if a == "--surrogates" and i + 1 < len(sys.argv):
            nsur = int(sys.argv[i + 1])

    rng = random.Random(3301)
    stream, wid = load_clean()

    if "--control" in sys.argv:
        from lp_plaintext_register import corpus  # noqa: PLC0415

        words = corpus()
        for k, sizes in ((2, [25, 4]), (4, [10, 9, 5, 5])):
            part = []
            for b, sz in enumerate(sizes):
                part += [b] * sz
            rng.shuffle(part)
            part = np.array(part)
            members = [np.flatnonzero(part == b).tolist() for b in range(k)]
            cs, cw = [], []
            for w, word in enumerate(words * 6):
                perm = list(range(M))
                for mem in members:
                    sh = mem[:]
                    rng.shuffle(sh)
                    for src, dst in zip(mem, sh):
                        perm[src] = dst
                for r in word:
                    cs.append(perm[r])
                    cw.append(w)
            pairs = within_word_pairs(cs, cw)
            sc, _a = optimise(pairs, k, rng, restarts=6)
            print(f"PLANTED {k}-block cipher, sizes {sizes}: best G^2 {sc:,.1f}")
        return

    pairs = within_word_pairs(stream, wid)
    print(f"body: {len(stream):,} runes, within-word pairs at lags {LAGS}")
    print(f"{'k':>3}{'observed G^2':>15}{'surrogate mean':>16}{'sd':>8}{'z':>8}")
    for k in blocks:
        obs, assign = optimise(pairs, k, rng)
        sur = []
        for _ in range(nsur):
            sh = doublet_preserving_shuffle(stream, rng)
            sur.append(optimise(within_word_pairs(sh, wid), k, rng, restarts=4)[0])
        mu = sum(sur) / len(sur)
        sd = (sum((x - mu) ** 2 for x in sur) / len(sur)) ** 0.5
        z = (obs - mu) / sd if sd else 0.0
        print(f"{k:>3}{obs:>15.1f}{mu:>16.1f}{sd:>8.1f}{z:>+8.2f}")
        sizes = sorted(int((assign == b).sum()) for b in range(k))
        print(f"     best partition sizes {sizes}")


if __name__ == "__main__":
    main()
