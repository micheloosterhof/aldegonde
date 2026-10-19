# ABOUTME: Checks every Quagmire with keyed alphabets on both sides, a period-5 schedule
# ABOUTME: and free per-word dials against the DIVINITY WITHIN crib, where 13 runes decide.
"""The opening crib against the whole C9-compatible Quagmire family.

`odometer_crib_check.py` tests one keyed alphabet with dials that advance by one per
word, the clock at phase 0 on the first rune. Row C9 only asks that the per-word
relation be conjugated by a shift taking many values, and nothing fixes how the dials
move, which alphabet sits on the cipher side, or where the clock starts. So:

    c_j = K2[ (pos_K1(p_j + a_w) + S_k) mod 29 ] + b_w

with K1 and K2 any two keyed alphabets (or the standard order, either way round), S the
running sums of a five-step schedule with one zero offset, a_w and b_w free in every
word (a running key, an autokey, a keyword, a dial: all of them), the clock starting at
any phase and either running on through the word break or restarting at the word, and
the preventer firing at most once inside the thirteen runes.

The crib decides because nothing in the family is free per rune. DIVINITY has I at
positions 1, 3 and 5, so y_j = pos_K2(c_j - b) - S_k must agree at those three
positions whatever K1 and a_0 are: that cuts (K2, b, S, clock) by 841 before K1 is
looked at, and K1 is then found through an index on pairs of its positions. A wrong key
reproduces the thirteen runes with free (a_0, b_0, a_1, b_1) about once in 29^9, so
over 1.3e6 (K1, K2) pairs x 1.1e5 schedules x 130 clocks the expected number of false
matches is 0.15.

Run with no arguments for the self-test; `--run` for the check over 3301's vocabulary.
"""

from __future__ import annotations

import json
import random
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from odometer_crib_check import CRIB, all_schedules  # noqa: E402
from pure_quagmire_restart import running, schedule  # noqa: E402

from aldegonde.maths import permutation  # noqa: E402

M = 29
PLAIN0 = np.array(CRIB[0])
PLAIN1 = np.array(CRIB[1])
I_POS = [1, 3, 5]  # DIVINITY's three I's: their K1 positions must agree
DISTINCT0 = [0, 1, 2, 4, 6, 7]  # one position per distinct letter of DIVINITY
assert len({int(PLAIN0[j]) for j in DISTINCT0}) == 6
assert len({int(PLAIN0[j]) for j in I_POS}) == 1
OUT = ROOT / "experiments" / "dialled_quagmire_crib_matches.jsonl"


def inverse(K) -> np.ndarray:
    return np.asarray(permutation.inverse([int(x) for x in K]))


def clock_variants() -> list[tuple[str, np.ndarray]]:
    """(name, clock index of each crib rune): five start phases, continuous or
    restarting at the word, no preventer fire or one fire after rune d."""
    out = []
    for phase in range(5):
        for restart in (False, True):
            if restart:
                base = np.array(list(range(8)) + list(range(5))) + phase
            else:
                base = np.arange(13) + phase
            tag = f"phase {phase} {'restart' if restart else 'continuous'}"
            out.append((tag, base.copy()))
            for d in range(1, 13):
                clock = base.copy()
                end = 8 if (restart and d < 8) else 13
                clock[d:end] += 1
                out.append((f"{tag}, fire at {d}", clock))
    return out


class ScheduleIndex:
    """Schedules grouped by (S_k1 - S_k3, S_k3 - S_k5) at the clock of the three I's."""

    def __init__(self, sums: np.ndarray, clock: np.ndarray) -> None:
        ph = clock[I_POS] % 5
        d13 = (sums[:, ph[0]] - sums[:, ph[1]]) % M
        d35 = (sums[:, ph[1]] - sums[:, ph[2]]) % M
        key = d13 * M + d35
        self.order = np.argsort(key, kind="stable")
        sorted_keys = key[self.order]
        self.starts = np.searchsorted(sorted_keys, np.arange(M * M))
        self.ends = np.searchsorted(sorted_keys, np.arange(M * M), side="right")

    def lookup(self, keys: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(key position, schedule index) for every schedule under each key."""
        starts, ends = self.starts[keys], self.ends[keys]
        counts = ends - starts
        which = np.repeat(np.arange(len(keys)), counts)
        offsets = np.arange(counts.sum()) - np.repeat(
            np.cumsum(counts) - counts, counts
        )
        return which, self.order[np.repeat(starts, counts) + offsets]


class AlphabetIndex:
    """The K1 family with an index on (position y, position y', K1[y] - K1[y'])."""

    def __init__(self, names: list[str], alphabets: np.ndarray) -> None:
        self.names = names
        self.G = np.ascontiguousarray(alphabets, dtype=np.int64)  # (n, 29)
        n = len(self.G)
        diff = (self.G[:, :, None] - self.G[:, None, :]) % M  # (n, 29, 29)
        self.B = np.zeros((M, M, M, n), dtype=bool)
        k, y, yp = np.meshgrid(np.arange(n), np.arange(M), np.arange(M), indexing="ij")
        self.B[y.ravel(), yp.ravel(), diff.ravel(), k.ravel()] = True

    def matching(self, Y: np.ndarray, plain: np.ndarray):
        """(row, K1 index, a) with K1[Y[row, j]] == plain[j] + a for every column j."""
        delta = int((plain[0] - plain[1]) % M)
        cand = self.B[Y[:, 0], Y[:, 1], delta]  # (m, n)
        rows, ks = np.nonzero(cand)
        a = (self.G[ks, Y[rows, 0]] - plain[0]) % M
        ok = np.ones(len(rows), dtype=bool)
        for j in range(2, Y.shape[1]):
            ok &= (self.G[ks, Y[rows, j]] - plain[j]) % M == a
        return rows[ok], ks[ok], a[ok]


def word0_matches(K2, pos2, sums, sched_index, clock, cipher0, k1_index):
    """(K1 index, b0, schedule index, a0) for every key reproducing word 0."""
    b = np.arange(M)
    p = pos2[(cipher0[None, :] - b[:, None]) % M]  # (29, 8): pos_K2(c_j - b)
    keys = ((p[:, 1] - p[:, 3]) % M) * M + (p[:, 3] - p[:, 5]) % M
    bi, si = sched_index.lookup(keys)
    if len(si) == 0:
        return []
    y = (p[bi] - sums[si][:, clock[:8] % 5]) % M  # (m, 8)
    Y = y[:, DISTINCT0]
    distinct = (np.sort(Y, axis=1)[:, 1:] != np.sort(Y, axis=1)[:, :-1]).all(axis=1)
    bi, si, Y = bi[distinct], si[distinct], Y[distinct]
    if len(si) == 0:
        return []
    rows, ks, a0 = k1_index.matching(Y, PLAIN0[DISTINCT0])
    return [(int(k), int(bi[r]), int(si[r]), int(a)) for r, k, a in zip(rows, ks, a0)]


def word1_dials(K1, K2, sums_s, clock, cipher1) -> list[tuple[int, int]]:
    """Every (a1, b1) under which word 1 reads WITHIN."""
    pos1 = inverse(K1)
    K2 = np.asarray(K2)
    a1 = np.arange(M)
    x = (pos1[(PLAIN1[None, :] + a1[:, None]) % M] + sums_s[clock[8:] % 5]) % M
    b1 = (cipher1[None, :] - K2[x]) % M  # (29, 5)
    same = (b1 == b1[:, :1]).all(axis=1)
    return [(int(a), int(b1[a, 0])) for a in np.nonzero(same)[0]]


def check(
    k1_names, k1_alphabets, k2_family, sums, cipher0, cipher1, *, log_every=0, tag=""
):
    """Every (K1, K2, schedule, clock, a0, b0, a1, b1) reproducing both crib words."""
    k1_index = AlphabetIndex(k1_names, np.array(k1_alphabets))
    variants = clock_variants()
    indexes = [ScheduleIndex(sums, clock) for _, clock in variants]
    found, word0_total = [], 0
    start = time.time()
    for n, (k2name, K2) in enumerate(k2_family, 1):
        K2 = np.asarray(K2)
        pos2 = inverse(K2)
        for (vname, clock), sidx in zip(variants, indexes):
            hits = word0_matches(K2, pos2, sums, sidx, clock, cipher0, k1_index)
            word0_total += len(hits)
            for k, b0, s, a0 in hits:
                for a1, b1 in word1_dials(k1_index.G[k], K2, sums[s], clock, cipher1):
                    found.append(
                        {
                            "K1": k1_index.names[k],
                            "K2": k2name,
                            "schedule": int(s),
                            "clock": vname,
                            "a0": a0,
                            "b0": b0,
                            "a1": a1,
                            "b1": b1,
                        }
                    )
                    print(f"  MATCH: {found[-1]}", flush=True)
        if log_every and n % log_every == 0:
            print(
                f"  {tag}{n} cipher alphabets, {word0_total:,} word-0 matches, "
                f"{len(found)} full matches, {(time.time() - start) / 60:.1f} min",
                flush=True,
            )
    return found, word0_total


def encipher(plain_words, K1, K2, offsets, a, b, *, phase=0, restart=False):
    """The family's ciphertext with the preventer; also the stream indices where it fired."""
    pos1 = inverse(K1)
    S = running(offsets)
    out, fires, previous, i = [], [], None, 0
    clock = phase
    for w, word in enumerate(plain_words):
        if restart:
            clock = phase
        cw = []
        for p in word:
            x = (pos1[(p + a[w]) % M] + S[clock % 5]) % M
            c = (K2[x] + b[w]) % M
            if c == previous:
                fires.append(i)
                clock += 1
                x = (pos1[(p + a[w]) % M] + S[clock % 5]) % M
                c = (K2[x] + b[w]) % M
            cw.append(c)
            previous = c
            clock += 1
            i += 1
        out.append(cw)
    return out, fires


def family(words, *, affine: bool = False):
    """Keyed alphabets from `words` plus the standard order both ways round, or with
    `affine` every alphabet x -> ux + v (812, the standard order and its reverse
    among them)."""
    from walk_shift_sweep import keyed_alphabets  # noqa: PLC0415

    out = list(keyed_alphabets(words))
    if affine:
        for u in range(1, M):
            for v in range(M):
                out.append((f"affine {u}x+{v}", [(u * x + v) % M for x in range(M)]))
    else:
        out.append(("standard order", list(range(M))))
        out.append(("standard reversed", list(range(M - 1, -1, -1))))
    return out


def rotated(fam):
    """Every alphabet of `fam` in all 29 rotations: a disk has no start, and the
    schedules are normalised to S_4 = 0, which a rotation of K2 undoes."""
    return [
        (f"{name} rot{t}", list(K[t:]) + list(K[:t]))
        for name, K in fam
        for t in range(M)
    ]


_W: dict = {}


def _work(i: int):
    """One worker's share of the cipher alphabets."""
    return check(
        _W["names"],
        _W["alphabets"],
        _W["k2"][i :: _W["nproc"]],
        _W["sums"],
        *_W["cipher"],
        log_every=50,
        tag=f"worker {i}: ",
    )


def _plant(rng, fam1, fam2, sums, *, phase, restart, want_fires):
    """A planted key whose crib ciphertext has `want_fires` preventer fires inside it."""
    k1name, K1 = fam1[rng.randrange(len(fam1))]
    k2name, K2 = fam2[rng.randrange(len(fam2))]
    offsets = schedule(rng)
    s = np.nonzero((sums == np.cumsum(offsets) % M).all(axis=1))[0]
    assert len(s) == 1
    plain = [list(CRIB[0]), list(CRIB[1]), [rng.randrange(M) for _ in range(6)]]
    for _ in range(2000):
        a = [rng.randrange(M) for _ in plain]
        b = [rng.randrange(M) for _ in plain]
        ct, fires = encipher(plain, K1, K2, offsets, a, b, phase=phase, restart=restart)
        if len([f for f in fires if f < 13]) == want_fires:
            key = {
                "K1": k1name,
                "K2": k2name,
                "schedule": int(s[0]),
                "a0": a[0],
                "b0": b[0],
                "a1": a[1],
                "b1": b[1],
            }
            return key, ct, [f for f in fires if f < 13]
    msg = "no ciphertext with the wanted number of fires"
    raise AssertionError(msg)


def self_test() -> None:
    rng = random.Random(11)
    sums = all_schedules()
    words = ["DIVINITY", "WITHIN", "PARABLE", "WISDOM", "PILGRIM", "CIRCUMFERENCE"]
    fam = family(words)
    names = [n for n, _ in fam]
    alphabets = [K for _, K in fam]
    print(
        f"{len(fam)} alphabets, {len(sums):,} schedules, {len(clock_variants())} clocks"
    )
    cases = [
        (0, False, 0),
        (3, False, 1),
        (2, True, 1),
        (4, True, 0),
    ]
    for phase, restart, want in cases:
        key, ct, fires = _plant(
            rng, fam, fam, sums, phase=phase, restart=restart, want_fires=want
        )
        found, w0 = check(names, alphabets, fam, sums, np.array(ct[0]), np.array(ct[1]))
        kind = "restart" if restart else "continuous"
        expect_clock = f"phase {phase} {kind}" + (
            f", fire at {fires[0]}" if fires else ""
        )
        hit = [
            f
            for f in found
            if f["clock"] == expect_clock and all(f[k] == v for k, v in key.items())
        ]
        assert hit, f"planted key not found: {key} {expect_clock}; found {found}"
        print(
            f"{kind} clock at phase {phase}, {want} fire(s) at {fires}: planted key found; "
            f"{w0} word-0 matches, {len(found)} full match(es)"
        )
    cipher = [rng.randrange(M) for _ in range(13)]
    found, w0 = check(
        names, alphabets, fam, sums, np.array(cipher[:8]), np.array(cipher[8:])
    )
    print(f"random ciphertext: {w0} word-0 matches, {len(found)} full matches")
    assert not found
    aff = {tuple(K) for _, K in family([], affine=True)}
    assert len(aff) == (M - 1) * M
    assert tuple(range(M)) in aff and tuple(range(M - 1, -1, -1)) in aff
    print(f"affine family: {len(aff)} distinct alphabets, standard order both ways in")
    k2fam = rotated(fam[:4])
    key, ct, fires = _plant(rng, fam, k2fam, sums, phase=1, restart=False, want_fires=0)
    assert not key["K2"].endswith("rot0"), key
    found, w0 = check(names, alphabets, k2fam, sums, np.array(ct[0]), np.array(ct[1]))
    hit = [
        f
        for f in found
        if f["clock"] == "phase 1 continuous" and all(f[k] == v for k, v in key.items())
    ]
    assert hit, f"planted rotated key not found: {key}; found {found}"
    print(
        f"cipher alphabet {key['K2']}: planted key found; {w0} word-0 matches, "
        f"{len(found)} full match(es)"
    )
    print("self-test passed")


def run(*, affine: bool = False, rotations: bool = False, nproc: int = 1) -> None:
    from quagmire_schedule_census import lp_words  # noqa: PLC0415
    from quagmire_ungated_sweep import priority_vocabulary  # noqa: PLC0415

    body = lp_words()
    cipher0, cipher1 = np.array(body[0]), np.array(body[1])
    words = priority_vocabulary()
    sums = all_schedules()
    if rotations:
        k1, k2 = family(words, affine=True), rotated(family(words))
        label = "keyed and affine K1, keyed K2 in every rotation"
        out = OUT.with_name("dialled_quagmire_crib_rotations_matches.jsonl")
    else:
        k1 = k2 = family(words, affine=affine)
        label = "keyed and affine" if affine else "keyed"
        out = (
            OUT.with_name("dialled_quagmire_crib_affine_matches.jsonl")
            if affine
            else OUT
        )
    print(
        f"{len(k1):,} plain alphabets x {len(k2):,} cipher alphabets ({label}) x "
        f"{len(sums):,} schedules x {len(clock_variants())} clocks, dials free per word; "
        f"{nproc} worker(s)"
    )
    names, alphabets = [n for n, _ in k1], [K for _, K in k1]
    if nproc > 1:
        _W.update(
            names=names,
            alphabets=alphabets,
            k2=k2,
            sums=sums,
            cipher=(cipher0, cipher1),
            nproc=nproc,
        )
        found, w0 = [], 0
        with get_context("fork").Pool(nproc) as pool:
            for part, n in pool.imap_unordered(_work, range(nproc)):
                found.extend(part)
                w0 += n
    else:
        found, w0 = check(names, alphabets, k2, sums, cipher0, cipher1, log_every=20)
    with out.open("w") as fout:
        for row in found:
            fout.write(json.dumps(row) + "\n")
    print(f"\nDONE: {w0:,} word-0 matches, {len(found)} keys reproduce DIVINITY WITHIN")


if __name__ == "__main__":
    if "--run" in sys.argv:
        nproc = 1
        for i, arg in enumerate(sys.argv):
            if arg == "--nproc" and i + 1 < len(sys.argv):
                nproc = int(sys.argv[i + 1])
        run(
            affine="--affine" in sys.argv,
            rotations="--rotations" in sys.argv,
            nproc=nproc,
        )
    else:
        self_test()
