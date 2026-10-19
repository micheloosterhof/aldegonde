# ABOUTME: Checks every odometer-Quagmire key over 3301's vocabulary against the
# ABOUTME: DIVINITY WITHIN crib, where thirteen runes decide a key outright.
"""The opening crib as a key test for the odometer families.

For the walk the first two blocks constrain little, because each block carries a free
base. The odometer families have no free base: given the keyed alphabet K, the
schedule S and the inner dial a_0, the ciphertext of DIVINITY WITHIN is fixed up to
the outer dial b, a single shift common to all thirteen runes. A wrong key matches
thirteen runes with one shift once in 29^12, so over 3.9e9 keys the expected number of
false matches is 1e-8: the crib alone decides, if it is right.

Two families, both with the dials on a carry and the clock running on from the first
rune (`quagmire-odometer.md`, `plaintext-dial-odometer.md`):

    inside     c = K[ pos_K(p) + a_w + S_k ] + b_w
    plaintext  c = K[ pos_K(p + a_w) + S_k ] + b_w

Word 0 uses a_0 at clock 0..7, word 1 uses a_0 + 1 at clock 8..12. The preventer may
have advanced the clock inside the crib (about one chance in three that it did once,
one in fourteen twice), so every placement of one extra clock step is tried too.

Run with no arguments for the self-test; `--run` for the check over every keyed
alphabet, schedule and dial.
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from pure_quagmire_restart import running, schedule  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
CRIB = [c3301.encode_english("DIVINITY"), c3301.encode_english("WITHIN")]
assert [len(w) for w in CRIB] == [8, 5]
PLAIN = np.array(CRIB[0] + CRIB[1])
WORD = np.array([0] * 8 + [1] * 5)


def clock_variants() -> list[np.ndarray]:
    """The clock at each crib rune: no skip, or one extra step after rune d."""
    base = np.arange(13)
    out = [base]
    for d in range(1, 13):
        clock = base.copy()
        clock[d:] += 1
        out.append(clock)
    return out


def all_schedules() -> np.ndarray:
    """Running sums S_0..S_4 of every five-step schedule with exactly one zero offset."""
    from dodge_priority_sweep import surviving_schedules  # noqa: PLC0415
    from quagmire_runner import (  # noqa: PLC0415
        PROSE_CACHE,
        build_register,
        build_setup,
    )
    from quagmire_schedule_census import (  # noqa: PLC0415
        lp_words,
        observed_rates,
        wilson,
    )
    from zero_offset_census import diluted_band  # noqa: PLC0415

    lens = [len(w) for w in lp_words()][:400]
    _w, _v, T1, lo1, hi1, _s = build_setup(PROSE_CACHE, lens, vocab=["the"])
    _T1, T4, T6, _c = build_register(PROSE_CACHE, lens)
    obs = observed_rates(lp_words())
    bands = (
        (lo1, hi1),
        diluted_band(*wilson(*obs[4]), 4),
        diluted_band(*wilson(*obs[6]), 6),
    )
    K = list(range(M))  # the generator's banding is off, so K does not matter
    offsets = surviving_schedules(K, (T1, T4, T6), bands)
    return np.cumsum(offsets.astype(np.int64), axis=1) % M


def matches(K, sums: np.ndarray, cipher: np.ndarray, *, plaintext_side: bool):
    """(schedule index, a0, b, clock variant) for every key reproducing the crib."""
    K = np.asarray(K, dtype=np.int16)
    pos = np.empty(M, dtype=np.int16)
    pos[K] = np.arange(M)
    dial = (np.arange(M)[:, None] + WORD[None, :]) % M  # (29, 13): a_w for each a0
    if plaintext_side:
        start = pos[(PLAIN[None, :] + dial) % M]  # (29, 13)
    else:
        start = pos[PLAIN][None, :] + dial
    hits = []
    sums16 = sums.astype(np.int16)
    for v, clock in enumerate(clock_variants()):
        phase = clock % 5
        # the first two runes already fix the outer shift; only keys where they agree
        # need the other eleven, which is one key in 29
        two = (start[:, None, :2] + sums16[None, :, phase[:2]]) % M  # (29, n, 2)
        b2 = (cipher[None, None, :2] - K[two]) % M
        a0s, idxs = np.nonzero(b2[..., 0] == b2[..., 1])
        if len(idxs) == 0:
            continue
        inner = (start[a0s, :] + sums16[idxs][:, phase]) % M  # (m, 13)
        b = (cipher[None, :] - K[inner]) % M
        same = (b == b[:, :1]).all(axis=1)
        for a0, idx, row in zip(a0s[same], idxs[same], b[same]):
            hits.append((int(idx), int(a0), int(row[0]), v))
    return hits


def naive(K, offsets, start, *, plaintext_side: bool) -> list[int]:
    """The crib's ciphertext with the preventer switched off, clock 0..12."""
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    plain = CRIB[0] + CRIB[1]
    out = []
    for i, p in enumerate(plain):
        a = (start[0] + (1 if i >= 8 else 0)) % M
        x = pos[(p + a) % M] if plaintext_side else pos[p] + a
        out.append((K[(x + S[i % 5]) % M] + start[1]) % M)
    return out


def encipher(plain, K, offsets, start, *, plaintext_side: bool):
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    a, b = start
    out, previous, clock = [], None, 0
    for word in plain:
        cw = []
        for p in word:
            x = pos[(p + a) % M] if plaintext_side else pos[p] + a
            c = (K[(x + S[clock % 5]) % M] + b) % M
            if c == previous:
                clock += 1
                c = (K[(x + S[clock % 5]) % M] + b) % M
            cw.append(c)
            previous = c
            clock += 1
        out.append(cw)
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    return out


def self_test() -> None:
    rng = random.Random(7)
    sums = all_schedules()
    print(f"{len(sums):,} schedules")
    for side in (False, True):
        K = rng.sample(range(M), M)
        offsets = schedule(rng)
        start = (rng.randrange(M), rng.randrange(M))
        target = np.nonzero((sums == np.cumsum(offsets) % M).all(axis=1))[0]
        assert len(target) == 1, "the planted schedule must be in the set once"
        for _ in range(200):  # a crib the preventer left alone, the no-skip case
            ct = encipher(
                [list(CRIB[0]), list(CRIB[1])], K, offsets, start, plaintext_side=side
            )
            flat = ct[0] + ct[1]
            if flat == naive(K, offsets, start, plaintext_side=side):
                break
            start = (rng.randrange(M), rng.randrange(M))
        hits = matches(K, sums, np.array(flat), plaintext_side=side)
        assert (int(target[0]), start[0], start[1], 0) in hits, (
            "the planted key is not found"
        )
        wrong = [h for h in hits if h[0] != int(target[0]) or h[1] != start[0]]
        print(
            f"{'plaintext' if side else 'inside'} dial: planted key found, "
            f"{len(hits)} match(es) over {len(sums) * M * 13:,} (schedule, a0, clock) keys"
        )
        assert not wrong
    # a planted skip inside the crib is found by the clock variants
    K = rng.sample(range(M), M)
    offsets = schedule(rng)
    start = (3, 11)
    flat = None
    for _ in range(300):
        plain = [list(CRIB[0]), list(CRIB[1])]
        ct = encipher(plain, K, offsets, start, plaintext_side=True)
        joined = ct[0] + ct[1]
        if joined != naive(K, offsets, start, plaintext_side=True):
            flat = joined
            break
        start = (rng.randrange(M), rng.randrange(M))
    assert flat is not None, "no crib with a fire was produced"
    hits = matches(K, sums, np.array(flat), plaintext_side=True)
    target = int(np.nonzero((sums == np.cumsum(offsets) % M).all(axis=1))[0][0])
    assert any(h[0] == target and h[1] == start[0] and h[3] > 0 for h in hits), (
        "the skipped crib is not found"
    )
    print(
        "a crib with one preventer fire inside it is found through the clock variants"
    )
    print("self-test passed")


def dictionary_alphabets(top: int):
    """Keyed alphabets from the `top` most frequent English words not in the priority list."""
    from keyword_exhaustion import alphabets, kw_runes  # noqa: PLC0415
    from quagmire_ungated_sweep import priority_vocabulary  # noqa: PLC0415
    from wordfreq import top_n_list  # noqa: PLC0415

    skip = {w.upper() for w in priority_vocabulary()}
    out = []
    for word in top_n_list("en", top):
        if word.isalpha() and word.upper() not in skip:
            seq = kw_runes(word)
            if seq:
                out.extend((f"{word} {rule}", list(K)) for rule, K in alphabets(seq))
    return out


def run(top: int = 0) -> None:
    from dodge_priority_sweep import _prepare  # noqa: PLC0415
    from quagmire_schedule_census import lp_words  # noqa: PLC0415

    body = lp_words()
    cipher = np.array(body[0] + body[1])
    if top:
        keys = dictionary_alphabets(top)
    else:
        _w, keys = _prepare([len(w) for w in body][:400])
    sums = all_schedules()
    print(
        f"{len(keys):,} keyed alphabets x {len(sums):,} schedules x 29 dials x 13 clocks, two families"
    )
    start = time.time()
    found = []
    for n, (name, K) in enumerate(keys, 1):
        for side in (False, True):
            for idx, a0, b, v in matches(K, sums, cipher, plaintext_side=side):
                found.append((name, side, idx, a0, b, v))
                print(
                    f"  MATCH: {name} {'plaintext' if side else 'inside'} dial, schedule {idx}, a0 {a0}, b {b}, clock variant {v}",
                    flush=True,
                )
        if n % 100 == 0:
            print(
                f"  {n} alphabets, {len(found)} matches, {(time.time() - start) / 60:.1f} min",
                flush=True,
            )
    print(f"\nDONE: {len(found)} keys reproduce DIVINITY WITHIN with one outer shift")


if __name__ == "__main__":
    if "--run" in sys.argv:
        top = 0
        for i, arg in enumerate(sys.argv):
            if arg == "--top" and i + 1 < len(sys.argv):
                top = int(sys.argv[i + 1])
        run(top)
    else:
        self_test()
