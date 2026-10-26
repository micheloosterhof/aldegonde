# ABOUTME: Asks whether the 28 lag-5 frames share any layout or content feature beyond their
# ABOUTME: geometry, against three nulls: a layout-preserving shuffle, the walk, and real matches.
"""Steps 1-3 of the frame program: do the frames share anything?

A frame is `c_i = c_(i+5)` and `c_(i+4) = c_(i+9)`. There are 28 against a chance
expectation near 16-18, so about ten are excess and the rest are chance frames that any
null reproduces. A feature can therefore show only if it is rare among chance frames and
near-universal among the excess ones; the power table is in the write-up.

Six features, fixed before looking:

  F1 section 4              the known pocket section (a check, not a discovery)
  F2 line-initial rune      one of the four matched runes opens a line
  F3 marked span            a word inside the span closes with a mark other than the plain
                            separator (four-dot, thirteen-dot, ...)
  F4 word-initial start     the first matched rune opens its word
  F5 S among x, y           either matched value is the rune S
  F6 both legs cross-word   neither leg sits inside one word

Three nulls, each producing frames in the LP's own layout:

  1. layout shuffle   the rune stream resampled at the observed doublet rate with word
                      lengths, lines and marks held; breaks the echo along with everything
  2. the walk         the doublet-dodging walk on prose re-cut to the LP's word lengths;
                      keeps the echo, the preventer and the word structure
  3. case-control     pairs of REAL lag-5 matches at separations 2, 3, 6, 7, 8, whose
                      counts sit at chance; selection held fixed with no model at all

Each feature is reported as the frame count against the pooled null rate (binomial),
with the Bonferroni factor for six features.

    python experiments/frame_feature_nulls.py [--shuffles 1000] [--walks 200]
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binom, chi2_contingency

from aldegonde import analysis, stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import encipher, order5_fixing  # noqa: E402
from frame_count_baseline import (  # noqa: E402
    LAG,
    flatten,
    match_indicator,
    prose_books,
)
from within_word_d5 import R2I, RUNES, WORD_BOUNDARIES, M  # noqa: E402

SEED = 20261027
FRAME = 4
CONTROL_SEPARATIONS = (2, 3, 6, 7, 8)
PLAIN_SEPARATOR = "①"
S_RUNE = R2I["ᛋ"]
FEATURES = (
    "F1 section 4",
    "F2 line-initial rune",
    "F3 marked span",
    "F4 word-initial start",
    "F5 S among x, y",
    "F6 both legs cross-word",
)


class Layout:
    """Per-rune section, line, word, and per-word closing glyph of the clean corpus."""

    def __init__(self, path: Path) -> None:
        text = path.read_text()
        self.section: list[int] = []
        self.line_start: list[bool] = []
        self.word: list[int] = []
        self.closer: list[str] = []
        sec = 0
        at_line_start = True
        in_word = False
        word = -1
        for ch in text:
            if ch in RUNES:
                if not in_word:
                    word += 1
                    in_word = True
                    self.closer.append(PLAIN_SEPARATOR)
                self.section.append(sec)
                self.line_start.append(at_line_start)
                self.word.append(word)
                at_line_start = False
            elif ch == "$":
                in_word = False
                sec += 1
                if sec >= 10:
                    break
            elif ch in WORD_BOUNDARIES:
                if in_word:
                    self.closer[word] = ch
                in_word = False
            elif ch == "\n":
                at_line_start = True
        self.owner = np.array(self.word)
        self.word_start = np.array(
            [i == 0 or self.word[i] != self.word[i - 1] for i in range(len(self.word))]
        )

    def features(self, stream: np.ndarray, i: int, d: int) -> list[bool]:
        """The six features of a match pair at (i, i+5) and (i+d, i+d+5)."""
        positions = (i, i + LAG, i + d, i + d + LAG)
        words_in_span = range(self.word[i], self.word[i + d + LAG] + 1)
        return [
            self.section[i] == 4,
            any(self.line_start[p] for p in positions),
            any(self.closer[w] != PLAIN_SEPARATOR for w in list(words_in_span)[:-1]),
            bool(self.word_start[i]),
            stream[i] == S_RUNE or stream[i + d] == S_RUNE,
            self.word[i] != self.word[i + LAG]
            and self.word[i + d] != self.word[i + d + LAG],
        ]


def pair_positions(m: np.ndarray, d: int) -> np.ndarray:
    return np.flatnonzero(m[:-d] & m[d:])


def feature_matrix(layout: Layout, stream: np.ndarray, d: int) -> np.ndarray:
    m = match_indicator(stream)
    rows = [layout.features(stream, int(i), d) for i in pair_positions(m, d)]
    return np.array(rows, dtype=bool).reshape(-1, len(FEATURES))


def shuffle_null(
    layout: Layout, stream: np.ndarray, draws: int, rng: random.Random, observed: int
) -> np.ndarray:
    rate = float(np.mean(stream[:-1] == stream[1:]))
    model = stats.doublet_shuffle(rate)
    rows = [
        feature_matrix(layout, np.array(model(list(stream), rng)), FRAME)
        for _ in range(draws)
    ]
    count_line("layout shuffle", rows, observed)
    return np.vstack(rows)


def count_line(label: str, rows: list[np.ndarray], observed: int) -> None:
    counts = np.array([len(r) for r in rows])
    tail = (np.sum(counts >= observed) + 1) / (len(counts) + 1)
    print(
        f"  {label}: {len(counts)} draws, {counts.mean():.1f} ± {counts.std():.1f} frames"
        f" each, P(>= {observed}) = {tail:.3f}"
    )


def walk_null(
    layout: Layout, lengths: list[int], draws: int, rng: random.Random, observed: int
) -> np.ndarray:
    # prose runs with at least as many runes as the LP, re-cut to its word lengths
    need = sum(lengths)
    windows = []
    for book in prose_books():
        runes = [r for w in book for r in w]
        windows += [runes[s : s + need] for s in range(0, len(runes) - need + 1, need)]
    rows = []
    for t in range(draws):
        plain = analysis.recut_words(windows[t % len(windows)], lengths)
        g = order5_fixing(rng.sample(range(M), 4), rng)
        sigma = rng.sample(range(M), M)
        cipher = encipher(plain, rng.sample(range(M), M), g, sigma)
        stream, _ = flatten(cipher)
        rows.append(feature_matrix(layout, stream, FRAME))
    count_line("the walk", rows, observed)
    return np.vstack(rows)


def control_rows(layout: Layout, stream: np.ndarray) -> np.ndarray:
    rows = np.vstack([feature_matrix(layout, stream, d) for d in CONTROL_SEPARATIONS])
    print(
        f"  case-control: {len(rows)} real match pairs at separations {CONTROL_SEPARATIONS}"
    )
    return rows


def report(frames: np.ndarray, nulls: dict[str, np.ndarray]) -> None:
    n = len(frames)
    print(f"\n{'feature':<26}{'frames':>8}" + "".join(f"{name:>26}" for name in nulls))
    print(
        f"{'':<26}{'of ' + str(n):>8}"
        + "".join(f"{'null rate   P(>=)  x6':>26}" for _ in nulls)
    )
    for k, name in enumerate(FEATURES):
        obs = int(frames[:, k].sum())
        line = f"{name:<26}{obs:>8}"
        for rows in nulls.values():
            p = rows[:, k].mean()
            tail = binom.sf(obs - 1, n, p)
            line += f"{p:>14.3f}{tail:>8.3f}{min(1.0, 6 * tail):>6.2f}"
        print(line)


def identity_check(frames_xy: np.ndarray, null_xy: np.ndarray) -> None:
    """Are the matched values x, y distributed as in the shuffle null?"""
    table = np.array(
        [np.bincount(frames_xy, minlength=M), np.bincount(null_xy, minlength=M)]
    )
    table = table[:, table.sum(0) > 0]
    chi2, p, dof, _ = chi2_contingency(table)
    print(
        f"\nmatched values x, y against the layout shuffle: chi2 {chi2:.1f} on {dof} df, p = {p:.2f}"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shuffles", type=int, default=1000)
    ap.add_argument("--walks", type=int, default=200)
    args = ap.parse_args()
    rng = random.Random(SEED)
    layout = Layout(ROOT / "data/page0-56.txt")
    sections = __import__("within_word_d5").parse_clean_sections(
        str(ROOT / "data/page0-56.txt")
    )
    words = [w for s in sections for w in s]
    stream, owner = flatten(words)
    assert len(stream) == len(layout.word) and np.array_equal(owner, layout.owner), (
        "layout parse disagrees"
    )
    lengths = [len(w) for w in words]

    frames = feature_matrix(layout, stream, FRAME)
    print(f"LP: {len(frames)} frames")
    nulls = {
        "layout shuffle": shuffle_null(layout, stream, args.shuffles, rng, len(frames)),
        "the walk": walk_null(layout, lengths, args.walks, rng, len(frames)),
        "case-control": control_rows(layout, stream),
    }
    report(frames, nulls)

    m = match_indicator(stream)
    fx = pair_positions(m, FRAME)
    frames_xy = np.concatenate([stream[fx], stream[fx + FRAME]])
    model = stats.doublet_shuffle(float(np.mean(stream[:-1] == stream[1:])))
    null_xy = []
    for _ in range(200):
        s = np.array(model(list(stream), rng))
        px = pair_positions(match_indicator(s), FRAME)
        null_xy.append(np.concatenate([s[px], s[px + FRAME]]))
    identity_check(frames_xy, np.concatenate(null_xy))


if __name__ == "__main__":
    main()
