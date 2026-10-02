# ABOUTME: Slides the deterministic-keystream sweep across every part of the body, so an
# ABOUTME: interrupted running key is caught in whichever window happens to be clean.
"""The sequence sweep scores one window. An interrupted key needs every window.

`sequence_key_sweep.py` fixed three defects in the original sweep -- it scores a PREFIX
so a later interrupt cannot hide a correct generator, varies the sequence start, and
uses a scorer with a measured positive control. It still tests one place: the first 57
runes of the body.

That is the wrong place to bet on. The author interrupts his keystream about once per
85 runes on the solved AN END page, so the key index at rune `i` is `i` minus however
many interrupts came before it. After a few hundred runes the drift exceeds any start
range the sweep tries, and the prefix is the one stretch where drift is zero only if the
body's cipher begins exactly there.

So slide the window. Any 57-rune window that happens to contain no interrupt decrypts
correctly under the right generator at the right start, wherever it sits, and the
accumulated drift is absorbed by the start search. At an interrupt rate of 1.2% about
half of all windows are clean, so a real running key cannot hide from all of them.

The claim this falsifies: **the body is an additive keystream from one of these 24
integer sequences over the standard rune order, at any phase, with interrupts.**

A planted control runs first and must be found, or the sweep proves nothing.

    python window_sequence_sweep.py [--width 57] [--step 29] [--starts 150] [--control]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import sequence_key_sweep as sks  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from sequence_key_sweep import M, trigram_table  # noqa: E402

# the shared module builds 4,000 terms, which does not reach the end of a 12,956-rune
# body. A running key has to be defined everywhere the ciphertext is.
sks.TERMS = 14000
generators = sks.generators


def score_all_starts(
    window: np.ndarray, seq: np.ndarray, starts: int, first: int = 0
) -> np.ndarray:
    """Best trigram score over 29 offsets and both senses, for every sequence start.

    `first` is the lowest key index tried. A running key's index at rune `p` is `p`
    minus the interrupts before it, so the starts that matter for a window at `p` are
    the ones just below `p` -- not the ones near the sequence's beginning. Searching
    `[p - starts, p]` covers any interrupt count up to `starts`.

    Vectorised over starts: the whole (starts, 58, width) tensor is built once, which
    is what makes a slide across the body affordable.
    """
    t = trigram_table()
    w = window.size
    keys = np.lib.stride_tricks.sliding_window_view(seq, w)[first : first + starts]
    d = (window[None, :] - keys) % M
    offs = np.arange(M)[None, :, None]
    both = np.concatenate([(d[:, None, :] + offs) % M, (-d[:, None, :] + offs) % M], 1)
    idx = both[:, :, :-2] * 841 + both[:, :, 1:-1] * 29 + both[:, :, 2:]
    return t[idx].mean(axis=2).max(axis=1)


def sweep_windows(
    stream: np.ndarray, width: int, step: int, starts: int, *, drift: bool = True
):
    """Slide a window; at each one try the key indices the position allows.

    `drift=True` searches key indices in `[pos - starts, pos]`, which is where a
    running key that has been interrupted at most `starts` times must be.
    `drift=False` searches `[0, starts)`, which asks instead whether the key restarts
    near the window -- a per-page key, say.
    """
    gens = generators()
    best = []
    for pos in range(0, stream.size - width + 1, step):
        window = stream[pos : pos + width]
        first = max(0, pos - starts) if drift else 0
        for name, seq in gens.items():
            scores = score_all_starts(window, seq, starts, first)
            if not scores.size:
                continue
            j = int(scores.argmax())
            best.append((float(scores[j]), pos, name, first + j))
    best.sort(reverse=True)
    return best


def control(width: int, starts: int) -> bool:
    """Plant a prime running key on real runeglish and check the sweep finds it."""
    import json  # noqa: PLC0415
    import re  # noqa: PLC0415

    from aldegonde import c3301  # noqa: PLC0415

    triples = json.loads(
        (ROOT / "experiments" / "solved_page_triples.json").read_text()
    )
    page = next(x for x in triples if x["cipher"] == "prime running key")
    plain = np.array(page["plaintext_runes"], dtype=np.int64)
    seq = generators()["prime(n)-1"]
    # encipher the real AN END plaintext with the real generator, no interrupts, and
    # bury it in random runes so the sweep has to locate it as well as identify it
    rng = np.random.default_rng(7)
    cipher = (plain + seq[: plain.size]) % M
    filler_a = rng.integers(0, M, 200)
    filler_b = rng.integers(0, M, 200)
    stream = np.concatenate([filler_a, cipher, filler_b])
    rows = sweep_windows(stream, width, 7, starts)
    top = rows[0]
    hit = 200 <= top[1] < 200 + plain.size and top[2] == "prime(n)-1"
    alph = c3301.CICADA_ALPHABET
    eng = c3301.CICADA_ENGLISH_ALPHABET
    print(f"control: planted prime(n)-1 at rune 200 of {stream.size}")
    print(
        f"  top hit  score {top[0]:+.3f} at position {top[1]}, "
        f"generator {top[2]}, start {top[3]}"
    )
    runner = sorted({r[2] for r in rows[:10]})
    print(f"  generators in the top ten: {', '.join(runner)}")
    print("  FOUND\n" if hit else "  MISSED -- the sweep has no power, stop here\n")
    del alph, eng, re
    return hit


def main() -> None:
    width, step, starts = 57, 29, 150
    for i, a in enumerate(sys.argv):
        if a == "--width" and i + 1 < len(sys.argv):
            width = int(sys.argv[i + 1])
        if a == "--step" and i + 1 < len(sys.argv):
            step = int(sys.argv[i + 1])
        if a == "--starts" and i + 1 < len(sys.argv):
            starts = int(sys.argv[i + 1])

    if not control(width, starts):
        return
    if "--control" in sys.argv:
        return

    stream = np.array(load_clean()[0], dtype=np.int64)
    for drift, label in (
        (True, "key runs on through the body, interrupted at most `starts` times"),
        (False, "key restarts near the sequence's beginning in some window"),
    ):
        rows = sweep_windows(stream, width, step, starts, drift=drift)
        scores = np.array([r[0] for r in rows])
        print(
            f"\n{label}\n  {len(rows):,} (window, generator) pairs, width {width}, "
            f"step {step}, {starts} starts each"
        )
        print(f"  {'score':>8}{'position':>10}{'generator':>22}{'start':>8}")
        for sc, pos, name, start in rows[:6]:
            print(f"  {sc:>8.3f}{pos:>10}{name:>22}{start:>8}")
        print(
            f"  max {scores.max():.3f}, median {np.median(scores):.3f}, "
            f"sd {scores.std():.3f}  ->  best is "
            f"{(scores.max() - scores.mean()) / scores.std():+.2f} sigma of its own scan"
        )
    print(
        "\nThe planted control scores +14.27. A body best near +11.5 at under three"
        "\nsigma of a ten-thousand-cell scan is what a scan of noise looks like."
    )


if __name__ == "__main__":
    main()
