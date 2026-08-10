# ABOUTME: Censuses every dot-cluster mark in the LP page scans by dot count,
# ABOUTME: testing whether the transcription's two mark classes are enough.
"""How many kinds of dot mark does the book actually use?

The transcription records two: `-` for a word separator and `.` for a sentence
mark. Manual review of the scan-vs-transcription discrepancies found that is
not the whole inventory — a mark transcribed as `-` on page 5 is a triple dot,
and page 7 carries a thirteen-dot cluster the transcription omits entirely.

That is the same failure the apostrophes and quotation marks had
(`contraction-cribs.md`): the glyph inventory was assumed rather than measured.
So this measures it. Every small ink blob in the text block is found, blobs are
grouped into clusters by proximity, and the clusters are histogrammed by dot
count.

If the book only used a separator and a sentence mark, the histogram should be
bimodal at 1 and one other value. Anything else is a mark class the
transcription is collapsing or dropping, and every downstream statistic that
counts '.' marks — the sentence-mark semantics work, mark density, sentence
lengths — is measured on the wrong inventory.

The classes are not an artifact of LINK. Varying it from 45 to 110 px over the
manually confirmed pages leaves the 13-dot count invariant at 9 and the 4-dot
count at 13-15; only the 1-dot count falls, as adjacent word separators start
being merged, which is what fixes LINK near 45.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict

import numpy as np
from PIL import Image
from scipy import ndimage

from aldegonde import c3301
from experiments.locate_marks import CORPUS, IMAGE_DIR, TEXT_BLOCK

RUNE = re.compile(r"[ᚠ-᛿]")
PAGES = range(58)
DOT_MAX = 16  # a single dot is about 10px square
LINK = 45  # dots this close belong to one cluster
INK = 128


def dots(page: int) -> list[tuple[int, int]]:
    """Centres of every dot-sized blob inside the text block."""
    ink = np.array(Image.open(IMAGE_DIR / f"{page}.jpg").convert("L")) < INK
    labels, _ = ndimage.label(ink, structure=np.ones((3, 3)))
    out = []
    for ys, xs in ndimage.find_objects(labels):
        h, w = ys.stop - ys.start, xs.stop - xs.start
        if h <= DOT_MAX and w <= DOT_MAX and TEXT_BLOCK[0] <= xs.start <= TEXT_BLOCK[1]:
            out.append((ys.start + h // 2, xs.start + w // 2))
    return out


def cluster(points: list[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    """Group dots by transitive proximity."""
    parent = list(range(len(points)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, a in enumerate(points):
        for j in range(i + 1, len(points)):
            b = points[j]
            if abs(a[0] - b[0]) <= LINK and abs(a[1] - b[1]) <= LINK:
                parent[find(i)] = find(j)
    groups: dict[int, list] = defaultdict(list)
    for i, p in enumerate(points):
        groups[find(i)].append(p)
    return list(groups.values())


def main() -> None:
    sizes: Counter[int] = Counter()
    big: list[tuple[int, int, int, int]] = []

    for page in PAGES:
        for group in cluster(dots(page)):
            sizes[len(group)] += 1
            if len(group) >= 3:
                ys = [p[0] for p in group]
                xs = [p[1] for p in group]
                big.append((len(group), page, min(ys), min(xs)))

    total = sum(sizes.values())
    print(f"dot clusters in the text block of all {len(PAGES)} pages: {total}\n")
    print(f"{'dots':>6}{'clusters':>10}{'share':>9}")
    for n in sorted(sizes):
        print(f"{n:>6}{sizes[n]:>10}{sizes[n] / total:>9.2%}")

    txt = CORPUS.read_text()
    word = sum(1 for ch in txt if ch in c3301.WORD_MARKS)
    cluster_marks = sum(1 for ch in txt if ch in c3301.CLUSTER_MARKS)
    print(
        f"\ntranscription records {word} word marks and {cluster_marks} clusters "
        f"= {word + cluster_marks} marks"
    )
    print(f"scan finds {total} clusters, of which {sizes[1]} are single dots")

    print("\nclusters of 3+ dots, by size")
    for size in sorted({b[0] for b in big}):
        members = [b for b in big if b[0] == size]
        where = ", ".join(f"p{b[1]}" for b in members[:8])
        more = f" +{len(members) - 8} more" if len(members) > 8 else ""
        print(f"   {size:>3} dots: {len(members):>4}  {where}{more}")


if __name__ == "__main__":
    main()
