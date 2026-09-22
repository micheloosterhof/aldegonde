# ABOUTME: Tests whether the short-unit joining, applied across span boundaries rather than
# ABOUTME: within them, reproduces the body's flat final edge without any transposition.
"""Before believing a transposition, try to kill it with the joining already on record.

`the-rearrangement-is-not-a-simple-rule.md` excludes identity word order at P = 2e-6 on
the span-final length profile, and reads that as evidence the words were rearranged. That
inference has a gap. Every reference arm in that test joins short units **per sentence**,
so a sentence's final word can never merge into anything: `join` looks one place forward
and the span ends.

The body's scribe had no such rule. If the joining ran along the **stream**, a short word
at the end of a span would merge with the first word of the next one, and the mark would
have to fall on one side of the merged unit or the other. Either way the span's final
block is no longer the sentence's final word -- it is displaced by one, with no
rearrangement anywhere. That is a strictly simpler explanation than a transposition and it
has never been tested.

Two further knobs are swept at the same time, because they are equally unconstrained:

- **direction** -- a short unit may merge into the word that follows it or the one before;
- **threshold** -- units of two runes or less is the fitted rule, but three is as natural
  a convention and the fit was made on the histogram, not the edges.

## What each arm has to reproduce

The body's eight-number edge fingerprint: the share of blocks in four length classes at
the first block of a span and at the last, each minus that span's own interior. An arm is
scored by chi-squared against it, carrying the body's sampling error and the spread over
the ten registers.

The transposition arm -- shuffle within each span, then join per sentence -- is included
so the two explanations are read on the same scale rather than one at a time.

## Result: no joining convention can do it, and the reason is structural

Twelve arms, sweeping direction, threshold, whether a merge may cross a span boundary and
which side of a merged unit the mark falls on. **Every one fails at P <= 0.001.**

| arm | chi2 first | chi2 last | chi2 both | P |
|---|---|---|---|---|
| **shuffle within the span, then join** | 5.8 | **3.9** | **9.7** | **0.29** |
| join within the span, forward, <=3 | 4.9 | 21.3 | 26.2 | 0.0010 |
| join across the boundary, forward, <=3, mark before | 4.9 | 29.6 | 34.6 | 2e-5 |
| join within the span, forward, <=2 (the reference) | 6.7 | 31.7 | 38.5 | 6e-6 |
| join within the span, backward, <=2 | 10.9 | 29.8 | 40.7 | 2e-6 |
| join across the boundary, forward, <=2, mark before | 6.2 | 39.1 | 45.2 | 3e-7 |
| join across the boundary, forward, <=2, mark after | 6.9 | 43.0 | 49.9 | 4e-8 |
| join across the boundary, backward, <=3, mark before | 8.2 | 61.8 | 70.0 | 5e-12 |

Best joining-only arm 26.2 against the transposition arm's 9.7: a likelihood ratio of
about **3,800 to 1** on eight cells.

**Crossing the boundary makes the fit worse, not better.** That was the whole point of the
test and it comes out the wrong way round, which turns out to be structural rather than
accidental.

The body's span-final blocks are **enriched** in short words and depleted in long ones
relative to the span interior: +0.031 and +0.023 in the 1-2 and 3-4 classes, -0.019 and
-0.036 in 5-6 and 7+. Joining *removes* short blocks. Every convention for it can only
push the final edge further from short-enrichment, which is the opposite of what is
needed. So this is not a matter of finding the right rate or direction:

    no joining rule of any kind can flatten the final edge,
    because the deficit is in the long classes and joining acts on the short ones.

That closes the simplest alternative to a rearrangement. What put those blocks at the end
of a span put ordinary interior words there -- which is what the shuffle arm supplies, at
chi2 3.9 on the last edge.

## A consistency check worth noting

The arm "join within the span, forward, <=2" is the reference convention, and it scores
38.5 here against 38.5 for identity in `which_structured_permutation.py`. The two scripts
share no code beyond the fingerprint and agree exactly.

    python can_joining_alone_flatten_the_edge.py
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
from the_gap_depends_on_span_length import body_spans  # noqa: E402
from where_in_the_distribution_is_the_anomaly import CLASSES, cells, lift  # noqa: E402

JOIN_RATE = 0.40
MIN_SPAN = 3


def join_within(spans, q, threshold, rng, *, forward):
    """The reference convention: each span joined on its own, so its edges are protected."""
    out = []
    for s in spans:
        cur, i = list(s), 0
        while i < len(cur):
            j = i + 1 if forward else i - 1
            if cur[i] <= threshold and rng.random() < q and 0 <= j < len(cur):
                cur[j] += cur[i]
                cur.pop(i)
                continue
            i += 1
        if len(cur) >= MIN_SPAN:
            out.append(cur)
    return out


def join_across(spans, q, threshold, rng, *, forward, mark_follows):
    """Joining along the whole stream, so a merge may cross a span boundary.

    `mark_follows` decides which side of a merged unit the mark lands on: True keeps the
    mark after the merged block, so the block belongs to the earlier span; False puts it
    before, so the block opens the later span.
    """
    flat = [(x, w) for w, s in enumerate(spans) for x in s]
    i = 0
    while i < len(flat):
        j = i + 1 if forward else i - 1
        if flat[i][0] <= threshold and rng.random() < q and 0 <= j < len(flat):
            length, span = flat[j]
            keep = flat[i][1] if mark_follows else span
            flat[j] = (length + flat[i][0], keep if j > i else span)
            flat.pop(i)
            continue
        i += 1
    out, cur, at = [], [], None
    for length, span in flat:
        if span != at and cur:
            out.append(cur)
            cur = []
        at, _ = span, cur.append(length)
    if cur:
        out.append(cur)
    return [s for s in out if len(s) >= MIN_SPAN]


def shuffle_within(spans, rng):
    out = []
    for s in spans:
        s = list(s)
        rng.shuffle(s)
        out.append(s)
    return out


def fingerprint(spans) -> np.ndarray:
    first, last, interior = cells(spans)
    return np.concatenate([lift(first, interior), lift(last, interior)])


def body_fingerprint():
    body = body_spans()
    first, last, interior = cells(body)
    se = []
    for edge in (first, last):
        a, b = np.array(edge, float), np.array(interior, float)
        for lo, hi, _ in CLASSES:
            pe = ((a >= lo) & (a <= hi)).mean()
            pi = ((b >= lo) & (b <= hi)).mean()
            se.append(math.sqrt(pe * (1 - pe) / len(a) + pi * (1 - pi) / len(b)))
    return fingerprint(body), np.array(se)


def score(raw, build, observed, body_se, rng):
    prints = np.array([fingerprint(build(s, rng)) for s in raw])
    mean, spread = prints.mean(axis=0), prints.std(axis=0, ddof=1)
    chi = ((observed - mean) / np.hypot(body_se, spread)) ** 2
    k = len(CLASSES)
    return float(chi[:k].sum()), float(chi[k:].sum()), float(chi.sum())


def main() -> None:
    rng = random.Random(3301)
    raw = [
        register_spans(p, rng, join_rate=0.0)
        for p in (fetch(n) for n in REGISTERS)
        if p is not None
    ]
    observed, body_se = body_fingerprint()
    print(f"{len(raw)} registers, {sum(len(s) for s in raw):,} sentences.")
    print("Every arm is scored against the body's eight-number edge fingerprint.\n")
    print(f"{'arm':<46}{'chi2 first':>11}{'chi2 last':>11}{'chi2 both':>11}{'P':>9}")

    arms = []
    for threshold in (2, 3):
        for forward in (True, False):
            way = "forward" if forward else "backward"
            arms.append(
                (
                    f"join within the span, {way}, <={threshold}",
                    lambda s, r, t=threshold, f=forward: join_within(
                        s, JOIN_RATE, t, r, forward=f
                    ),
                )
            )
            for mark_follows in (True, False):
                side = "mark after" if mark_follows else "mark before"
                arms.append(
                    (
                        f"join across the boundary, {way}, <={threshold}, {side}",
                        lambda s, r, t=threshold, f=forward, m=mark_follows: join_across(
                            s, JOIN_RATE, t, r, forward=f, mark_follows=m
                        ),
                    )
                )
    arms.append(
        (
            "SHUFFLE within the span, then join, forward, <=2",
            lambda s, r: join_within(shuffle_within(s, r), JOIN_RATE, 2, r, forward=True),
        )
    )

    rows = []
    for label, build in arms:
        a, b, total = score(raw, build, observed, body_se, rng)
        rows.append((total, label, a, b, stats.chi2.sf(total, 2 * len(CLASSES))))
    for total, label, a, b, p in sorted(rows):
        print(f"{label:<46}{a:>11.1f}{b:>11.1f}{total:>11.1f}{p:>9.4f}")

    best_join = min(t for t, label, _, _, _ in rows if "SHUFFLE" not in label)
    shuffled = next(t for t, label, _, _, _ in rows if "SHUFFLE" in label)
    print(
        f"\nBest joining-only arm: {best_join:.1f}.   Transposition arm: {shuffled:.1f}."
        f"\nLikelihood ratio between them, on eight cells: "
        f"{math.exp((best_join - shuffled) / 2):.1f} to 1 for the better."
    )


if __name__ == "__main__":
    main()
