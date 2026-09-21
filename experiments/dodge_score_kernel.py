# ABOUTME: Builds and calls the compiled dodge-aware scorer (dodge_score_kernel.c);
# ABOUTME: checks it against the Python reference and measures the sweep's real rate.
"""ctypes front end for the compiled dodge-aware scorer.

`score_dials` sweeps every odometer dial pair against one keyed alphabet and schedule.
The dials have to be enumerated -- `quagmire-odometer.md` measures that the scorer's
free bijection does not absorb them -- so they are the natural inner loop, and the
29 x 29 x 5 table they index is built once per (alphabet, schedule).

Run with no arguments to check the kernel against `dodge_aware_scorer.score` on a
planted key and to print the throughput a sweep would get.
"""

from __future__ import annotations

import ctypes
import hashlib
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import log_frequencies  # noqa: E402
from dodge_aware_scorer import PASSES, WINDOW, letter_maps, score  # noqa: E402
from doublet_phase_test import encipher  # noqa: E402
from ea_direction_test import PROSE_CACHE  # noqa: E402
from fingerprint_battery import M  # noqa: E402
from pure_quagmire_restart import matched_register, schedule  # noqa: E402
from quagmire_runner import load_clean, load_register  # noqa: E402

SOURCE = ROOT / "experiments" / "dodge_score_kernel.c"
_LIB: dict[int, ctypes.CDLL] = {}


def _library(points: int = M) -> ctypes.CDLL:
    """The shared library, named by source hash so a rebuild never clobbers a sweep."""
    if points not in _LIB:
        digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()[:12]
        target = Path(tempfile.gettempdir()) / f"dodge_score_{digest}_{points}.so"
        if not target.exists():
            subprocess.run(  # noqa: S603
                [
                    "cc",
                    "-O3",
                    "-shared",
                    "-fPIC",
                    f"-DM={points}",
                    "-o",
                    str(target),
                    str(SOURCE),
                ],  # noqa: S607
                check=True,
            )
        lib = ctypes.CDLL(str(target))
        lib.score_dials.restype = None
        _LIB[points] = lib
    return _LIB[points]


def log_table(K, offsets, logf) -> np.ndarray:
    """logtab[k][t][z] = log f of the plaintext that candidate z implies.

    `k` is the clock phase, `t` the word's inner dial, `z` the candidate already
    un-shifted by the outer dial. Mirrors the inner two lines of
    `dodge_aware_scorer.build`, which is what the equality test pins.
    """
    _fwd, inv = letter_maps(K, offsets)
    pos_of = [0] * M
    for i, r in enumerate(K):
        pos_of[r] = i
    tab = np.empty((5, M, M), dtype=np.float32)
    for k in range(5):
        for t in range(M):
            for z in range(M):
                inner = (pos_of[z] - t) % M
                tab[k, t, z] = logf[inv[k][K[inner]]]
    return tab


def score_dials(logtab, dials, cipher_words, window=WINDOW, passes=PASSES):
    """Nats per rune above flat, one per dial pair."""
    runes = np.array([c for w in cipher_words for c in w], dtype=np.int8)
    lens = np.array([len(w) for w in cipher_words], dtype=np.int32)
    pairs = np.ascontiguousarray(np.asarray(dials), dtype=np.int8)
    out = np.empty(len(pairs), dtype=np.float32)
    ptr = lambda a: a.ctypes.data_as(ctypes.c_void_p)  # noqa: E731
    _library().score_dials(
        ptr(np.ascontiguousarray(logtab, dtype=np.float32)),
        ptr(pairs),
        ctypes.c_int(len(pairs)),
        ptr(runes),
        ptr(lens),
        ctypes.c_int(len(lens)),
        ctypes.c_int(window),
        ctypes.c_int(passes),
        ptr(out),
    )
    return out


def main() -> None:
    rng = random.Random(3301)
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)][:400]
    pools, _t, _f = load_register(PROSE_CACHE)
    logf = log_frequencies()

    K = rng.sample(range(M), M)
    offsets = schedule(rng)
    true_dials = (rng.randrange(M), rng.randrange(M))
    plain = matched_register(rng, lens, pools)
    cipher = encipher(plain, K, offsets, true_dials, 0, "advance")
    n_runes = sum(len(w) for w in cipher)
    flat = float(np.mean(logf))
    print(f"{len(cipher)} words, {n_runes} runes, window {WINDOW}, {PASSES} passes")

    logtab = log_table(K, offsets, logf)

    # the kernel must reproduce the Python reference, which is the only thing that
    # makes the C worth trusting. Python returns raw nats; the kernel subtracts flat.
    probe = [true_dials, (0, 0), (7, 19), (28, 3)]
    got = score_dials(logtab, probe, cipher)
    print(f"\n{'dials':>10}{'python':>12}{'kernel':>12}{'diff':>10}")
    worst = 0.0
    for (a, b), c_score in zip(probe, got):
        py = score(cipher, K, offsets, (a, b), logf) - flat
        worst = max(worst, abs(py - c_score))
        tag = " <- planted" if (a, b) == true_dials else ""
        print(
            f"{f'({a},{b})':>10}{py:>12.4f}{c_score:>12.4f}{py - c_score:>10.5f}{tag}"
        )
    assert worst < 2e-3, f"kernel disagrees with the reference by {worst:.4f}"
    print(f"\nlargest disagreement {worst:.5f} nats/rune")

    # The OUTER dial is degenerate: it shifts every ciphertext rune by the same
    # amount, and a uniform shift is itself a bijection, so the free assignment
    # absorbs it exactly. Checked below rather than assumed, because it divides the
    # sweep by 29.
    all_dials = [(a, b) for a in range(M) for b in range(M)]
    t0 = time.time()
    scores = score_dials(logtab, all_dials, cipher)
    dt = time.time() - t0
    rank = int((scores > scores[all_dials.index(true_dials)]).sum())
    print(
        f"\nall {len(all_dials)} dial pairs in {dt:.3f}s "
        f"({len(all_dials) / dt:,.0f} keys/s/core)"
    )
    print(
        f"planted dials {true_dials} score {scores[all_dials.index(true_dials)]:+.4f}, "
        f"rank {rank + 1} of {len(all_dials)}; runner-up {np.sort(scores)[-2]:+.4f}"
    )
    assert rank == 0, "the planted dial pair must top its own alphabet and schedule"

    grid = scores.reshape(M, M)
    spread = float(grid.std(axis=1).max())
    print(
        f"largest score spread across the 29 OUTER dials, over all inner dials: "
        f"{spread:.6f}"
    )
    assert spread < 1e-5, (
        "a uniform ciphertext shift is a bijection, so the outer dial must be "
        "absorbed exactly by the free assignment"
    )
    print("so the outer dial is free and the sweep enumerates 29 dials, not 841.")

    rate = len(all_dials) / dt
    pairs_needed = 1.3e7
    print(
        f"\nat {rate:,.0f} keys/s/core the priority sweep is "
        f"{pairs_needed * M / rate / 3600:,.0f} core-hours,"
        f"\nor {pairs_needed * M * 0.6 / rate / 3600:,.0f} with the 60% prefilter."
    )


if __name__ == "__main__":
    main()
