# ABOUTME: Sweeps the walk with a per-word plaintext shift over two-keyword keys, using
# ABOUTME: the DIVINITY WITHIN crib as a base-free filter on sigma before scoring.
"""Two keywords instead of one, paid for by the opening crib.

`walk_shift_sweep.py` builds g and sigma from the same keyword, 1.8e7 keys. With sigma
from a second keyword the family is 1,264 times larger and cannot be scored. The
opening title can pay for it: the first two blocks are 8 and 5 runes, the runeglish
lengths of DIVINITY and WITHIN, and the red ink covers exactly those 13 runes
(`crib_divinity_within.py`). Under the shifted walk

    c_j = base_0( g^j( p_j + s_0 ) )                  word 0, s_0 = a_0
    c'_j = base_0( g^2 sigma g^j( p'_j + s_1 ) )      word 1, s_1 = a_0 +- 1, (8-1) mod 5 = 2

and base_0 is a bijection, so the arguments must agree exactly where the ciphertext
runes agree and differ where they differ. The two words share runes at positions
(0, 0) and (2, 2), which pins sigma at two points; the other three positions of
word 1 exclude eight values each. That leaves about one sigma in 800 of the family,
base-free and before any scoring, at the cost of trusting the crib and of the
preventer not firing inside those two words (about one chance in four that it does).

`--selftest` plants a two-keyword key with the crib in place and must recover it;
`--run` sweeps g from every priority keyword against sigma from every priority
keyword.
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import log_frequencies, powers  # noqa: E402
from walk_shift_kernel import Windows, schedule_shifts, score_sigmas  # noqa: E402
from walk_shift_sweep import (  # noqa: E402
    KEEP,
    SPANS,
    encipher_dir,
    grid_steps,
    keyed_alphabets,
    sigma_family,
)

from aldegonde import c3301  # noqa: E402
from aldegonde.maths import permutation  # noqa: E402

M = 29
OUT = ROOT / "experiments" / "walk_shift_crib_candidates.jsonl"
CRIB = [c3301.encode_english("DIVINITY"), c3301.encode_english("WITHIN")]
assert [len(w) for w in CRIB] == [8, 5]


class SigmaIndex:
    """The sigma family with an index on (point, image), for two-point lookups."""

    def __init__(self, sigmas: np.ndarray) -> None:
        self.sigmas = np.ascontiguousarray(sigmas, dtype=np.int8)
        self.by_point = [[None] * M for _ in range(M)]
        for x in range(M):
            col = self.sigmas[:, x]
            for y in range(M):
                self.by_point[x][y] = np.nonzero(col == y)[0]

    def matching(self, pins: list[tuple[int, int]], excluded: list[tuple[int, set]]):
        """Indices of sigmas with sigma(x) = y for every pin and sigma(x) not in E."""
        idx = np.arange(len(self.sigmas))
        for x, y in pins:
            idx = np.intersect1d(idx, self.by_point[x][y], assume_unique=True)
        if len(idx) == 0:
            return idx
        keep = np.ones(len(idx), dtype=bool)
        for x, bad in excluded:
            keep &= ~np.isin(self.sigmas[idx, x], list(bad))
        return idx[keep]


def crib_conditions(g, a0: int, direction: int, cipher0, cipher1):
    """(pins, exclusions) on sigma from the crib, or None if g and a0 are refuted.

    base_0 is a bijection, so within word 0 two positions carry the same ciphertext
    rune exactly when their arguments agree; the same holds across both words for
    the arguments after sigma and g^2.
    """
    gp = [permutation.power(g, k) for k in range(5)]
    g2inv = permutation.inverse(gp[2])
    s0, s1 = a0 % M, (a0 + direction) % M
    A = [gp[i % 5][(p + s0) % M] for i, p in enumerate(CRIB[0])]
    B = [gp[j % 5][(p + s1) % M] for j, p in enumerate(CRIB[1])]
    for args, cipher in ((A, cipher0), (B, cipher1)):
        forward: dict[int, int] = {}
        backward: dict[int, int] = {}
        for x, c in zip(args, cipher):
            if forward.setdefault(x, c) != c or backward.setdefault(c, x) != x:
                return None
    targets = {c: g2inv[a] for c, a in zip(cipher0, A)}  # sigma(B_j) must hit this
    all_targets = set(targets.values())
    pins, excluded = [], []
    for j, c in enumerate(cipher1):
        if c in targets:
            pins.append((B[j], targets[c]))
        else:
            excluded.append((B[j], all_targets))
    return pins, excluded


def sweep(
    g_words, sigma_words, body_words, logf, *, keep: int = KEEP, log_every: int = 50
):
    family = np.concatenate([sigma_family(K) for _, K in keyed_alphabets(sigma_words)])
    family = np.unique(family, axis=0)
    index = SigmaIndex(family)
    cipher0, cipher1 = body_words[0], body_words[1]
    windows = {}
    best: list[tuple[float, str, str, list[int], int, int]] = []
    tested = refuted = triples = 0
    start = time.time()
    for n, (kname, K) in enumerate(keyed_alphabets(g_words), 1):
        for gname, g in grid_steps(K):
            perms = powers(g)
            for direction in (+1, -1):
                for a0 in range(M):
                    triples += 1
                    cond = crib_conditions(g, a0, direction, cipher0, cipher1)
                    if cond is None:
                        refuted += 1
                        continue
                    idx = index.matching(*cond)
                    if len(idx) == 0:
                        continue
                    key = (a0, direction)
                    if key not in windows:
                        windows[key] = Windows(
                            [body_words[a:b] for a, b in SPANS],
                            schedule_shifts(SPANS, a0, direction),
                        )
                    scores = score_sigmas(perms, family[idx], windows[key], logf)
                    tested += len(idx)
                    top = int(scores.argmax())
                    best.append(
                        (
                            float(scores[top]),
                            kname,
                            gname,
                            [int(x) for x in family[idx[top]]],
                            a0,
                            direction,
                        )
                    )
                    best.sort(reverse=True)
                    del best[keep:]
        if n % log_every == 0:
            print(
                f"  {n} g-alphabets, {triples:,} (g, a0) triples, {refuted:,} refuted by "
                f"word 0, {tested:,} sigmas scored, best {best[0][0]:+.4f} "
                f"({best[0][1]} {best[0][2]}), {(time.time() - start) / 60:.1f} min",
                flush=True,
            )
    return best, tested, triples, refuted, len(family)


def selftest() -> None:
    from pure_quagmire_restart import matched_register  # noqa: PLC0415
    from quagmire_runner import PROSE_CACHE, load_register  # noqa: PLC0415
    from walk_shift_sweep import _lens  # noqa: PLC0415

    rng = random.Random(3301)
    pools, _t, _f = load_register(PROSE_CACHE)
    lens = _lens()
    plain = [list(CRIB[0]), list(CRIB[1])] + matched_register(rng, lens[2:], pools)
    g_words = ["DIVINITY", "WITHIN", "PARABLE", "WISDOM"]
    sigma_words = ["PILGRIM", "CIRCUMFERENCE", "PRIMES", "INSTAR"]
    _kname, K = list(keyed_alphabets(g_words))[9]
    gname, g = list(grid_steps(K))[2]
    _sname, Ks = list(keyed_alphabets(sigma_words))[5]
    sigma = [int(x) for x in sigma_family(Ks)[13]]
    a0, direction = 22, +1
    # a preventer fire inside the crib words would break the crib; draw a base_0 that
    # keeps them clean, which is the case the filter is built for
    for _ in range(100):
        base0 = rng.sample(range(M), M)
        ct = encipher_dir(plain, base0, g, sigma, a0, direction)
        clean = all(
            ct[w][i] != ct[w][i - 1] for w in (0, 1) for i in range(1, len(ct[w]))
        )
        if clean and ct[1][0] != ct[0][-1]:
            break
    print(
        f"planted: g from {_kname} {gname}, sigma from {_sname} #13, a0 {a0}, dir {direction}"
    )
    cond = crib_conditions(g, a0, direction, ct[0], ct[1])
    assert cond is not None, "the crib refutes the planted g"
    print(
        f"planted ciphertext gives {len(cond[0])} pins and {len(cond[1])} exclusions on sigma"
    )
    fam = np.unique(
        np.concatenate([sigma_family(x) for _, x in keyed_alphabets(sigma_words)]),
        axis=0,
    )
    idx = SigmaIndex(fam).matching(*cond)
    assert any(list(fam[i]) == sigma for i in idx), (
        "the planted sigma fails the crib filter"
    )
    print(
        f"crib filter keeps {len(idx)} of {len(fam)} sigmas for the planted (g, a0), the true one among them"
    )

    logf = log_frequencies()
    best, tested, triples, refuted, size = sweep(
        g_words, sigma_words, ct, logf, keep=10, log_every=10**9
    )
    print(
        f"{triples:,} triples, {refuted:,} refuted by word 0, {tested:,} sigmas scored of {triples * size:,}"
    )
    for row in best[:5]:
        print(
            f"  {row[0]:+.4f}  {row[1]:<26} {row[2]:<16} a0 {row[4]:>2} dir {row[5]:+d}"
        )
    top = best[0]
    assert (
        top[3] == sigma and top[4] == a0 and top[5] == direction and top[2] == gname
    ), "the planted key does not rank first"
    print("self-test passed")


def run() -> None:
    from quagmire_schedule_census import lp_words  # noqa: PLC0415
    from quagmire_ungated_sweep import priority_vocabulary  # noqa: PLC0415

    words = priority_vocabulary()
    body = lp_words()
    logf = log_frequencies()
    print(
        f"{len(words)} priority words for g and for sigma; crib DIVINITY WITHIN at words 0-1"
    )
    best, tested, triples, refuted, size = sweep(words, words, body, logf)
    print(
        f"\nDONE: {triples:,} (g, a0, dir) triples x {size:,} sigmas = {triples * size:,} keys; "
        f"{refuted:,} triples refuted by word 0; {tested:,} keys scored"
    )
    with OUT.open("w") as fout:
        for score, kname, gname, sigma, a0, direction in best:
            print(
                f"  {score:+.4f}  {kname:<28} {gname:<16} a0 {a0:>2} dir {direction:+d}"
            )
            fout.write(
                json.dumps(
                    {
                        "score": score,
                        "alphabet": kname,
                        "g": gname,
                        "sigma": sigma,
                        "a0": a0,
                        "dir": direction,
                    }
                )
                + "\n"
            )
    print(f"written to {OUT}; a true key scores near +1.1, wrong keys below +0.6")


def main() -> None:
    if "--selftest" in sys.argv:
        selftest()
    elif "--run" in sys.argv:
        run()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
