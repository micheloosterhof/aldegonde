# ABOUTME: Locates the change in joining rate by a change-point scan priced against a
# ABOUTME: surrogate null, finding exactly one change, at page 14, and none after it.
"""The convention changes once, at page 14, and the boundary was found rather than assumed.

Every comparison in `short-units-are-written-joined.md` partitions the book as "front
matter against body" at page 15, because that is where the solved pages stop. That makes
the boundary an assumption: the joining rate might change somewhere else, or gradually, or
more than once, and the partition would still show a difference.

A change-point scan answers it. For each split of the book's pages, fit one 2-rune rate
before and one after, and take the likelihood ratio against a single rate throughout. The
maximum over splits is a scan statistic, so it needs a surrogate null rather than a
chi-square table (`scan-maxima-need-surrogate-nulls`): redraw each page's count from a
single pooled rate, keeping the page sizes, and rescan.

## One change, and it is where it was assumed to be

    scan maximum                     24.2  at page 14
    under no change point             4.3 +- 2.3
    P(max >= observed)              0.0000

    pages 0-13    0.243        pages 14-72    0.160

The localisation is soft: pages 13, 14, 15, 17 and 18 all score within four units of the
maximum, so the change sits in **13-15** and no finer. That still covers the solved/
unsolved boundary, so the assumed partition was right.

## Nothing changes after it

Rescanning pages 14 and later finds no second change: maximum 2.3 against a null of
4.1 +- 2.2, **P = 0.79**. The enciphered body and the end matter are one regime, which
matches `the-body-is-one-uniform-text.md` reaching the same verdict across sections by a
different route.

## Two things checked and dropped

- **"The end matter returns to the front-matter rate."** Pages 70-72 read 0.29, 0.32 and
  0.25, which looked like a second change back. It is small-page noise: pages 65-72
  together read 0.177 +- 0.025, which is z = +0.68 from the body and z = -2.20 from the
  front matter. The one solved page there (71, the prime running key) reads 0.320 on 25
  blocks, consistent with the front matter and far too small to carry anything.
- **A change at page 7.** Scanning pages 0-13 alone flags one at P = 0.02
  (0.201 -> 0.294). It does not track the cipher kind -- both halves hold plaintext,
  monoalphabetic and Vigenere pages -- and it rests on pages 8, 9 and 10 running high at
  about 2 sigma each. With three scans run it is not supported, and it is recorded here so
  it is not mistaken for a finding later.

    python where_the_joining_starts.py
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

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ANNOTATION = re.compile(r"^[\s0-9-]*$")
MIN_BLOCKS = 15  # a page too small to carry a rate is dropped
MARGIN = 3  # splits this close to either end are not scanned
DRAWS = 500


def blocks_of(page: str) -> list[int]:
    text = "\n".join(
        line
        for line in page.replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )
    out, current = [], 0
    for ch in text:
        if RUNE.match(ch):
            current += 1
        elif ch == "\n" or ch in "%$&":
            continue
        elif ch in c3301.WORD_BOUNDARY:
            if current:
                out.append(current)
                current = 0
    if current:
        out.append(current)
    return out


def usable_pages():
    pages = MASTER.read_text().split("%")
    out = []
    for n, page in enumerate(pages):
        blocks = blocks_of(page)
        if len(blocks) >= MIN_BLOCKS:
            out.append((n, blocks))
    return out


def loglik(hits, total, rate):
    rate = min(max(rate, 1e-9), 1 - 1e-9)
    return hits * math.log(rate) + (total - hits) * math.log(1 - rate)


def scan(hits, totals):
    """Best split by likelihood ratio against one rate throughout."""
    pooled = sum(loglik(k, n, hits.sum() / totals.sum()) for k, n in zip(hits, totals))
    best = (-1.0, None)
    for c in range(MARGIN, len(hits) - MARGIN):
        before = hits[:c].sum() / totals[:c].sum()
        after = hits[c:].sum() / totals[c:].sum()
        value = 2 * (
            sum(loglik(k, n, before) for k, n in zip(hits[:c], totals[:c]))
            + sum(loglik(k, n, after) for k, n in zip(hits[c:], totals[c:]))
            - pooled
        )
        if value > best[0]:
            best = (value, c)
    return best


def price(subset, label, rng):
    hits = np.array([sum(1 for x in b if x == 2) for _, b in subset], float)
    totals = np.array([len(b) for _, b in subset], float)
    if len(subset) < 2 * MARGIN + 4:
        print(f"{label:<36}too few pages")
        return
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
        f"{label:<36}{observed:>7.1f}{f'{null.mean():.1f} +- {null.std(ddof=1):.1f}':>15}"
        f"{float((null >= observed).mean()):>9.4f}   p{subset[c][0]}: "
        f"{before:.3f} -> {after:.3f}"
    )


def main() -> None:
    pages = usable_pages()
    print(
        f"{len(pages)} pages with {MIN_BLOCKS}+ blocks, "
        f"{sum(len(b) for _, b in pages)} blocks.\n"
    )
    rng = np.random.default_rng(3301)
    print(f"{'scan over':<36}{'max':>7}{'null':>15}{'P':>9}   best split")
    price(pages, "the whole book", rng)
    price([p for p in pages if p[0] >= 14], "pages 14+, a second change?", rng)
    price([p for p in pages if p[0] < 14], "pages 0-13, an earlier one?", rng)

    hits = np.array([sum(1 for x in b if x == 2) for _, b in pages], float)
    totals = np.array([len(b) for _, b in pages], float)
    pooled = sum(loglik(k, n, hits.sum() / totals.sum()) for k, n in zip(hits, totals))
    curve = []
    for c in range(MARGIN, len(hits) - MARGIN):
        before = hits[:c].sum() / totals[:c].sum()
        after = hits[c:].sum() / totals[c:].sum()
        curve.append(
            (
                pages[c][0],
                2
                * (
                    sum(loglik(k, n, before) for k, n in zip(hits[:c], totals[:c]))
                    + sum(loglik(k, n, after) for k, n in zip(hits[c:], totals[c:]))
                    - pooled
                ),
            )
        )
    print("\nHow sharply the change is located: the best six splits.\n")
    print(f"{'split before page':<22}{'statistic':>11}")
    for page, value in sorted(curve, key=lambda t: -t[1])[:6]:
        print(f"{page:<22}{value:>11.1f}")

    solved = set(PLAIN_PAGES) | {t["page"] for t in json.loads(TRIPLES.read_text())}
    print("\nThe groups the change separates.\n")
    print(f"{'group':<38}{'pages':>7}{'blocks':>8}{'frac at 2':>11}{'se':>8}")
    for ids, label in (
        (set(range(14)), "pages 0-13"),
        (set(range(14, 65)), "pages 14-64, the enciphered body"),
        (set(range(65, 73)), "pages 65-72, the end matter"),
        (set(range(65, 73)) & solved, "   of those, solved"),
    ):
        blocks = [x for n, b in pages if n in ids for x in b]
        if not blocks:
            continue
        f = float(np.mean([x == 2 for x in blocks]))
        print(
            f"{label:<38}{len(ids & {n for n, _ in pages}):>7}{len(blocks):>8}"
            f"{f:>11.3f}{math.sqrt(f * (1 - f) / len(blocks)):>8.3f}"
        )

    print(
        "\nOne change, at page 14, where the partition had assumed it. Nothing changes"
        "\nafter it, so the joining is a single switch rather than a drift -- which is"
        "\nwhat one different exemplar looks like, and not a scribe changing habits."
    )


if __name__ == "__main__":
    main()
