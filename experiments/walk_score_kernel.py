# ABOUTME: Builds and calls the compiled base_0-free walk scorer (walk_score_kernel.c);
# ABOUTME: self-tests it against the Python reference on the planted-key corpus.
"""ctypes front end for the compiled walk scorer.

`score_sigmas` scores every sigma in a batch against one set of five letter perms,
over several ciphertext windows, and returns each sigma's best window score (nats
per rune above flat). Windows are scored independently, each with its own free
base, so a section-level restart or one bad word length spoils one window only.

Run with no arguments to check the kernel against `base_free_verifier.score_key`
on the planted-key corpus and to print its throughput.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import (  # noqa: E402
    REFERENCE,
    log_frequencies,
    powers,
    score_key,
)

M = 29
SOURCE = ROOT / "experiments" / "walk_score_kernel.c"
_LIB: ctypes.CDLL | None = None


def _library() -> ctypes.CDLL:
    """The shared library, built once per version of the C source.

    The file name carries the source hash, so a rebuild never overwrites a library
    that a running sweep has loaded.
    """
    global _LIB  # noqa: PLW0603
    if _LIB is None:
        digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()[:12]
        target = Path(tempfile.gettempdir()) / f"walk_score_kernel_{digest}.so"
        if not target.exists():
            subprocess.run(  # noqa: S603
                ["cc", "-O3", "-shared", "-fPIC", "-o", str(target), str(SOURCE)],  # noqa: S607
                check=True,
            )
        _LIB = ctypes.CDLL(str(target))
        _LIB.score_sigmas.restype = None
    return _LIB


class Windows:
    """Ciphertext windows packed for the kernel."""

    def __init__(self, windows: list[list[list[int]]]) -> None:
        self.runes = np.array(
            [c for win in windows for word in win for c in word], dtype=np.int8
        )
        self.word_lens = np.array(
            [len(word) for win in windows for word in win], dtype=np.int32
        )
        self.window_words = np.array([len(win) for win in windows], dtype=np.int32)


def score_sigmas(
    letter_perms,
    sigmas: np.ndarray,
    windows: Windows,
    logf: np.ndarray,
    *,
    sum_windows: bool = False,
) -> np.ndarray:
    """Score of each sigma (rows of `sigmas`) under `letter_perms`.

    The best window score, or with `sum_windows` the rune-weighted mean over windows.
    """
    perms = np.ascontiguousarray(np.asarray(letter_perms), dtype=np.int8)
    sig = np.ascontiguousarray(sigmas, dtype=np.int8)
    lf = np.ascontiguousarray(logf, dtype=np.float32)
    out = np.empty(len(sig), dtype=np.float32)
    ptr = lambda a: a.ctypes.data_as(ctypes.c_void_p)  # noqa: E731
    _library().score_sigmas(
        ptr(perms),
        ptr(sig),
        ctypes.c_int(len(sig)),
        ptr(windows.runes),
        ptr(windows.word_lens),
        ptr(windows.window_words),
        ctypes.c_int(len(windows.window_words)),
        ptr(lf),
        ctypes.c_int(int(sum_windows)),
        ptr(out),
    )
    return out


def self_test() -> None:
    with REFERENCE.open() as fh:
        ref = json.load(fh)
    g, sigma, ct = ref["g"], ref["sigmas"][0], ref["ciphertext_words"]
    logf = log_frequencies()
    rng = random.Random(3301)
    spans = [(0, 250), (806, 1056), (2181, 2431)]
    windows = Windows([ct[a:b] for a, b in spans])
    sigmas = np.array([sigma] + [rng.sample(range(M), M) for _ in range(200)])

    got = score_sigmas(powers(g), sigmas, windows, logf)
    for k in range(6):
        want = max(
            score_key(ct[a:b], powers(g), list(sigmas[k]), logf)[0] for a, b in spans
        )
        assert abs(got[k] - want) < 1e-3, f"kernel {got[k]} != reference {want}"
    assert got[0] > got[1:].max() + 0.3, "true sigma does not stand out"
    summed = score_sigmas(powers(g), sigmas[:3], windows, logf, sum_windows=True)
    for k in range(3):
        parts = [score_key(ct[a:b], powers(g), list(sigmas[k]), logf) for a, b in spans]
        runes = [sum(len(w) for w in ct[a:b]) for a, b in spans]
        want = sum(p[0] * n for p, n in zip(parts, runes)) / sum(runes)
        assert abs(summed[k] - want) < 1e-3, f"summed {summed[k]} != reference {want}"
    print(
        f"kernel matches the Python reference; true {got[0]:.3f}, best wrong {got[1:].max():.3f}"
    )

    big = np.array([rng.sample(range(M), M) for _ in range(20000)])
    start = time.perf_counter()
    score_sigmas(powers(g), big, windows, logf)
    rate = len(big) / (time.perf_counter() - start)
    print(
        f"throughput: {rate:,.0f} keys/s per core over {len(spans)} windows of 250 words"
    )
    print("self-test passed")


if __name__ == "__main__":
    self_test()
