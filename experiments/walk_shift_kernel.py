# ABOUTME: Builds and calls the compiled walk scorer with a per-word plaintext shift
# ABOUTME: (walk_shift_kernel.c); self-tests it against the Python reference.
"""ctypes front end for `walk_shift_kernel.c`.

`score_sigmas` scores every sigma in a batch against one set of five letter perms
and one shift schedule, over several ciphertext windows, each with its own free base,
and returns each sigma's best window score in nats per rune above flat.

Run with no arguments to check the kernel against
`walk_shift_verifier_check.score_key` on a planted key and print its throughput.
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

from base_free_verifier import log_frequencies, powers  # noqa: E402

M = 29
SOURCE = ROOT / "experiments" / "walk_shift_kernel.c"
_LIB: dict[str, ctypes.CDLL] = {}


def _library() -> ctypes.CDLL:
    """The shared library, named by the source hash so a rebuild never clobbers one in use."""
    if "lib" not in _LIB:
        digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()[:12]
        target = Path(tempfile.gettempdir()) / f"walk_shift_kernel_{digest}.so"
        if not target.exists():
            subprocess.run(  # noqa: S603
                ["cc", "-O3", "-shared", "-fPIC", "-o", str(target), str(SOURCE)],  # noqa: S607
                check=True,
            )
        lib = ctypes.CDLL(str(target))
        lib.score_sigmas_shifted.restype = None
        _LIB["lib"] = lib
    return _LIB["lib"]


class Windows:
    """Ciphertext windows packed for the kernel, with each word's shift s_w."""

    def __init__(self, windows: list[list[list[int]]], shifts: list[list[int]]) -> None:
        self.runes = np.array(
            [c for win in windows for word in win for c in word], dtype=np.int8
        )
        self.word_lens = np.array(
            [len(word) for win in windows for word in win], dtype=np.int32
        )
        self.word_shifts = np.array([s for win in shifts for s in win], dtype=np.int8)
        self.window_words = np.array([len(win) for win in windows], dtype=np.int32)
        assert len(self.word_shifts) == len(self.word_lens)


def schedule_shifts(
    spans: list[tuple[int, int]], a0: int, direction: int
) -> list[list[int]]:
    """s_w = a0 + direction * w for the words of each span (w the body word index)."""
    return [[(a0 + direction * w) % M for w in range(a, b)] for a, b in spans]


def score_sigmas(letter_perms, sigmas, windows: Windows, logf) -> np.ndarray:
    perms = np.ascontiguousarray(np.asarray(letter_perms), dtype=np.int8)
    sig = np.ascontiguousarray(sigmas, dtype=np.int8)
    lf = np.ascontiguousarray(logf, dtype=np.float32)
    out = np.empty(len(sig), dtype=np.float32)
    ptr = lambda a: a.ctypes.data_as(ctypes.c_void_p)  # noqa: E731
    _library().score_sigmas_shifted(
        ptr(perms),
        ptr(sig),
        ctypes.c_int(len(sig)),
        ptr(windows.runes),
        ptr(windows.word_lens),
        ptr(windows.word_shifts),
        ptr(windows.window_words),
        ctypes.c_int(len(windows.window_words)),
        ptr(lf),
        ptr(out),
    )
    return out


def self_test() -> None:
    from fingerprint_battery import rich_order5  # noqa: PLC0415
    from pure_quagmire_restart import matched_register  # noqa: PLC0415
    from quagmire_runner import PROSE_CACHE, load_register  # noqa: PLC0415
    from walk_shift_verifier_check import encipher, score_key  # noqa: PLC0415

    rng = random.Random(3301)
    pools, _t, _f = load_register(PROSE_CACHE)
    lens = [rng.choice([2, 3, 3, 4, 4, 5, 6, 7, 8]) for _ in range(1200)]
    plain = matched_register(rng, lens, pools)
    g = rich_order5(rng)
    sigma = rng.sample(range(M), M)
    base0 = rng.sample(range(M), M)
    a0 = rng.randrange(M)
    ct = encipher(plain, base0, g, sigma, a0)
    logf = log_frequencies()
    spans = [(0, 250), (400, 650), (900, 1150)]
    windows = Windows([ct[a:b] for a, b in spans], schedule_shifts(spans, a0, +1))
    sigmas = np.array([sigma] + [rng.sample(range(M), M) for _ in range(200)])

    got = score_sigmas(powers(g), sigmas, windows, logf)
    for k in range(6):
        want = max(
            score_key(ct[a:b], g, list(sigmas[k]), (a0 + a) % M, logf) for a, b in spans
        )
        assert abs(got[k] - want) < 1e-3, f"kernel {got[k]} != reference {want}"
    assert got[0] > got[1:].max() + 0.3, "true sigma does not stand out"
    print(
        f"kernel matches the Python reference; true {got[0]:.3f}, best wrong {got[1:].max():.3f}"
    )

    # the shift must be the right one: the true sigma with the schedule off by one
    off = Windows([ct[a:b] for a, b in spans], schedule_shifts(spans, (a0 + 1) % M, +1))
    wrong_shift = score_sigmas(powers(g), sigmas[:1], off, logf)[0]
    assert wrong_shift < got[0] - 0.3, "a wrong shift schedule should not score"
    print(f"true key with the schedule off by one: {wrong_shift:.3f}")

    batch = np.array([rng.sample(range(M), M) for _ in range(2000)])
    start = time.time()
    score_sigmas(powers(g), batch, windows, logf)
    rate = len(batch) / (time.time() - start)
    print(f"{rate:,.0f} keys/s on three 250-word windows")
    print("self-test passed")


if __name__ == "__main__":
    self_test()
