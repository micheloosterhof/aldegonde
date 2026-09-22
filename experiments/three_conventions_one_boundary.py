# ABOUTME: Runs change-point scans on the joining rate, the mark rate and the line
# ABOUTME: measure, and finds all three switch at page 14-15 rather than drifting apart.
"""Three conventions change at one page, and one of them belongs to the scribe.

`where_the_joining_starts.py` located the joining change at page 14 by a change-point
scan rather than assuming page 15. The same scan applies to the other conventions that
differ between the front matter and the body, and the answer matters because they are
different *kinds* of thing:

- the **joining rate** and the **mark rate** are properties of the text being copied;
- the **line measure** is a property of the person ruling the page.

If they change at different places, the exemplar and the scribe changed separately. If
they change together, one production event covers both.

## They change together

Each scan is priced against a surrogate null for the maximum, not a chi-square table:
rates are redrawn from a single pooled value keeping page sizes, and the line measure is
nulled by permuting the page order.

| observable | max | null | P | best split |
|---|---|---|---|---|
| blocks of length 2 | 24.2 | 4.3 ± 2.3 | 0.0000 | p14: 0.243 → 0.160 |
| dot marks per rune | 35.0 | 4.1 ± 2.3 | 0.0000 | p15: 0.0311 → 0.0139 |
| runes per line | 884.5 | 112.8 ± 63.2 | 0.0000 | p15: 19.03 → 21.77 |

Three observables of two different kinds, all switching within one page of each other.

## The line measure is not the encipherment confound

`short-units-are-written-joined.md` records the trap: enciphered text has no word shapes
to break on, so a scribe fills to a measure where plaintext breaks at sentence ends, and
the raw front-against-body gap overstates any change of hand. Comparing like with like,
with paragraph-final lines dropped:

    plaintext front matter  18.59  ->  enciphered front matter 19.88   +1.29 +- 0.99  z +1.30
    enciphered front matter 19.88  ->  the body                21.80   +1.92 +- 0.35  z +5.53

**The confound itself is not significant** and the enciphered-against-enciphered change
is, at +9.7%. So the ruling really changes at page 15, and it is not the cipher doing it.

## What this supports

A single production break at page 14-15 covering the exemplar and the ruling together --
which is what `short-units-are-written-joined.md` reading 1 predicts, and is now carried
by three measurements instead of one. Pages 57-72 read 22.05 runes per line, still in the
body's regime, matching the absence of any second change point.

It does not identify what changed: a different hand, a different pen, a different page
format and a different sitting all produce this signature and the transcription cannot
separate them.

    python three_conventions_one_boundary.py
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import MASTER, PLAIN_PAGES, TRIPLES  # noqa: E402
from where_the_joining_starts import MARGIN, blocks_of, scan  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ANNOTATION = re.compile(r"^[\s0-9-]*$")
DOT_MARKS = ".④⑬③⑩"
MIN_RUNES = 80
DRAWS = 500


def page_rows():
    """Per page: dot marks, runes, line lengths and blocks."""
    pages = MASTER.read_text().split("%")
    out = []
    for n, page in enumerate(pages):
        lines = [
            len(RUNE.findall(line))
            for line in page.replace("/", "\n").split("\n")
            if not ANNOTATION.match(line)
        ]
        lines = [x for x in lines if x]
        if sum(lines) < MIN_RUNES or len(lines) < 4:
            continue
        out.append(
            {
                "page": n,
                "marks": sum(1 for c in page if c in DOT_MARKS),
                "runes": sum(lines),
                "lines": lines,
                "blocks": blocks_of(page),
            }
        )
    return out


def price_rate(hits, totals, ids, label, rng):
    hits, totals = np.array(hits, float), np.array(totals, float)
    observed, c = scan(hits, totals)
    rate = hits.sum() / totals.sum()
    null = np.array(
        [
            scan(rng.binomial(totals.astype(int), rate).astype(float), totals)[0]
            for _ in range(DRAWS)
        ]
    )
    before = hits[:c].sum() / totals[:c].sum()
    after = hits[c:].sum() / totals[c:].sum()
    print(
        f"{label:<26}{observed:>8.1f}{f'{null.mean():.1f} +- {null.std(ddof=1):.1f}':>17}"
        f"{float((null >= observed).mean()):>9.4f}   p{ids[c]}: {before:.4f} -> {after:.4f}"
    )


def gaussian_scan(values, weights):
    """Between-group sum of squares at the best split, for a continuous measure."""
    best = (-1.0, None)
    grand = (values * weights).sum() / weights.sum()
    total = (weights * (values - grand) ** 2).sum()
    for c in range(MARGIN, len(values) - MARGIN):
        m1 = (values[:c] * weights[:c]).sum() / weights[:c].sum()
        m2 = (values[c:] * weights[c:]).sum() / weights[c:].sum()
        within = (weights[:c] * (values[:c] - m1) ** 2).sum() + (
            weights[c:] * (values[c:] - m2) ** 2
        ).sum()
        if total - within > best[0]:
            best = (total - within, c)
    return best


def main() -> None:
    rows = page_rows()
    ids = [r["page"] for r in rows]
    rng = np.random.default_rng(3301)
    print(f"{len(rows)} pages carrying {MIN_RUNES}+ runes.\n")
    print(f"{'observable':<26}{'max':>8}{'null':>17}{'P':>9}   best split")
    price_rate(
        [sum(1 for x in r["blocks"] if x == 2) for r in rows],
        [len(r["blocks"]) for r in rows],
        ids,
        "blocks of length 2",
        rng,
    )
    price_rate(
        [r["marks"] for r in rows],
        [r["runes"] for r in rows],
        ids,
        "dot marks per rune",
        rng,
    )

    measure = np.array([np.mean(r["lines"]) for r in rows])
    weights = np.array([len(r["lines"]) for r in rows], float)
    observed, c = gaussian_scan(measure, weights)
    null = np.array(
        [
            gaussian_scan(measure[p], weights[p])[0]
            for p in (rng.permutation(len(measure)) for _ in range(DRAWS))
        ]
    )
    m1 = (measure[:c] * weights[:c]).sum() / weights[:c].sum()
    m2 = (measure[c:] * weights[c:]).sum() / weights[c:].sum()
    print(
        f"{'runes per line':<26}{observed:>8.1f}"
        f"{f'{null.mean():.1f} +- {null.std(ddof=1):.1f}':>17}"
        f"{float((null >= observed).mean()):>9.4f}   p{ids[c]}: {m1:.2f} -> {m2:.2f}"
    )

    print("\nIs the line-measure change just the encipherment? Compare like with like.")
    print("Paragraph-final lines are dropped: they are short whatever the measure.\n")
    pages = MASTER.read_text().split("%")
    triples = {t["page"]: t["cipher"] for t in json.loads(TRIPLES.read_text())}

    def lines_for(page_ids):
        out = []
        for n in page_ids:
            if n >= len(pages):
                continue
            v = [
                len(RUNE.findall(line))
                for line in pages[n].replace("/", "\n").split("\n")
                if not ANNOTATION.match(line)
            ]
            out += [x for x in v if x][:-1]
        return np.array(out, float)

    groups = {
        "front matter, plaintext": lines_for(PLAIN_PAGES),
        "front matter, enciphered": lines_for(list(triples)),
        "the body, pages 15-56": lines_for(range(15, 57)),
        "pages 57-72": lines_for(range(57, 73)),
    }
    print(f"{'group':<30}{'lines':>7}{'mean':>8}{'sd':>7}")
    for label, v in groups.items():
        print(f"{label:<30}{len(v):>7}{v.mean():>8.2f}{v.std(ddof=1):>7.2f}")

    def gap(a, b):
        d = b.mean() - a.mean()
        se = math.hypot(
            a.std(ddof=1) / math.sqrt(len(a)), b.std(ddof=1) / math.sqrt(len(b))
        )
        return d, se, d / se

    print()
    for label, a, b in (
        (
            "the confound: plaintext -> enciphered front",
            groups["front matter, plaintext"],
            groups["front matter, enciphered"],
        ),
        (
            "the test: enciphered front -> the body",
            groups["front matter, enciphered"],
            groups["the body, pages 15-56"],
        ),
    ):
        d, se, z = gap(a, b)
        print(f"  {label:<44}{d:+.2f} +- {se:.2f}   z = {z:+.2f}")

    print(
        "\nThe confound is not significant and the enciphered-against-enciphered change"
        "\nis, so the ruling changes at page 15 and the cipher is not what changes it."
        "\nThree observables of two kinds -- what was copied and how it was ruled -- all"
        "\nswitch within one page. That is one production break, not three drifts."
    )


if __name__ == "__main__":
    main()
