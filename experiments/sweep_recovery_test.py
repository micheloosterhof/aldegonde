# ABOUTME: End-to-end check that the keyword sweep recovers a key drawn from its OWN
# ABOUTME: candidate stream, not merely a key handed to the scorer.
"""Would the sweep have found the key, if the key were in the family?

`length-clocked-walk.md` records the trap exactly: a planted key that is out-of-family
validates the VERIFIER but not the ENUMERATION, and a search over a family that does
not contain it "would correctly reject everything, falsely reading as either success
or an empty family". The positive controls in `quagmire_ungated_sweep.py` and
`grid_affine_ungated.py` plant a key and hand it straight to the scorer. They never
check that `g_candidates` and `sigma_candidates` actually emit it.

This closes that gap. It draws a key from the candidate generators themselves,
enciphers prose with it, and then runs the real scoring loop over the stream those
generators produce -- the same path a production sweep takes. The planted key must
come out on top and above the candidate floor.

A negative sweep is only worth something if this passes.

Run with no arguments to test the band the `--run` sweep used; `--wide` for the
register-robust band, which enumerates far more slowly.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import quagmire_runner  # noqa: E402
from base_free_verifier import log_frequencies  # noqa: E402
from compact_state_models import prose_corpora  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from quagmire_runner import (  # noqa: E402
    build_setup,
    encrypt_walk,
    g_candidates,
    letter_steps,
)
from quagmire_ungated_sweep import (  # noqa: E402
    CANDIDATE_FROM,
    WIDE_D1,
    WIDE_SEAM,
    windows_of,
)
from walk_score_kernel import score_sigmas  # noqa: E402

M = 29
SLICE = 400  # keywords to enumerate over; enough to hold a planted key and rivals


def lp_lengths() -> list[int]:
    _stream, wid = load_clean()
    lens = [0] * (wid[-1] + 1)
    for w in wid:
        lens[w] += 1
    return lens


def main() -> None:
    rng = random.Random(3301)
    lens = lp_lengths()
    if "--wide" in sys.argv:
        quagmire_runner.D1_BAND = WIDE_D1
        quagmire_runner.SEAM_BAND = WIDE_SEAM
    _words, vocab, T1, lo1, hi1, sigmas = build_setup(quagmire_runner.PROSE_CACHE, lens)
    print(f"bands: d1 ({lo1:.4f}, {hi1:.4f}) -- the ones the production sweep used")

    # the candidate stream the production sweep would walk
    chunk = vocab[:SLICE]
    stream = list(g_candidates(chunk, T1, lo1, hi1, None))
    assert stream, "the candidate generator produced nothing"
    print(
        f"candidate stream from {SLICE} keywords: {len(stream):,} letter wheels, "
        f"{len(sigmas):,} disks"
    )

    # plant a key drawn FROM that stream, not invented alongside it
    pick = len(stream) // 3
    true_K, true_sched = stream[pick]
    true_sigma_index = len(sigmas) // 3
    true_sigma = sigmas[true_sigma_index]
    g_by_phase = letter_steps(true_K, true_sched)

    plain = prose_corpora(2928, 1)[0]
    plain = [w[:n] for w, n in zip(plain, lens)]
    base0 = rng.sample(range(M), M)
    cipher = encrypt_walk(plain, base0, g_by_phase, true_sigma)
    assert len({tuple(w) for w in cipher}) > 2000, "planted key is degenerate"
    print(f"planted key: wheel #{pick} of the stream, disk #{true_sigma_index}")

    # score the whole stream against it, exactly as the sweep does
    logf = log_frequencies()
    windows = windows_of(cipher)
    disks = np.array(sigmas, dtype=np.int8)
    best = (-1.0, None)
    true_score = None
    for index, (K, sched) in enumerate(stream):
        scores = score_sigmas(letter_steps(K, sched), disks, windows, logf)
        top = int(scores.argmax())
        if index == pick:
            true_score = float(scores[true_sigma_index])
        if float(scores[top]) > best[0]:
            best = (float(scores[top]), (index, top))
    print(
        f"planted key scores {true_score:.3f}; best over the whole stream "
        f"{best[0]:.3f} at wheel #{best[1][0]}, disk #{best[1][1]}"
    )

    assert best[1] == (pick, true_sigma_index), (
        f"the sweep's top key is not the planted one: {best[1]} vs "
        f"{(pick, true_sigma_index)}"
    )
    assert true_score >= CANDIDATE_FROM, (
        f"the planted key scores {true_score:.3f}, under the candidate floor "
        f"{CANDIDATE_FROM} -- a production sweep would have skipped it"
    )
    print(
        f"\nPASS: the enumeration recovers a key drawn from its own stream, and the "
        f"score clears the {CANDIDATE_FROM} floor. The negative sweeps are meaningful."
    )


if __name__ == "__main__":
    main()
