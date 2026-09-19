# ABOUTME: Tests word-level base-indexing schemes on NEARBY word pairs only, so that a
# ABOUTME: compact clock disturbed by occasional interrupts is not averaged away.
"""A compact state with interrupts survives a global bucket test. Does it survive a local one?

`word_state_sweep.py` buckets every rune by a visible state S (word index,
cumulative length, ...) modulo m and pools ALL pairs in a bucket. If the alphabet is
a function of S, pairs in a bucket coincide at the plaintext rate (~0.06, not 1/29).
That test assumes the solver can compute S exactly. 3301's own solved pages break
that assumption: their key streams skip at certain plaintext F's. One interrupt
shifts the true clock by one for the rest of the text, so bucket-mates far apart stop
sharing an alphabet and the pooled coincidence falls back to chance -- while
bucket-mates a few words apart still share it.

So this sweep counts coincidences only between runes at most D words apart (and in
different words, which keeps the within-word d5 echo out). A compact clock with rare
interrupts shows as a coincidence rate that RISES as D shrinks.

Run with no arguments for the planted control (a letter-clocked disk with one
interrupt per ~40 words must be invisible globally and visible locally). `--run`
sweeps the unsolved corpus. `--family` scans the 29 disks turned a fixed amount per
letter and per space, (A + beta*w) mod 29, and stress-tests the strongest.

**Result (2026-09-19).** `--run`: 3,058 cells, strongest z = +3.37, which is what
that many cells give by chance. `--family`: the 29 members scatter like a standard
normal (sd 1.18 with the strongest included) and the strongest is beta = 28, the clock A - w = the number of letter
steps so far (the walk's own increment): 969 of 25,144 pairs within 60 words,
rate 0.0385 against 0.0345, z = +3.52. It holds in both halves of the corpus
(+2.77, +1.86), beats every one of 200 clocks built from shuffled word lengths
(max +2.55), and does not come from page layout. As the largest of 58 family cells
(two phase conventions) it is p ~ 0.013. The digraph check does not confirm it: 28
double matches against 20.1 +- 4.8, z = +1.6, where full alphabet sharing at the
monograph rate would give about 49. Read: a weak watch-item. If real it is a
partial effect of about 6-10%, not a clock that indexes the alphabet.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from ea_direction_test import PROSE_CACHE  # noqa: E402
from quagmire_runner import load_register  # noqa: E402
from word_state_sweep import load_rich, state_functions  # noqa: E402

N = 29
CHANCE = 1.0 / N
REACHES = (10, 30, 100)  # word distances
MAX_WORD_RUNES = 14


def local_coincidence(a: dict[str, np.ndarray], codes: np.ndarray, keys: np.ndarray):
    """{reach: (hits, pairs)} over rune pairs in different words with equal key."""
    words = a["w"]
    out = {reach: [0, 0] for reach in REACHES}
    for lag in range(2, max(REACHES) * MAX_WORD_RUNES):
        gap = words[lag:] - words[:-lag]
        if gap.min() > max(REACHES):
            break
        same_key = keys[lag:] == keys[:-lag]
        equal = codes[lag:] == codes[:-lag]
        for reach in REACHES:
            mask = same_key & (gap >= 1) & (gap <= reach)
            out[reach][0] += int((mask & equal).sum())
            out[reach][1] += int(mask.sum())
    return out


def z_score(hits: int, pairs: int) -> float:
    return (
        (hits - pairs * CHANCE) / math.sqrt(pairs * CHANCE * (1 - CHANCE))
        if pairs
        else 0.0
    )


def sweep(a: dict[str, np.ndarray], codes: np.ndarray):
    rows = []
    moduli = range(2, 61)
    for name, state in state_functions(a).items():
        for m in [int(state.max()) + 1] if name in ("L", "prevL") else moduli:
            for phase_name, phase in (("reset", a["j"] % 5), ("cont", a["i"] % 5)):
                keys = (state % m) * 5 + phase
                for reach, (hits, pairs) in local_coincidence(a, codes, keys).items():
                    if pairs >= 2000:
                        rows.append(
                            (
                                z_score(hits, pairs),
                                name,
                                m,
                                phase_name,
                                reach,
                                hits,
                                pairs,
                            )
                        )
    return sorted(rows, reverse=True)


def planted(a: dict[str, np.ndarray], rng: random.Random) -> np.ndarray:
    """Prose under a letter-clocked disk whose clock slips once per ~40 words."""
    pools, _table, _floor = load_register(PROSE_CACHE)
    disk = rng.sample(range(N), N)
    g = list(range(N))
    points = rng.sample(range(N), 25)
    for c in range(5):
        cycle = points[5 * c : 5 * c + 5]
        for t in range(5):
            g[cycle[t]] = cycle[(t + 1) % 5]
    powers = [list(range(N))]
    for _ in range(4):
        powers.append([g[x] for x in powers[-1]])
    codes, slips, start = [], 0, 0
    for length in a["lens"]:
        slips += rng.random() < 1 / 40
        turn = (start + slips) % N
        word = rng.choice(pools[int(length)])[: int(length)]
        codes += [disk[(powers[j % 5][p] + turn) % N] for j, p in enumerate(word)]
        start += int(length)
    return np.asarray(codes)


def clock_stat(a, word_state: np.ndarray, reach: int, keep: np.ndarray | None = None):
    """(hits, pairs, digraph pairs, digraph hits) for the clock word_state mod 29.

    Pairs share (clock mod 29, within-word phase), lie in different words at most
    `reach` words apart, and optionally both lie in `keep`. A digraph pair is a pair
    whose successors sit in the same two words; it hits when both runes match.
    """
    codes, words = a["rune"], a["w"]
    keys = (word_state[words] % N) * 5 + a["j"] % 5
    has_next = np.zeros(len(codes), dtype=bool)
    has_next[:-1] = words[1:] == words[:-1]
    hits = pairs = di_pairs = di_hits = 0
    for lag in range(2, reach * MAX_WORD_RUNES):
        gap = words[lag:] - words[:-lag]
        mask = (keys[lag:] == keys[:-lag]) & (gap >= 1) & (gap <= reach)
        if keep is not None:
            mask &= keep[lag:] & keep[:-lag]
        equal = codes[lag:] == codes[:-lag]
        hits += int((mask & equal).sum())
        pairs += int(mask.sum())
        idx = np.nonzero(mask & has_next[lag:] & has_next[:-lag])[0]
        di_pairs += len(idx)
        di_hits += int((equal[idx] & (codes[idx + 1] == codes[idx + lag + 1])).sum())
    return hits, pairs, di_pairs, di_hits


def family(a: dict[str, np.ndarray], reach: int = 60, draws: int = 200) -> None:
    """The disk family (A + beta*w) mod 29, then the checks on its strongest member."""
    lens = a["lens"]
    n_words = len(lens)
    starts = np.concatenate([[0], np.cumsum(lens)[:-1]])
    rows = []
    for beta in range(N):
        hits, pairs, _dp, _dh = clock_stat(a, starts + beta * np.arange(n_words), reach)
        rows.append((z_score(hits, pairs), beta, hits, pairs))
    zs = np.array([r[0] for r in rows])
    print(f"clock (A + beta*w) mod 29, phase reset, pairs within {reach} words")
    print(f"  29 members: mean z {zs.mean():+.2f}, sd {zs.std():.2f}")
    for z, beta, hits, pairs in sorted(rows, reverse=True)[:3]:
        print(f"  beta {beta:>2}: {hits}/{pairs} = {hits / pairs:.4f}, z = {z:+.2f}")
    beta = max(rows)[1]
    clock = starts + beta * np.arange(n_words)
    hits, pairs, di_pairs, di_hits = clock_stat(a, clock, reach)
    half = a["w"] < n_words // 2
    for name, keep in (("first half", half), ("second half", ~half)):
        h, p, _dp, _dh = clock_stat(a, clock, reach, keep)
        print(f"  {name}: {h}/{p} = {h / p:.4f}, z = {z_score(h, p):+.2f}")
    rng = np.random.default_rng(3301)
    null_z, null_di = [], []
    for _ in range(draws):
        shuffled = rng.permutation(lens)
        fake = np.concatenate([[0], np.cumsum(shuffled)[:-1]]) + beta * np.arange(
            n_words
        )
        h, p, _dp, dh = clock_stat(a, fake, reach)
        null_z.append(z_score(h, p))
        null_di.append(dh)
    null_z, null_di = np.array(null_z), np.array(null_di)
    print(
        f"  clock built from shuffled word lengths ({draws} draws): z mean {null_z.mean():+.2f}, "
        f"sd {null_z.std():.2f}, max {null_z.max():+.2f}"
    )
    print(
        f"  digraphs: {di_hits} of {di_pairs} aligned pairs match on both runes; "
        f"shuffled clocks give {null_di.mean():.1f} +- {null_di.std():.1f} "
        f"(z = {(di_hits - null_di.mean()) / null_di.std():+.2f})"
    )


def main() -> None:
    a = load_rich()
    if "--family" in sys.argv:
        family(a)
        return
    if "--run" in sys.argv:
        rows = sweep(a, a["rune"])
        print(f"{len(rows)} cells; strongest 15 (chance rate {CHANCE:.4f}):\n")
        print(
            f"{'z':>6}  {'state':<10}{'mod':>4} {'phase':<6}{'reach':>6}{'rate':>8}{'pairs':>9}"
        )
        for z, name, m, phase, reach, hits, pairs in rows[:15]:
            print(
                f"{z:>6.2f}  {name:<10}{m:>4} {phase:<6}{reach:>6}{hits / pairs:>8.4f}{pairs:>9}"
            )
        return
    codes = planted(a, random.Random(3301))
    keys = (a["A"] % N) * 5 + a["j"] % 5
    local = local_coincidence(a, codes, keys)
    every = np.bincount(keys * N + codes)
    sizes = np.bincount(keys)
    global_rate = (every * (every - 1) // 2).sum() / (sizes * (sizes - 1) // 2).sum()
    print(
        f"planted slipping clock: global bucket rate {global_rate:.4f} (chance {CHANCE:.4f})"
    )
    for reach, (hits, pairs) in local.items():
        print(
            f"  within {reach:>3} words: rate {hits / pairs:.4f}, z = {z_score(hits, pairs):+.1f}"
        )
    near, far = local[REACHES[0]], local[REACHES[-1]]
    assert z_score(*near) > 6, "local test misses a planted slipping clock"
    assert near[0] / near[1] > far[0] / far[1], "rate should rise as the reach shrinks"
    assert global_rate < CHANCE * 1.1, (
        "the control should be invisible to the global test"
    )
    print("planted control passed")


if __name__ == "__main__":
    main()
