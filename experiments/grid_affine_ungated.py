# ABOUTME: Scores every magic-square grid g against every affine sigma with the
# ABOUTME: base_0-free verifier: no DJU-BEI gate and no register-derived g pool.
"""Magic-square g x affine sigma, the whole family, decided directly.

`affine-sigma.md` tested this pairing on 46 of the 190,008 grid g (those inside the
register-derived d1..d7 bands) and only on pairs passing the DJU-BEI six-point gate.
Both cuts can drop a true key: the bands rest on stand-in prose, and the gate is a
necessary condition only if DJU-BEI is a genuine state return, which the walk model
makes a ~1e-6 event (`quagmire_ungated_sweep.py`).

Here all 190,008 g x 812 sigma = 1.5e8 complete keys are scored by
`walk_score_kernel.score_sigmas`, base_0 free, on five 250-word section openings.
A wrong key floors near 0.6 nats/rune on a window; a true key sits near 1.2.

Run with no arguments for the positive control (a planted family key enciphered on
the real length sequence must be found). `--run N` sweeps the family over N workers.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import log_frequencies, powers  # noqa: E402
from ea_direction_test import PROSE_CACHE  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from magic_square_sweep import build_family_g  # noqa: E402
from quagmire_runner import load_register  # noqa: E402
from quagmire_ungated_sweep import SECTIONS, windows_of  # noqa: E402
from walk_full_profile import encipher  # noqa: E402
from walk_score_kernel import Windows, score_sigmas  # noqa: E402

M = 29
OUT = ROOT / "experiments" / "grid_affine_ungated_candidates.jsonl"
AFFINE = np.array(
    [
        [(a * x + b) % M for x in range(M)]
        for a in range(1, M)
        for b in range(M)
        if (a, b) != (1, 0)
    ],
    dtype=np.int8,
)
_W: dict = {}


def lp_words() -> list[list[int]]:
    stream, wid = load_clean()
    words: list[list[int]] = [[] for _ in range(wid[-1] + 1)]
    for rune, w in zip(stream, wid):
        words[w].append(rune)
    return words


def _init_worker() -> None:
    _W.update(windows=windows_of(lp_words()), logf=log_frequencies())


def _work(fixed_sets: list[tuple[int, ...]]):
    """Best affine sigma for every grid g built on these fixed-rune choices."""
    best = (-1.0, None)
    tested = 0
    for fixed in fixed_sets:
        for rot in (1, 2, 3, 4):
            for by_col in (True, False):
                g = build_family_g(set(fixed), rot, by_col=by_col)
                scores = score_sigmas(
                    powers(list(g)), AFFINE, _W["windows"], _W["logf"]
                )
                tested += len(scores)
                top = int(scores.argmax())
                if scores[top] > best[0]:
                    best = (float(scores[top]), (fixed, rot, by_col, top))
    return tested, best


def positive_control() -> None:
    rng = random.Random(3301)
    lens = [len(w) for w in lp_words()]
    pools, _table, _floor = load_register(PROSE_CACHE)
    plain = [rng.choice(pools[L])[:L] for L in lens]
    g = [int(x) for x in build_family_g({3, 11, 17, 26}, 2, by_col=True)]
    true_index = 300
    sigma = [int(x) for x in AFFINE[true_index]]
    cipher = encipher(plain, g, rng.sample(range(M), M), [sigma], [0] * len(plain))
    scores = score_sigmas(powers(g), AFFINE, windows_of(cipher), log_frequencies())
    wrong = np.delete(scores, true_index)
    print(
        f"planted key {scores[true_index]:.3f}; best of 811 wrong sigmas {wrong.max():.3f}"
    )
    assert scores.argmax() == true_index, "planted key not found"
    assert scores[true_index] > wrong.max() + 0.2, "planted key not found"
    print("positive control passed")


def run(nproc: int) -> None:
    fixed_sets = list(itertools.combinations(range(M), 4))
    chunks = [fixed_sets[i :: nproc * 30] for i in range(nproc * 30)]
    words, logf = lp_words(), log_frequencies()
    start = time.time()
    tested = 0
    results = []
    with Pool(nproc, initializer=_init_worker) as pool:
        for done, (count, best) in enumerate(pool.imap_unordered(_work, chunks), 1):
            tested += count
            results.append(best)
            if done % 30 == 0 or done == len(chunks):
                top = max(r[0] for r in results)
                print(
                    f"  {done}/{len(chunks)} chunks, {tested:,} keys, best {top:.3f}, "
                    f"{time.time() - start:.0f}s",
                    flush=True,
                )
    print(f"\nDONE: {tested:,} keys in {(time.time() - start) / 60:.1f} min")
    print("best keys re-scored on whole sections (wrong ~0.2, true ~1.2):")
    with OUT.open("w") as fout:
        for score, (fixed, rot, by_col, si) in sorted(results, key=lambda r: -r[0])[
            :20
        ]:
            g = build_family_g(set(fixed), rot, by_col=by_col)
            full = [
                float(
                    score_sigmas(
                        powers(list(g)),
                        AFFINE[si : si + 1],
                        Windows([words[a:b]]),
                        logf,
                    )[0]
                )
                for a, b in SECTIONS
            ]
            print(
                f"  window {score:.3f}  sections {' '.join(f'{x:.2f}' for x in full)}  fixed {fixed}"
            )
            record = {
                "window": score,
                "sections": full,
                "fixed": fixed,
                "rot": rot,
                "by_col": by_col,
            }
            record["sigma"] = [int(x) for x in AFFINE[si]]
            fout.write(json.dumps(record) + "\n")
    print(f"written to {OUT}")


if __name__ == "__main__":
    if "--run" in sys.argv:
        run(int(sys.argv[sys.argv.index("--run") + 1]))
    else:
        positive_control()
