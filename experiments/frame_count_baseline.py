# ABOUTME: Re-prices the 28 lag-5 frames (x···yx···y) against a null that carries the word
# ABOUTME: layout and the within-word echo, and measures frames in running runeglish prose.
"""Step 0 of the frame program: fix the baseline before looking at the events.

The frame is two lag-5 matches at separation 4, `c_i = c_(i+5)` and `c_(i+4) = c_(i+9)`.
Every figure on record prices its count (28) against uniform text or uniformly scattered
match positions. Neither carries the word layout or the within-word echo, so the
expectation 17.7 (= 479·478/12,950) conditions on the observed match total -- which is
itself the pairing -- and ignores that within-word legs match at 0.049 and cross-word
legs at 1/29.

Two measurements:

1. The LP count against independent Bernoulli matches with per-leg rates set by word
   geometry (within-word legs at the LP's own echo rate, cross-word legs at chance),
   analytically and by simulation, for every separation; and the LP's frames by
   boundaries crossed against the uniform-scatter null, for comparison with prose.
2. Frames in RUNNING runeglish prose, book spelling, windows of the LP's 2,928 words,
   split by how many word boundaries the frame crosses. `plaintext_lag5_pairing.py`
   measured only within-word frames on concatenated dictionary words; frames hardly fit
   inside a word (1 of the LP's 28), so the cross-word rate in real prose is what matters.

    python experiments/frame_count_baseline.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import BOOK_CACHE, PROSE_REGISTERS  # noqa: E402
from within_word_d5 import M, parse_clean_sections  # noqa: E402

LAG = 5
SEPARATIONS = (1, 2, 3, 4, 6, 7, 8)
LP_WORDS = 2928
TRIALS = 20000
SEED = 20261027
B_CLASSES = 4  # 0, 1, 2, 3+


def flatten(words: list[list[int]]) -> tuple[np.ndarray, np.ndarray]:
    stream = np.array([r for w in words for r in w])
    owner = np.array([k for k, w in enumerate(words) for _ in w])
    return stream, owner


def match_indicator(stream: np.ndarray) -> np.ndarray:
    return stream[:-LAG] == stream[LAG:]


def pair_counts(m: np.ndarray) -> dict[int, int]:
    return {d: int(np.sum(m[:-d] & m[d:])) for d in SEPARATIONS}


def by_boundary(
    m: np.ndarray, owner: np.ndarray, d: int
) -> tuple[np.ndarray, np.ndarray]:
    """Pairs at separation d by boundaries crossed over the span, observed and
    expected if the same number of matches were scattered uniformly."""
    span = d + LAG
    b_class = np.minimum(owner[span:] - owner[:-span], B_CLASSES - 1)
    n = len(m)
    pairs = m[:-d] & m[d:]
    obs = np.array(
        [np.sum(pairs & (b_class == b)) for b in range(B_CLASSES)], dtype=float
    )
    per_position = m.sum() * (m.sum() - 1) / (n * (n - 1))
    exp = np.array([per_position * np.sum(b_class == b) for b in range(B_CLASSES)])
    return obs, exp


def print_by_boundary(obs: np.ndarray, exp: np.ndarray) -> None:
    for b in range(B_CLASSES):
        label = f"b={b}" if b < B_CLASSES - 1 else f"b>={B_CLASSES - 1}"
        ratio = obs[b] / exp[b] if exp[b] else float("nan")
        z = (obs[b] - exp[b]) / np.sqrt(exp[b]) if exp[b] else float("nan")
        print(
            f"    {label:<5} observed {obs[b]:>7.0f}  null {exp[b]:>8.1f}  ratio {ratio:5.2f}  z {z:+6.1f}"
        )
    print(
        f"    all   observed {obs.sum():>7.0f}  null {exp.sum():>8.1f}  ratio {obs.sum() / exp.sum():5.2f}"
    )


def lp_baseline(words: list[list[int]]) -> None:
    stream, owner = flatten(words)
    m = match_indicator(stream)
    n = len(m)
    within_leg = owner[:-LAG] == owner[LAG:]
    rate_within = m[within_leg].mean()
    rate_cross = m[~within_leg].mean()
    print(f"LP: {len(stream)} runes, {m.sum()} lag-5 matches over {n} legs")
    print(
        f"  within-word legs {within_leg.sum()}: rate {rate_within:.4f}; "
        f"cross-word legs {(~within_leg).sum()}: rate {rate_cross:.4f} (chance {1 / M:.4f})"
    )
    observed = pair_counts(m)
    # per-leg rates from geometry: the echo inside words, chance across
    p = np.where(within_leg, rate_within, 1 / M)
    rng = np.random.default_rng(SEED)
    sims = {d: np.zeros(TRIALS, dtype=int) for d in SEPARATIONS}
    for t in range(TRIALS):
        sm = rng.random(n) < p
        for d, v in pair_counts(sm).items():
            sims[d][t] = v
    uniform = m.sum() * (m.sum() - 1) / n
    print(
        f"\n  pairs of lag-5 matches at separation d; the record's null is {uniform:.1f} at every d"
    )
    print(
        f"  {'d':>3}{'observed':>10}{'analytic':>10}{'sim mean':>10}{'sd':>7}{'P(>=obs)':>10}"
    )
    for d in SEPARATIONS:
        analytic = float(np.sum(p[:-d] * p[d:]))
        s = sims[d]
        pv = (np.sum(s >= observed[d]) + 1) / (TRIALS + 1)
        print(
            f"  {d:>3}{observed[d]:>10}{analytic:>10.1f}{s.mean():>10.1f}{s.std():>7.1f}{pv:>10.4f}"
        )
    for d in (1, 4):
        print(f"\n  LP separation {d} by boundaries crossed, uniform-scatter null:")
        print_by_boundary(*by_boundary(m, owner, d))


def prose_books() -> list[list[list[int]]]:
    books = []
    for number in PROSE_REGISTERS:
        if number is None:
            continue
        path = BOOK_CACHE / f"pg{number}.txt"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        words = [c3301.encode_english(w) for w in re.findall(r"[A-Za-z]+", text)]
        words = [w for w in words if w]
        trim = len(words) // 10
        books.append(words[trim : len(words) - trim])
    return books


def prose_frames(books: list[list[list[int]]]) -> None:
    print(
        "\nrunning runeglish prose, book spelling, windows of 2,928 consecutive words,"
    )
    print("pairs by boundaries crossed against each window's own uniform-scatter null")
    obs = {d: np.zeros(B_CLASSES) for d in (1, 4)}
    exp = {d: np.zeros(B_CLASSES) for d in (1, 4)}
    windows = 0
    mono = []
    for book in books:
        for start in range(0, len(book) - LP_WORDS + 1, LP_WORDS):
            stream, owner = flatten(book[start : start + LP_WORDS])
            m = match_indicator(stream)
            mono.append(m.mean() * M)
            windows += 1
            for d in (1, 4):
                o, e = by_boundary(m, owner, d)
                obs[d] += o
                exp[d] += e
    print(
        f"  {windows} windows; monograph lag-5 IoC {np.mean(mono):.3f} ± {np.std(mono):.3f}"
    )
    for d in (1, 4):
        print(f"  separation {d}:")
        print_by_boundary(obs[d], exp[d])


def main() -> None:
    sections = parse_clean_sections(str(ROOT / "data/page0-56.txt"))
    lp_baseline([w for s in sections for w in s])
    prose_frames(prose_books())


if __name__ == "__main__":
    main()
