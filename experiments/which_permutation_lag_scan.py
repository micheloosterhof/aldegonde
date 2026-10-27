# ABOUTME: Asks whether the within-span permutation has a fixed geometry (columnar, rail fence,
# ABOUTME: reversal) by scanning the length transition table over lags and over inverted geometries.
"""Is the word permutation a fixed-geometry transposition, or a shuffle?

`length_adjacency_self_null.py` read the body's lag-1 transition table of block-length
classes at z = -0.10 against its own within-span shuffle, where intact order reads +5 to
+17. That excludes a permutation that keeps neighbours together (reversal, rotation). It
does not exclude a transposition with a fixed geometry: a columnar transposition of a
span's words with R rows puts English neighbours R positions apart in the output, so the
same table at lag R carries the intact-order signal. Two scans, both scored against the
within-span shuffle, which keeps every span's multiset:

- **lag scan**: the table over pairs (i, i + lag) for lags 1..LAGS, family p-value for
  the largest z over lags 2..LAGS; this sees any geometry with a fixed row count;
- **inversion scan**: each candidate geometry (columnar with R rows, columnar with C
  columns, rail fence with k rails, reversal) is undone on every span and the lag-1 table
  is scored; the true geometry restores intact order; family p-value over the geometries.

Both are calibrated first on the author's joined solved pages and on a joined prose window
at the body's block count, each with a planted geometry.

    python experiments/which_permutation_lag_scan.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from length_adjacency_self_null import (  # noqa: E402
    EDGES,
    JOIN_RATE,
    length_class,
    shuffled,
    windows,
)
from order_survives_in_the_lengths import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from sentences_do_not_end_long import join  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402

SEED = 20261028
DRAWS = 300
LAGS = 12


def columnar_rows(n: int, rows: int) -> list[int]:
    """Input indices in output order: written row-wise into `rows` rows, read by columns."""
    width = math.ceil(n / rows)
    return [
        r * width + c for c in range(width) for r in range(rows) if r * width + c < n
    ]


def columnar_cols(n: int, cols: int) -> list[int]:
    """Written row-wise into rows of width `cols`, read by columns."""
    rows = math.ceil(n / cols)
    return [r * cols + c for c in range(cols) for r in range(rows) if r * cols + c < n]


def rail_fence(n: int, rails: int) -> list[int]:
    """Written in a zigzag over `rails` rails, read rail by rail."""
    rail_of, r, step = [], 0, 1
    for _ in range(n):
        rail_of.append(r)
        if rails > 1:
            if r == 0:
                step = 1
            elif r == rails - 1:
                step = -1
            r += step
    return [i for k in range(rails) for i in range(n) if rail_of[i] == k]


def reversal(n: int, _: int = 0) -> list[int]:
    return list(range(n - 1, -1, -1))


GEOMETRIES = (
    [(f"columnar, {r} rows", columnar_rows, r) for r in range(2, 7)]
    + [(f"columnar, {c} columns", columnar_cols, c) for c in range(2, 9)]
    + [(f"rail fence, {k} rails", rail_fence, k) for k in range(2, 5)]
    + [("reversal", reversal, 0)]
)


def apply(span: list[int], perm) -> list[int]:
    return [span[i] for i in perm(len(span))]


def invert(span: list[int], perm) -> list[int]:
    p = perm(len(span))
    out = [0] * len(span)
    for j, i in enumerate(p):
        out[i] = span[j]
    return out


def table(spans, lag: int) -> np.ndarray:
    k = len(EDGES) + 1
    t = np.zeros((k, k))
    for s in spans:
        for a, b in zip(s, s[lag:]):
            t[length_class(a), length_class(b)] += 1
    return t


class Scorer:
    """Chi-square of a table against the within-span shuffle, per lag and per geometry,
    with the family null taken over one shared set of shuffles."""

    def __init__(self, spans, rng, draws=DRAWS) -> None:
        self.spans = spans
        fit = [shuffled(spans, rng) for _ in range(draws)]
        self.null_draws = [shuffled(spans, rng) for _ in range(draws)]
        self.lag_fit = {}
        for lag in range(1, LAGS + 1):
            t = np.array([table(f, lag) for f in fit])
            self.lag_fit[lag] = (t.mean(axis=0), t.std(axis=0, ddof=1))

    def chi(self, t, lag) -> float:
        mean, sd = self.lag_fit[lag]
        live = sd > 0
        return float((((t - mean)[live] / sd[live]) ** 2).sum())

    def lag_scan(self) -> dict:
        null = np.array(
            [
                [self.chi(table(d, lag), lag) for lag in range(1, LAGS + 1)]
                for d in self.null_draws
            ]
        )
        obs = np.array(
            [self.chi(table(self.spans, lag), lag) for lag in range(1, LAGS + 1)]
        )
        z = (obs - null.mean(axis=0)) / null.std(axis=0, ddof=1)
        z_null = (null - null.mean(axis=0)) / null.std(axis=0, ddof=1)
        top = z[1:].max()
        return {
            "z": z,
            "top": top,
            "family_p": float((z_null[:, 1:].max(axis=1) >= top).mean()),
        }

    def inversion_scan(self) -> dict:
        def all_geometries(rows):
            return [
                self.chi(
                    table([invert(s, lambda n, g=g, k=k: g(n, k)) for s in rows], 1), 1
                )
                for _, g, k in GEOMETRIES
            ]

        null = np.array([all_geometries(d) for d in self.null_draws])
        obs = np.array(all_geometries(self.spans))
        z = (obs - null.mean(axis=0)) / null.std(axis=0, ddof=1)
        z_null = (null - null.mean(axis=0)) / null.std(axis=0, ddof=1)
        top = z.max()
        return {
            "z": z,
            "top": top,
            "family_p": float((z_null.max(axis=1) >= top).mean()),
        }


def report(label: str, spans, rng) -> None:
    sc = Scorer(spans, rng)
    lags = sc.lag_scan()
    geo = sc.inversion_scan()
    print(f"\n{label}: {len(spans)} spans, {sum(len(s) for s in spans)} blocks")
    print(
        "  lag scan, z by lag 1.."
        + str(LAGS)
        + ":  "
        + " ".join(f"{v:+.1f}" for v in lags["z"])
    )
    print(
        f"    largest z over lags 2..{LAGS}: {lags['top']:+.2f}, family P = {lags['family_p']:.3f}"
    )
    order = np.argsort(-geo["z"])
    print(
        "  inversion scan, best three geometries: "
        + ", ".join(f"{GEOMETRIES[i][0]} {geo['z'][i]:+.1f}" for i in order[:3])
    )
    print(
        f"    largest z over {len(GEOMETRIES)} geometries: {geo['top']:+.2f}, family P = {geo['family_p']:.3f}"
    )


def main() -> None:
    rng = random.Random(SEED)
    body = [s for s in body_spans() if len(s) >= 2]
    size = sum(len(s) for s in body)
    author = [
        s
        for s in (join(list(s), JOIN_RATE, rng, forward=True) for s in author_spans())
        if len(s) >= 2
    ]
    prose = []
    for number in REGISTERS[:3]:
        path = fetch(number)
        if path is not None:
            prose += [s for s in register_spans(path, rng, JOIN_RATE) if len(s) >= 2]
    window = windows(prose, size, 1, rng)[0]

    print("Calibration (intact order, then a planted geometry)")
    report("author joined, intact", author, rng)
    report(
        "author joined, columnar 3 rows planted",
        [apply(s, lambda n: columnar_rows(n, 3)) for s in author],
        rng,
    )
    report("prose window, intact", window, rng)
    report(
        "prose window, columnar 3 rows planted",
        [apply(s, lambda n: columnar_rows(n, 3)) for s in window],
        rng,
    )
    report(
        "prose window, columnar 5 rows planted",
        [apply(s, lambda n: columnar_rows(n, 5)) for s in window],
        rng,
    )
    report(
        "prose window, columnar 4 columns planted",
        [apply(s, lambda n: columnar_cols(n, 4)) for s in window],
        rng,
    )
    report(
        "prose window, rail fence 3 rails planted",
        [apply(s, lambda n: rail_fence(n, 3)) for s in window],
        rng,
    )
    report("prose window, shuffled", shuffled(window, rng), rng)

    print("\nThe body")
    report("body, four-dot spans", body, rng)


if __name__ == "__main__":
    main()
