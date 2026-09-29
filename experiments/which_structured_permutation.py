# ABOUTME: Scores structured word-order permutations that work at any sentence length
# ABOUTME: against the body's two span-edge length profiles, which constrain them sharply.
"""If the words were rearranged by a rule rather than shuffled, the edges say which rule.

`where_in_the_distribution_is_the_anomaly.py` reads both span edges as length-class
profiles rather than means, and they disagree:

- the **first** block of a body span carries the LP author's own span-initial signature,
  cell for cell -- +0.054 against his +0.058 in the 1-2 class, -0.067 against -0.068 in
  3-4;
- the **last** block carries nothing. Every class sits within 0.04 of the span interior,
  and it is 3.7 sigma from the ten registers in the 7+ class where English puts its
  sentence-final weight.

## What the two edges can and cannot do

**The last edge carries the test.** Identity fails it at chi2 = 31.7 on four degrees of
freedom -- the body's span-final block is not an English sentence-final word, stated as a
profile rather than a mean.

**The first edge is weaker than it looks.** The body's first-block profile matches the
author's cell for cell, but the ten registers disagree among themselves by +-0.055 and
+-0.092 in the first two classes, so against that spread nearly every rule fits: identity
scores 6.7 and a full shuffle 5.3. The one thing it does exclude is *reversal*, at 22.2,
because that puts the long sentence-final word into position 0. So "position 0 is fixed"
is supported against the author and not against the registers, and is not claimed here.

## The rules tested

Every rule here is defined for a sentence of any length, which is the property a scribal
convention would need:

| rule | sends position i to |
|---|---|
| identity | i |
| reverse | n-1-i |
| rotate left k | (i+k) mod n, for k = 1, 2, 3 |
| swap adjacent pairs | i xor 1 |
| odd-even split | even positions in order, then odd |
| even-odd split | odd positions in order, then even |
| keep first, reverse rest | 0, then n-1 down to 1 |
| keep first, shuffle rest | 0, then the rest permuted |
| rail fence, 2 and 3 rails | the zigzag reading order |
| columnar, 2 to 4 columns | written in rows, read down columns |
| outward-in | 0, n-1, 1, n-2, ... |
| full shuffle | a uniform permutation |

## How they are scored

Each rule is applied to the ten registers' sentences *before* the short-unit joining,
since a scribal rearrangement would come before a scribal merge. The resulting spans give
an eight-number fingerprint -- four length classes at each edge -- compared with the
body's by chi-squared, carrying both the body's sampling error and the spread across the
ten registers.

## Result: the corpus constrains the destination, not the rule

| rule | chi2 first | chi2 last | chi2 both | P |
|---|---|---|---|---|
| keep first, reverse rest | 5.7 | 1.8 | 7.5 | 0.48 |
| rotate left 2 | 6.7 | 1.4 | 8.1 | 0.42 |
| **full shuffle** | 5.3 | 3.1 | 8.5 | 0.39 |
| rotate left 3 | 5.9 | 2.8 | 8.8 | 0.36 |
| outward-in | 5.8 | 4.1 | 9.9 | 0.27 |
| keep first, shuffle rest | 8.2 | 3.5 | 11.7 | 0.17 |
| rail fence 3 / columnar 3 / columnar 4 | ~8.3 | 5.2-5.9 | 13.6-14.3 | 0.07-0.09 |
| columnar 2 = rail fence 2 = odd-even split | ~8.1 | 9.5-9.9 | 17.5-18.0 | 0.02 |
| even-odd split | 8.2 | 10.2 | 18.4 | 0.018 |
| swap adjacent pairs | 9.6 | 9.1 | 18.7 | 0.017 |
| rotate left 1 | 8.9 | 10.3 | 19.2 | 0.014 |
| reverse | **22.2** | 6.4 | 28.7 | 0.0004 |
| **identity** | 6.7 | **31.7** | **38.5** | **2e-6** |

**No structured rule beats a full shuffle.** The top five sit within 2.4 of each other
with the shuffle among them, so the corpus cannot name a rule.

**But it says exactly what the last slot may hold.** Sorting the rules by what lands
there makes the last-edge misfit nearly monotone, correlation +0.71:

| what lands in the last slot | rules | chi2 last |
|---|---|---|
| the sentence's own final word, always | identity | 31.7 |
| that word about half the time | swap pairs, columnar 2, odd-even, even-odd | 9.1-10.2 |
| the sentence's *first* word | rotate left 1, reverse | 10.3, 6.4 |
| that word a quarter to a third of the time | rail fence 3, columnar 3, columnar 4 | 5.2-5.9 |
| an interior word, essentially always | rotate 2, rotate 3, keep-first-reverse-rest, outward-in, shuffle | 1.4-4.1 |

So the constraint is on the destination: **the last block of a body span holds a word that
was neither its sentence's last nor its sentence's first.** Every rule is penalised in
proportion to how often it violates that, and any rule satisfying it survives.

Note that columnar-2, rail-fence-2 and odd-even split are the *same permutation*
(`s[0::2] + s[1::2]`); their scores differ only by the joining draw, which is a useful
check that the scatter between rules is small.

    python which_structured_permutation.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from order_survives_in_the_lengths import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from sentences_do_not_end_long import join  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402
from where_in_the_distribution_is_the_anomaly import CLASSES, cells, lift  # noqa: E402

JOIN_RATE = 0.40
MIN_SPAN = 3


def rotate(k):
    return lambda s, rng: [s[(i + k) % len(s)] for i in range(len(s))]


def swap_pairs(s, rng):
    out = list(s)
    for i in range(0, len(s) - 1, 2):
        out[i], out[i + 1] = out[i + 1], out[i]
    return out


def odd_even(s, rng):
    return s[0::2] + s[1::2]


def even_odd(s, rng):
    return s[1::2] + s[0::2]


def keep_first_reverse(s, rng):
    return [s[0]] + s[:0:-1]


def keep_first_shuffle(s, rng):
    tail = s[1:]
    rng.shuffle(tail)
    return [s[0]] + tail


def rail_fence(rails):
    def rule(s, rng):
        lanes = [[] for _ in range(rails)]
        lane, step = 0, 1
        for x in s:
            lanes[lane].append(x)
            if rails > 1:
                if lane == rails - 1:
                    step = -1
                elif lane == 0:
                    step = 1
                lane += step
        return [x for lane in lanes for x in lane]

    return rule


def columnar(columns):
    def rule(s, rng):
        return [s[i] for c in range(columns) for i in range(c, len(s), columns)]

    return rule


def outward_in(s, rng):
    out, lo, hi = [], 0, len(s) - 1
    while lo <= hi:
        out.append(s[lo])
        if lo != hi:
            out.append(s[hi])
        lo, hi = lo + 1, hi - 1
    return out


def shuffle_all(s, rng):
    out = list(s)
    rng.shuffle(out)
    return out


RULES = (
    ("identity", lambda s, rng: list(s)),
    ("reverse", lambda s, rng: s[::-1]),
    ("rotate left 1", rotate(1)),
    ("rotate left 2", rotate(2)),
    ("rotate left 3", rotate(3)),
    ("swap adjacent pairs", swap_pairs),
    ("odd-even split", odd_even),
    ("even-odd split", even_odd),
    ("keep first, reverse rest", keep_first_reverse),
    ("keep first, shuffle rest", keep_first_shuffle),
    ("rail fence, 2 rails", rail_fence(2)),
    ("rail fence, 3 rails", rail_fence(3)),
    ("columnar, 2 columns", columnar(2)),
    ("columnar, 3 columns", columnar(3)),
    ("columnar, 4 columns", columnar(4)),
    ("outward-in", outward_in),
    ("full shuffle", shuffle_all),
)


def fingerprint(spans) -> np.ndarray:
    """Four length classes at the first edge, then four at the last."""
    first, last, interior = cells(spans)
    return np.concatenate([lift(first, interior), lift(last, interior)])


def apply_rule(spans, rule, rng):
    """Rearrange, then join short units, which is the order a scribe would work in."""
    out = []
    for s in spans:
        moved = rule(list(s), rng)
        joined = join(moved, JOIN_RATE, rng, forward=True)
        if len(joined) >= MIN_SPAN:
            out.append(joined)
    return out


def main() -> None:
    rng = random.Random(3301)
    raw = [
        register_spans(p, rng, join_rate=0.0)
        for p in (fetch(n) for n in REGISTERS)
        if p is not None
    ]
    body = body_spans()
    observed = fingerprint(body)
    first, last, interior = cells(body)
    body_se = []
    for edge in (first, last):
        a, b = np.array(edge, float), np.array(interior, float)
        for lo, hi, _ in CLASSES:
            pe = ((a >= lo) & (a <= hi)).mean()
            pi = ((b >= lo) & (b <= hi)).mean()
            body_se.append(math.sqrt(pe * (1 - pe) / len(a) + pi * (1 - pi) / len(b)))
    body_se = np.array(body_se)

    author = author_spans()
    print(f"{len(body)} body spans, {len(author)} author spans, {len(raw)} registers.")
    print("Eight numbers per rule: four length classes at the first edge, four at the")
    print(
        "last. chi2 is against the body, carrying its error and the register spread.\n"
    )
    print(f"{'rule':<28}{'chi2 first':>12}{'chi2 last':>12}{'chi2 both':>12}{'P':>10}")

    rows = []
    for name, rule in RULES:
        prints = np.array([fingerprint(apply_rule(s, rule, rng)) for s in raw])
        mean, spread = prints.mean(axis=0), prints.std(axis=0, ddof=1)
        se = np.hypot(body_se, spread)
        chi = ((observed - mean) / se) ** 2
        k = len(CLASSES)
        rows.append(
            (
                float(chi.sum()),
                name,
                float(chi[:k].sum()),
                float(chi[k:].sum()),
                float(stats.chi2.sf(chi.sum(), 2 * k)),
            )
        )
    for total, name, a, b, p in sorted(rows):
        print(f"{name:<28}{a:>12.1f}{b:>12.1f}{total:>12.1f}{p:>10.4f}")

    print("\nWhat each rule puts in the last slot, against how badly it fits there.\n")
    print(
        f"{'rule':<28}{'orig. final':>13}{'orig. first':>13}"
        f"{'interior':>10}{'chi2 last':>11}"
    )
    last_chi = {name: b for _, name, _, b, _ in rows}
    table = []
    for name, rule in RULES:
        stays = firsts = 0
        trials = range(3, 40)
        for n in trials:
            order = rule(list(range(n)), random.Random(11))
            stays += order[-1] == n - 1
            firsts += order[-1] == 0
        k = len(list(trials))
        table.append((last_chi[name], name, stays / k, firsts / k))
    for chi, name, stays, firsts in sorted(table):
        print(
            f"{name:<28}{stays:>13.2f}{firsts:>13.2f}"
            f"{1 - stays - firsts:>10.2f}{chi:>11.1f}"
        )
    keeps = np.array([s + f for _, _, s, f in table])
    chis = np.array([c for c, _, _, _ in table])
    print(
        f"\n  correlation between 'an edge word lands last' and the last-edge misfit:"
        f" {np.corrcoef(keeps, chis)[0, 1]:+.2f}"
    )


if __name__ == "__main__":
    main()
