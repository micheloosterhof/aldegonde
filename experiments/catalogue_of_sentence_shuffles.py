# ABOUTME: Enumerates the deterministic word shuffles that work at any sentence length and tests
# ABOUTME: each on the body by undoing it on every span and scoring the lag-1 length table.
"""Which deterministic sentence shuffle, if any, wrote the body's word order?

The words inside each four-dot span are not in English order, and the sixteen geometries
of `which_permutation_lag_scan.py` do not restore it. This is the full catalogue of
rule-based shuffles that are defined for every sentence length, so that a reader with the
rule can undo them:

- columnar: write the words in rows of a fixed width (2 to 10), read the columns in any
  order (every order up to width 6, forward and reverse above), downwards, upwards or
  alternating; the same with a fixed number of rows; and the inverse of each (write
  by columns, read by rows);
- rail fence with 2 to 6 rails at every starting offset, and its inverse;
- reversal, rotations, swapped halves, reversed halves, middle-out and ends-in orders,
  reversed blocks of 2 to 5 words, and their inverses.

Each candidate is undone on every span and the lag-1 transition table of length classes
is scored against the body's own within-span shuffle; the right rule restores intact
order, which reads +13 at the body's size. One family p-value covers the catalogue, from
the same shuffle draws scored under every rule.

A shuffle that sorts the words by something visible in the ciphertext (first rune, last
rune, Gematria sum, rune order) is tested separately: the count of ascending adjacent
pairs inside spans against the shuffle. A sort on the plaintext is invisible here.

    python experiments/catalogue_of_sentence_shuffles.py
"""

from __future__ import annotations

import itertools
import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from frame_feature_nulls import Layout  # noqa: E402
from length_adjacency_self_null import JOIN_RATE, length_class, windows  # noqa: E402
from order_survives_in_the_lengths import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import body_spans  # noqa: E402
from within_word_d5 import parse_clean_sections  # noqa: E402

from aldegonde import c3301  # noqa: E402

SEED = 20261028
FIT_DRAWS = 300
NULL_DRAWS = 200
CLASSES = 5
MARK = "④"


# --- the catalogue -------------------------------------------------------------------


def columnar(n: int, width: int, order: tuple[int, ...], direction: str) -> list[int]:
    """Rows of `width`, columns read in `order`, each down, up or alternating."""
    rows = math.ceil(n / width)
    out = []
    for j, c in enumerate(order):
        col = [r * width + c for r in range(rows) if r * width + c < n]
        if direction == "up" or (direction == "alternating" and j % 2):
            col.reverse()
        out.extend(col)
    return out


def by_rows(n: int, rows: int, reverse: bool, direction: str) -> list[int]:  # noqa: FBT001
    width = math.ceil(n / rows)
    order = tuple(range(width - 1, -1, -1) if reverse else range(width))
    return columnar(n, width, order, direction)


def rail(n: int, rails: int, offset: int) -> list[int]:
    """Zigzag over `rails` rails starting `offset` steps into the cycle."""
    period = 2 * (rails - 1)
    rail_of = []
    for i in range(n):
        t = (i + offset) % period
        rail_of.append(t if t < rails else period - t)
    return [i for k in range(rails) for i in range(n) if rail_of[i] == k]


def rotation(n: int, k: int) -> list[int]:
    return [(i + k) % n for i in range(n)]


def swapped_halves(n: int) -> list[int]:
    h = n // 2
    return list(range(h, n)) + list(range(h))


def reversed_halves(n: int) -> list[int]:
    h = n // 2
    return list(range(h - 1, -1, -1)) + list(range(n - 1, h - 1, -1))


def middle_out(n: int, *, right_first: bool) -> list[int]:
    left, right = (n - 1) // 2, (n - 1) // 2 + 1
    out = []
    for step in range(n):
        if (step % 2 == 0) == right_first and right < n:
            out.append(right)
            right += 1
        elif left >= 0:
            out.append(left)
            left -= 1
        else:
            out.append(right)
            right += 1
    return out


def ends_in(n: int, *, right_first: bool) -> list[int]:
    left, right = 0, n - 1
    out = []
    while left <= right:
        a, b = (right, left) if right_first else (left, right)
        out.append(a)
        if left != right:
            out.append(b)
        left += 1
        right -= 1
    return out


def reversed_blocks(n: int, size: int) -> list[int]:
    out = []
    for start in range(0, n, size):
        out.extend(range(min(n, start + size) - 1, start - 1, -1))
    return out


def inverse(perm: list[int]) -> list[int]:
    out = [0] * len(perm)
    for j, i in enumerate(perm):
        out[i] = j
    return out


def catalogue() -> list[tuple[str, object]]:
    """(label, function of n) for every rule; each is followed by its inverse."""
    rules: list[tuple[str, object]] = []
    for width in range(2, 11):
        orders = (
            list(itertools.permutations(range(width)))
            if width <= 6
            else [tuple(range(width)), tuple(range(width - 1, -1, -1))]
        )
        for order in orders:
            for direction in ("down", "up", "alternating"):
                rules.append(
                    (
                        f"columnar width {width}, columns {order}, {direction}",
                        lambda n, w=width, o=order, d=direction: columnar(n, w, o, d),
                    )
                )
    for rows in range(2, 11):
        for reverse in (False, True):
            for direction in ("down", "up", "alternating"):
                rules.append(
                    (
                        f"columnar {rows} rows, columns {'reversed' if reverse else 'forward'}, {direction}",
                        lambda n, r=rows, v=reverse, d=direction: by_rows(n, r, v, d),
                    )
                )
    for rails in range(2, 7):
        for offset in range(2 * (rails - 1)):
            rules.append(
                (
                    f"rail fence {rails} rails, offset {offset}",
                    lambda n, k=rails, o=offset: rail(n, k, o),
                )
            )
    rules.append(("reversal", lambda n: list(range(n - 1, -1, -1))))
    for k in (1, 2, 3, -1, -2, -3):
        rules.append((f"rotation by {k}", lambda n, k=k: rotation(n, k)))
    rules.append(("swapped halves", swapped_halves))
    rules.append(("reversed halves", reversed_halves))
    for right_first in (False, True):
        rules.append(
            (
                f"middle-out, {'right' if right_first else 'left'} first",
                lambda n, r=right_first: middle_out(n, right_first=r),
            )
        )
        rules.append(
            (
                f"ends-in, {'right' if right_first else 'left'} first",
                lambda n, r=right_first: ends_in(n, right_first=r),
            )
        )
    for size in range(2, 6):
        rules.append(
            (f"reversed blocks of {size}", lambda n, s=size: reversed_blocks(n, s))
        )
    with_inverses = []
    for label, fn in rules:
        with_inverses.append((label, fn))
        with_inverses.append((f"inverse of {label}", lambda n, f=fn: inverse(f(n))))
    return with_inverses


# --- the scorer ----------------------------------------------------------------------


class Corpus:
    """Length classes of a corpus of spans, laid out end to end, with the pair mask."""

    def __init__(self, spans: list[list[int]]) -> None:
        self.spans = [list(s) for s in spans]
        self.classes = np.array([length_class(x) for s in spans for x in s])
        self.starts = np.cumsum([0] + [len(s) for s in spans[:-1]])
        same = np.ones(len(self.classes) - 1, dtype=bool)
        same[self.starts[1:] - 1] = False
        self.pair_mask = same
        self.lengths = sorted({len(s) for s in spans})

    def recovery_index(self, fn) -> np.ndarray:
        """Index into the visible sequence that undoes the rule on every span."""
        per_n = {n: inverse(fn(n)) for n in self.lengths}
        idx = np.empty(len(self.classes), dtype=int)
        for start, s in zip(self.starts, self.spans):
            idx[start : start + len(s)] = start + np.array(per_n[len(s)])
        return idx

    def table(self, classes: np.ndarray) -> np.ndarray:
        a, b = classes[:-1][self.pair_mask], classes[1:][self.pair_mask]
        return np.bincount(CLASSES * a + b, minlength=CLASSES * CLASSES).astype(float)

    def shuffled_classes(self, rng: np.random.Generator) -> np.ndarray:
        out = self.classes.copy()
        for start, s in zip(self.starts, self.spans):
            rng.shuffle(out[start : start + len(s)])
        return out


def scan(corpus: Corpus, rules, rng: np.random.Generator) -> dict:
    fit = np.array(
        [corpus.table(corpus.shuffled_classes(rng)) for _ in range(FIT_DRAWS)]
    )
    mean, sd = fit.mean(axis=0), fit.std(axis=0, ddof=1)
    live = sd > 0

    def chi(t):
        return float((((t - mean)[live] / sd[live]) ** 2).sum())

    indices = [corpus.recovery_index(fn) for _, fn in rules]
    # one draw set standardises every rule, a separate set is the family null: a draw
    # standardised by a set it belongs to is capped at (n - 1) / sqrt(n), the observed
    # data is not
    draws = np.array(
        [
            [chi(corpus.table(draw[idx])) for idx in indices]
            for draw in (corpus.shuffled_classes(rng) for _ in range(2 * NULL_DRAWS))
        ]
    )
    scale, null = draws[:NULL_DRAWS], draws[NULL_DRAWS:]
    obs = np.array([chi(corpus.table(corpus.classes[idx])) for idx in indices])
    z = (obs - scale.mean(axis=0)) / scale.std(axis=0, ddof=1)
    z_null = (null - scale.mean(axis=0)) / scale.std(axis=0, ddof=1)
    return {
        "z": z,
        "top": float(z.max()),
        "family_p": float((z_null.max(axis=1) >= z.max()).mean()),
        "null_top": z_null.max(axis=1),
    }


def report(label: str, spans, rules, rng) -> dict:
    r = scan(Corpus(spans), rules, rng)
    order = np.argsort(-r["z"])
    print(f"\n{label}: {len(spans)} spans, {sum(len(s) for s in spans)} blocks")
    for i in order[:3]:
        print(f"  {r['z'][i]:+6.2f}  {rules[i][0]}")
    print(
        f"  largest z {r['top']:+.2f} over {len(rules)} rules; family P = {r['family_p']:.3f}"
        f" (null largest {r['null_top'].mean():.2f} +- {r['null_top'].std():.2f})"
    )
    return r


def final_block_check(spans, fn, label: str, rng: np.random.Generator) -> None:
    """A channel the scan did not use: under the right inversion the sentence-final long
    block returns (joined prose +1.28 +- 0.24, the author +0.42 +- 0.29 in
    `permutation_unit_size.py`)."""
    from permutation_unit_size import MIN_SPAN, bootstrap  # noqa: PLC0415

    long = [s for s in spans if len(s) >= MIN_SPAN]
    undone = []
    for s in long:
        inv = inverse(fn(len(s)))
        undone.append([s[inv[i]] for i in range(len(s))])
    print(
        f"\nSentence-final block under the winner's inversion ({label}), {len(long)} spans of {MIN_SPAN}+ blocks"
    )
    for name, rows in (("as written", long), ("undone", undone)):
        e, se = bootstrap(rows, rng)
        null = []
        for _ in range(2000):
            draw = [rng.permutation(s) for s in rows]
            null.append(np.mean([s[-1] - s.mean() for s in draw]))
        null = np.array(null)
        print(
            f"  {name:<11} last block minus span mean {e:+.3f} +- {se:.3f};"
            f" within-span shuffle {null.mean():+.3f} +- {null.std(ddof=1):.3f}; z {(e - null.mean()) / null.std(ddof=1):+.2f}"
        )


def held_out(spans, rules, rng: np.random.Generator) -> None:
    """The rule selected on one half of the spans, scored on the other half."""
    print(
        "\nHeld-out check: the best rule on one half, read on the other"
        "\n  (no power: a rule at the body's strength reads about +2.6 on a half, under the scan's null maximum)"
    )
    halves = (
        ("odd / even spans", spans[0::2], spans[1::2]),
        ("first / second half", spans[: len(spans) // 2], spans[len(spans) // 2 :]),
    )
    for name, a, b in halves:
        for sel, held, sl, hl in ((a, b, "first", "second"), (b, a, "second", "first")):
            r = scan(Corpus(sel), rules, rng)
            top = int(np.argmax(r["z"]))
            single = scan(Corpus(held), [rules[top]], rng)
            print(
                f"  {name}, selected on the {sl}: {rules[top][0]}"
                f" z {r['z'][top]:+.2f} (family P {r['family_p']:.2f});"
                f" on the {hl}: z {single['z'][0]:+.2f}"
            )


# --- sorts on visible features -----------------------------------------------------


def body_word_spans() -> list[list[list[int]]]:
    """Rune words grouped into the four-dot spans."""
    path = ROOT / "data/page0-56.txt"
    layout = Layout(path)
    words = [w for sec in parse_clean_sections(str(path)) for w in sec]
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        if layout.closer[i] == MARK:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def ascending_pairs(spans, key) -> int:
    return sum(key(a) < key(b) for s in spans for a, b in zip(s, s[1:]))


def sort_tests(spans, rng: random.Random) -> None:
    values = [c3301.r2v(c3301.i2r(i)) for i in range(29)]
    keys = {
        "first rune (Gematria order)": lambda w: w[0],
        "last rune": lambda w: w[-1],
        "Gematria sum": lambda w: sum(values[r] for r in w),
        "rune order (lexicographic)": lambda w: tuple(w),
        "length": len,
    }
    print(
        f"\nSorted after encipherment? ascending adjacent pairs inside {len(spans)} spans"
    )
    for label, key in keys.items():
        obs = ascending_pairs(spans, key)
        null = []
        for _ in range(NULL_DRAWS):
            draw = []
            for s in spans:
                s = list(s)
                rng.shuffle(s)
                draw.append(s)
            null.append(ascending_pairs(draw, key))
        null = np.array(null)
        z = (obs - null.mean()) / null.std(ddof=1)
        print(
            f"  {label:<30} {obs:>5}  shuffle {null.mean():7.1f} +- {null.std():5.1f}  z {z:+.2f}"
        )
    print(
        "  a sort would read far above the shuffle (ascending) or far below (descending)"
    )
    # relations between neighbours that no sort and no length class would show
    relations = {
        "same length parity as the previous word": lambda a, b: (
            len(a) % 2 == len(b) % 2
        ),
        "same first rune as the previous word": lambda a, b: a[0] == b[0],
        "same last rune as the previous word": lambda a, b: a[-1] == b[-1],
        "first rune equals the previous word's last rune": lambda a, b: a[-1] == b[0],
        "same length as the previous word": lambda a, b: len(a) == len(b),
    }
    print(f"\nNeighbour relations inside {len(spans)} spans, against the shuffle")
    for label, rel in relations.items():
        obs = sum(rel(a, b) for s in spans for a, b in zip(s, s[1:]))
        null = []
        for _ in range(NULL_DRAWS):
            draw = []
            for s in spans:
                s = list(s)
                rng.shuffle(s)
                draw.append(s)
            null.append(sum(rel(a, b) for s in draw for a, b in zip(s, s[1:])))
        null = np.array(null)
        print(
            f"  {label:<48} {obs:>5}  shuffle {null.mean():7.1f} +- {null.std():5.1f}"
            f"  z {(obs - null.mean()) / null.std(ddof=1):+.2f}"
        )


def main() -> None:
    rng = random.Random(SEED)
    nrng = np.random.default_rng(SEED)
    rules = catalogue()
    print(f"catalogue: {len(rules)} rules including inverses")

    body = [s for s in body_spans() if len(s) >= 2]
    size = sum(len(s) for s in body)
    prose = []
    for number in REGISTERS[:3]:
        path = fetch(number)
        if path is not None:
            prose += [s for s in register_spans(path, rng, JOIN_RATE) if len(s) >= 2]
    window = windows(prose, size, 1, rng)[0]

    print("\nCalibration on a joined prose window at the body's size")
    report("intact", window, rules, nrng)
    planted = [
        (
            "columnar width 5, columns (3, 0, 4, 1, 2), up",
            lambda n: columnar(n, 5, (3, 0, 4, 1, 2), "up"),
        ),
        ("rail fence 4 rails, offset 3", lambda n: rail(n, 4, 3)),
        ("ends-in, right first", lambda n: ends_in(n, right_first=True)),
    ]
    for label, fn in planted:
        report(
            f"planted {label}",
            [[s[i] for i in fn(len(s))] for s in window],
            rules,
            nrng,
        )
    shuffled = []
    for s in window:
        s = list(s)
        rng.shuffle(s)
        shuffled.append(s)
    report("shuffled", shuffled, rules, nrng)

    print("\nThe body")
    r = report("body, four-dot spans", body, rules, nrng)
    held_out(body, rules, nrng)
    top = int(np.argmax(r["z"]))
    final_block_check(body, rules[top][1], rules[top][0], nrng)
    sort_tests([s for s in body_word_spans() if len(s) >= 2], rng)


if __name__ == "__main__":
    main()
