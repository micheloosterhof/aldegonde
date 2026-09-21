# ABOUTME: Maps Liber Primus page images to transcription chunks by matching word-length
# ABOUTME: sequences, so image-side findings (rubrication, glyphs) can be located in the text.
"""Which transcription chunk is each page image?

Image-side work -- rubrication, the quote ticks, glyph geometry -- produces results
indexed by page number. Text-side work is indexed by the master transcription's
`%`-chunks. Those are not the same: the master holds 72 rune-bearing chunks against 58
page images, so `rubrication-crib-candidates.md` could not say which of its rows fall
on solved pages except by assuming a correspondence.

The two can be matched without reading a single rune. A page image shows its word
structure directly -- runes are ink blobs 100-125 px tall, separator dots are 6-14 px --
so the sequence of word LENGTHS can be read off the image, and word-length sequences are
distinctive enough to identify a chunk.

Blob detection is imperfect: runes sometimes split into components and touching pairs
sometimes merge, so image word counts miss transcription counts by -11% to +42%. The
match therefore uses longest common subsequence, which tolerates insertions and
deletions, normalised by the shorter sequence.

    python page_alignment.py
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from apostrophe_census import IMAGE_DIR, TEXT_BLOCK_X, components  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
LINE_GAP = 60
RUNE_H = (100, 125)
DOT = (6, 14)


def image_word_lengths(page: int) -> list[int]:
    items = []
    for y, x, h, w in components(IMAGE_DIR / f"{page}.jpg"):
        if not TEXT_BLOCK_X[0] <= x <= TEXT_BLOCK_X[1]:
            continue
        if RUNE_H[0] <= h <= RUNE_H[1]:
            items.append((y, x, "R"))
        elif DOT[0] <= h <= DOT[1] and DOT[0] <= w <= DOT[1]:
            items.append((y, x, "D"))
    if not items:
        return []
    items.sort()
    lines, cur = [], [items[0]]
    for it in items[1:]:
        if it[0] - cur[-1][0] <= LINE_GAP:
            cur.append(it)
        else:
            lines.append(cur)
            cur = [it]
    lines.append(cur)
    seq = [k for ln in lines for _y, _x, k in sorted(ln, key=lambda t: t[1])]
    out, run = [], 0
    for k in seq:
        if k == "R":
            run += 1
        elif run:
            out.append(run)
            run = 0
    if run:
        out.append(run)
    return out


def chunk_word_lengths(chunk: str) -> list[int]:
    out, run = [], 0
    for ch in chunk:
        if RUNE.match(ch):
            run += 1
        elif ch in "/\n":
            continue
        elif run:
            out.append(run)
            run = 0
    if run:
        out.append(run)
    return out


def lcs(a: list[int], b: list[int]) -> int:
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(cur[j], prev[j + 1]))
        prev = cur
    return prev[-1]


def main() -> None:
    # index by the master's own %-position, which is what every other consumer of
    # rubricated_titles.json and solved_page_triples.json uses. Filtering the runeless
    # chunk out of the list instead renumbers everything after it by one.
    raw = MASTER.read_text().split("%")
    tw = {i: chunk_word_lengths(c) for i, c in enumerate(raw) if RUNE.search(c)}
    rows, offsets = [], []
    print(f"{'page':>5}{'words':>7}{'chunk':>7}{'score':>7}{'2nd':>7}{'offset':>8}")
    for page in range(58):
        iw = image_word_lengths(page)
        if len(iw) < 8:
            rows.append({"page": page, "chunk": None, "why": "too few words"})
            print(f"{page:>5}{len(iw):>7}{'-':>7}{'-':>7}{'-':>7}{'-':>8}")
            continue
        scored = sorted(
            ((lcs(iw, t) / min(len(iw), len(t)), i) for i, t in tw.items() if t),
            reverse=True,
        )
        best, idx = scored[0]
        second = scored[1][0]
        ok = best > 0.85 and best - second > 0.05
        rows.append(
            {
                "page": page,
                "chunk": idx if ok else None,
                "score": round(best, 3),
                "runner_up": round(second, 3),
            }
        )
        if ok:
            offsets.append(idx - page)
        print(
            f"{page:>5}{len(iw):>7}{idx:>7}{best:>7.2f}{second:>7.2f}"
            f"{(idx - page) if ok else '-':>8}"
        )
    (ROOT / "experiments" / "page_alignment.json").write_text(
        json.dumps(rows, indent=1)
    )
    print(f"\nconfident: {sum(1 for r in rows if r['chunk'] is not None)}/58")
    print(f"offsets: {collections.Counter(offsets).most_common()}")


if __name__ == "__main__":
    main()
