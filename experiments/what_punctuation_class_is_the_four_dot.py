# ABOUTME: Compares the four-dot's before/after block profile against every English
# ABOUTME: punctuation class, not just the sentence end, to ask what level of mark it is.
"""Every reference used so far is a sentence end. English has other marks.

`sentences-do-not-end-long.md` and everything built on it compare the block before a ④
against the block before a period in ten registers, and find -0.17 +- 0.21 where English
gives +1.19 +- 0.28. The conclusion drawn is that ④ does not end a sentence. That is
right, and it leaves open which mark it *does* behave like, because the period is the only
reference that has ever been measured.

There is a second fact the sentence-end reading has never accommodated. The block
**after** a ④ is short-elevated exactly as an English sentence-initial word is: its share
of two-rune blocks is 0.224 +- 0.029 against the body's own 0.154 +- 0.007, a 1.46x lift
at 2.36 sigma (`titles_are_just_sentence_initial.py`). So ④ is not placed at random: the
text around it is structured on one side and not the other.

A mark whose following word runs short and whose preceding word does not run long is not a
terminator. It is what a comma is: English puts a function word after a comma -- and, but,
which, the -- while the word before it is an ordinary clause-internal word rather than the
heavy word that closes a sentence.

## What is measured

For each register, every word boundary is tagged with the punctuation that follows it.
Four classes are read separately -- sentence end, comma, colon or semicolon, and dash --
each giving the mean block length before and after, and the two-rune share after. The
body's ④ is held against all four.

Joining is applied forward along the stream at q = 0.40 as elsewhere, with one rule: a
unit carrying punctuation is never merged forward, since merging it would destroy the mark
being measured. That is the same convention the sentence-level reference already uses,
extended to the other marks.

    python what_punctuation_class_is_the_four_dot.py
"""

from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import IDX_ENG, to_runeglish  # noqa: E402
from do_the_marks_bound_the_titles import BODY, MASTER, chunk_words  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402

JOIN_RATE = 0.40
THRESHOLD = 2
CLASSES = (
    ("sentence end", ".!?"),
    ("comma", ","),
    ("colon or semicolon", ":;"),
    ("dash", "-—"),
)
TOKEN = re.compile(r"[A-Za-z']+|[.!?,:;—-]")


def tagged_stream(path) -> list[tuple[int, str]]:
    """(block length in runes, the punctuation that closes it) for a whole register."""
    text = path.read_text(encoding="utf-8", errors="replace")
    trim = len(text) // 10
    out: list[tuple[int, str]] = []
    pending = None
    for token in TOKEN.findall(text[trim : len(text) - trim]):
        if token[0].isalpha():
            if pending is not None:
                out.append((pending, ""))
            pending = len([c for c in to_runeglish(token.upper()) if c in IDX_ENG])
        elif pending:
            out.append((pending, token))
            pending = None
    if pending:
        out.append((pending, ""))
    return [(n, m) for n, m in out if n]


def join_stream(stream, rng, q=JOIN_RATE, threshold=THRESHOLD):
    """Merge an unmarked short unit into the one after it; a marked unit is left alone."""
    out = list(stream)
    i = 0
    while i < len(out) - 1:
        n, mark = out[i]
        if not mark and n <= threshold and rng.random() < q:
            out[i + 1] = (out[i + 1][0] + n, out[i + 1][1])
            out.pop(i)
            continue
        i += 1
    return out


def cells(stream, marks):
    """(before the mark, after it, everywhere else)."""
    before, after, interior = [], [], []
    for i, (n, mark) in enumerate(stream):
        if mark and mark in marks:
            before.append(n)
            if i + 1 < len(stream):
                after.append(stream[i + 1][0])
        elif not mark:
            interior.append(n)
    return before, after, interior


def body_cells(glyph="④"):
    chunks = {i: chunk_words(c) for i, c in enumerate(MASTER.read_text().split("%"))}
    stream = [(n, sep) for i in BODY for n, sep in chunks.get(i, [])]
    before, after, interior = [], [], []
    for i, (n, sep) in enumerate(stream):
        if sep == glyph:
            before.append(n)
            if i + 1 < len(stream):
                after.append(stream[i + 1][0])
        elif sep in {"①", "-"}:
            interior.append(n)
    return before, after, interior


def gap(values, interior):
    a, b = np.array(values, float), np.array(interior, float)
    se = math.hypot(
        a.std(ddof=1) / math.sqrt(len(a)), b.std(ddof=1) / math.sqrt(len(b))
    )
    return float(a.mean() - b.mean()), se


def short_lift(values, interior):
    a, b = np.array(values, float), np.array(interior, float)
    pa, pb = (a == 2).mean(), (b == 2).mean()
    se = math.sqrt(pa * (1 - pa) / len(a) + pb * (1 - pb) / len(b))
    return float(pa - pb), se


def main() -> None:
    rng = random.Random(3301)
    streams = [
        join_stream(tagged_stream(p), rng)
        for p in (fetch(n) for n in REGISTERS)
        if p is not None
    ]
    print(f"{len(streams)} registers, {sum(len(s) for s in streams):,} blocks.\n")
    print(
        f"{'English mark':<22}{'count':>9}{'before it':>16}{'after it':>16}"
        f"{'2-rune lift after':>20}"
    )
    reference = {}
    for label, marks in CLASSES:
        befores, afters, shorts, counts = [], [], [], 0
        for s in streams:
            b, a, interior = cells(s, marks)
            if len(b) < 50:
                continue
            counts += len(b)
            befores.append(gap(b, interior)[0])
            afters.append(gap(a, interior)[0])
            shorts.append(short_lift(a, interior)[0])
        if not befores:
            continue
        reference[label] = (
            (np.mean(befores), np.std(befores, ddof=1)),
            (np.mean(afters), np.std(afters, ddof=1)),
            (np.mean(shorts), np.std(shorts, ddof=1)),
        )
        b, a, s = reference[label]
        print(
            f"{label:<22}{counts:>9,}"
            f"{f'{b[0]:+.2f} +- {b[1]:.2f}':>16}{f'{a[0]:+.2f} +- {a[1]:.2f}':>16}"
            f"{f'{s[0]:+.3f} +- {s[1]:.3f}':>20}"
        )

    before, after, interior = body_cells()
    gb, sb = gap(before, interior)
    ga, sa = gap(after, interior)
    gs, ss = short_lift(after, interior)
    print(
        f"\n{'the body, four-dot':<22}{len(before):>9,}"
        f"{f'{gb:+.2f} +- {sb:.2f}':>16}{f'{ga:+.2f} +- {sa:.2f}':>16}"
        f"{f'{gs:+.3f} +- {ss:.3f}':>20}"
    )

    print("\nHow far the body sits from each English mark, in sigma.\n")
    print(
        f"{'English mark':<22}{'before':>10}{'after':>10}{'2-rune':>10}{'chi2 (3 df)':>14}"
    )
    for label, (b, a, s) in reference.items():
        z = (
            (gb - b[0]) / math.hypot(sb, b[1]),
            (ga - a[0]) / math.hypot(sa, a[1]),
            (gs - s[0]) / math.hypot(ss, s[1]),
        )
        print(
            f"{label:<22}{z[0]:>+10.2f}{z[1]:>+10.2f}{z[2]:>+10.2f}"
            f"{sum(x * x for x in z):>14.1f}"
        )


if __name__ == "__main__":
    main()
