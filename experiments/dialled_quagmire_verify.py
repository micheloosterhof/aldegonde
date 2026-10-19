# ABOUTME: Scores a dialled-Quagmire key on the body with the dials free in every word,
# ABOUTME: so that a crib match can be told from one of the expected false matches.
"""Body verification for `dialled_quagmire_crib_check.py` matches.

A crib match fixes K1, K2 and the schedule but says nothing about the dials of the
other words. Under the family every word decrypts for some (phase, a_w, b_w), 4,205
choices, and a trigram score cannot tell a true key from a wrong one: the best of
4,205 random strings is as trigram-plausible as a real word (measured: -2.9 per trigram
at five runes against about -3.5 for words). A dictionary can. A random six-rune string
is an English word about once in 10^5, so a wrong key finds a dictionary reading for a
long word about once in 20, while a true key reads most of them. The statistic is the
number of blocks of six runes or more, among the first 150 after the crib, that have a
dictionary reading under some choice of the dials, against the same count for random
keys of the family. Blocks that join two words, and words in which the preventer
fired, count as misses for the true key too; the rest carry the verdict.

Run with no arguments for the self-test; `--matches FILE` scores every row of a
matches file written by the crib check.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from dialled_quagmire_crib_check import (  # noqa: E402
    CRIB,
    all_schedules,
    backwards,
    encipher,
    family,
    inverse,
    rotated,
)
from pure_quagmire_restart import schedule  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
WORDS = 150
FIRST = 2  # the crib's two words are not scored
MIN_LEN = 6
POWERS = M ** np.arange(16, dtype=np.int64)


def codes(p: np.ndarray) -> np.ndarray:
    """One integer per row of rune indices (rows of at most 12 runes)."""
    L = min(p.shape[-1], 12)
    return (p[..., :L] * POWERS[:L]).sum(axis=-1)


def dictionary(top: int = 60000) -> dict[int, np.ndarray]:
    """Sorted codes of the `top` English words, by rune length, six runes and up."""
    from wordfreq import top_n_list  # noqa: PLC0415

    by_len: dict[int, set[int]] = {}
    for word in top_n_list("en", top):
        if not word.isalpha():
            continue
        runes = c3301.encode_english(word.upper())
        if len(runes) >= MIN_LEN:
            by_len.setdefault(len(runes), set()).add(int(codes(np.array(runes))))
    return {L: np.array(sorted(s), dtype=np.int64) for L, s in by_len.items()}


def readings(K1, K2, sums_s, cw) -> np.ndarray:
    """Every decryption of one block over (b, phase, a), as a (4205, L) array."""
    K1 = np.asarray(K1)
    pos2 = inverse(K2)
    c = np.asarray(cw)
    L = len(c)
    b = np.arange(M)
    phase = (np.arange(5)[:, None] + np.arange(L)[None, :]) % 5  # (5, L)
    inner = (pos2[(c[None, :] - b[:, None]) % M][:, None, :] - sums_s[phase][None]) % M
    p = (K1[inner][:, :, None, :] - np.arange(M)[None, None, :, None]) % M
    return p.reshape(-1, L)


def word_hits(K1, K2, sums_s, cipher_words, words) -> np.ndarray:
    """Whether each block of MIN_LEN runes or more has a dictionary reading."""
    out = []
    for cw in cipher_words:
        L = len(cw)
        if L < MIN_LEN or L not in words:
            continue
        found = np.isin(
            codes(readings(K1, K2, sums_s, cw)), words[L], assume_unique=False
        )
        out.append(bool(found.any()))
    return np.array(out, dtype=bool)


def score(K1, K2, sums_s, cipher_words, words) -> int:
    return int(word_hits(K1, K2, sums_s, cipher_words, words).sum())


def null_scores(fam1, fam2, sums, cipher_words, words, rng, n: int = 100) -> np.ndarray:
    """The statistic for `n` random keys of the family on the same ciphertext."""
    out = []
    for _ in range(n):
        K1 = fam1[rng.randrange(len(fam1))][1]
        K2 = fam2[rng.randrange(len(fam2))][1]
        out.append(score(K1, K2, sums[rng.randrange(len(sums))], cipher_words, words))
    return np.array(out)


def dictionary_readings(K1, K2, sums_s, cw, words) -> list[str]:
    """The English words one block can read as, under any dials."""
    L = len(cw)
    if L not in words:
        return []
    p = readings(K1, K2, sums_s, cw)
    hit = np.isin(codes(p), words[L])
    seen = {tuple(int(x) for x in row) for row in p[hit]}
    return [c3301.decode_english(list(row)) for row in sorted(seen)]


def self_test() -> None:
    from pure_quagmire_restart import matched_register  # noqa: PLC0415
    from quagmire_runner import PROSE_CACHE, load_register  # noqa: PLC0415
    from walk_shift_sweep import _lens  # noqa: PLC0415

    rng = random.Random(5)
    sums = all_schedules()
    words = dictionary()
    print(
        f"dictionary: {sum(len(v) for v in words.values()):,} words of {MIN_LEN}+ runes"
    )
    keywords = ["DIVINITY", "WITHIN", "PARABLE", "WISDOM", "PILGRIM", "CIRCUMFERENCE"]
    fam1, fam2 = family(keywords, affine=True), rotated(family(keywords))
    pools, _t, _f = load_register(PROSE_CACHE)
    lens = _lens()[: FIRST + WORDS]
    plain = [list(CRIB[0]), list(CRIB[1])] + matched_register(rng, lens[2:], pools)
    K1 = fam1[rng.randrange(len(fam1))][1]
    K2 = fam2[rng.randrange(len(fam2))][1]
    offsets = schedule(rng)
    s = int(np.nonzero((sums == np.cumsum(offsets) % M).all(axis=1))[0][0])
    a = [rng.randrange(M) for _ in plain]
    b = [rng.randrange(M) for _ in plain]
    ct, fires = encipher(plain, K1, K2, offsets, a, b, phase=2)
    body = ct[FIRST:]
    long_words = sum(len(w) >= MIN_LEN for w in body)
    true = score(K1, K2, sums[s], body, words)
    null = null_scores(fam1, fam2, sums, body, words, rng, n=40)
    z = (true - null.mean()) / max(null.std(), 1.0)
    print(
        f"{len(body)} blocks, {long_words} of {MIN_LEN}+ runes, {len(fires)} preventer "
        f"fires; planted key reads {true}, random keys {null.mean():.1f} +- "
        f"{null.std():.1f}, z = {z:+.1f}"
    )
    assert z > 5 and true > 3 * null.max(), "the planted key does not separate"
    first = next(w for w in body if len(w) >= MIN_LEN)
    print(f"a long block reads {dictionary_readings(K1, K2, sums[s], first, words)}")
    print("self-test passed")


def run(path: Path) -> None:
    from quagmire_schedule_census import lp_words  # noqa: PLC0415
    from quagmire_ungated_sweep import priority_vocabulary  # noqa: PLC0415

    keywords = priority_vocabulary()
    fam1 = family(keywords, affine=True)
    fam2 = rotated(family(keywords))
    by_name = dict(fam1)
    by_name.update(dict(fam2))
    by_name.update(dict(family(keywords)))
    by_name.update(dict(rotated(backwards(family(keywords)))))
    sums = all_schedules()
    words = dictionary()
    body = lp_words()[FIRST : FIRST + WORDS]
    long_words = sum(len(w) >= MIN_LEN for w in body)
    rng = random.Random(1)
    null = null_scores(fam1, fam2, sums, body, words, rng, n=100)
    print(
        f"{long_words} blocks of {MIN_LEN}+ runes; random keys read "
        f"{null.mean():.1f} +- {null.std():.1f} of them, max {null.max()}"
    )
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    for row in rows:
        K1, K2 = by_name[row["K1"]], by_name[row["K2"]]
        value = score(K1, K2, sums[row["schedule"]], body, words)
        z = (value - null.mean()) / max(null.std(), 1.0)
        sample = [
            dictionary_readings(K1, K2, sums[row["schedule"]], w, words)
            for w in body
            if len(w) >= MIN_LEN
        ]
        sample = [r for r in sample if r][:4]
        print(
            f"  reads {value:>3} (z {z:+.1f})  {row['K1']} / {row['K2']} schedule "
            f"{row['schedule']} {row['clock']}; e.g. {sample}"
        )
    print(f"{len(rows)} matches scored; a true key reads most long blocks")


if __name__ == "__main__":
    if "--matches" in sys.argv:
        run(Path(sys.argv[sys.argv.index("--matches") + 1]))
    else:
        self_test()
