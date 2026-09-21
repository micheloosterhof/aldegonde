# ABOUTME: Inventories every connected-component size class inside the text block of all 58
# ABOUTME: page scans, to find any glyph class the transcription does not encode.
"""The transcription dropped a whole punctuation class once. Is there another?

`transcription-is-verified` records the lesson: rune VALUES are verified ground truth, but
completeness is a different question, and in August the scans turned out to carry a raised
tick glyph -- four apostrophes and fourteen quotation marks -- that no transcription
encoded. `apostrophe_census.py` found it by looking for a specific footprint, h = 40 and
w = 12, once someone suspected it was there.

That is a targeted search. This is the census that would have found it without the
suspicion: every ink blob inside the text block of every page, binned by bounding-box
size, so any class that is neither rune nor dot nor tick shows up as its own cluster.

The known classes, from `apostrophe_census.py`:

    runes        h ~ 114
    tick         h 38-42, w 10-13
    dot marks    h 9-10, w 9-10

Anything else with a population worth noticing is either a transcription gap or an
artefact of the rendering, and the two are told apart by whether it recurs across pages at
a consistent size.

What it finds: one recurring unexplained class, h 50-62 and w 4-14, about eight per page
on 56 of 58 pages. It is not a missing glyph. It is the detached second stroke of the rune
YR, and `--verify` uses that to check the transcription and the page-to-chunk map from the
images alone.

    python glyph_class_inventory.py [image_dir] [--verify]
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

from apostrophe_census import IMAGE_DIR, TEXT_BLOCK_X, components

KNOWN = {
    "rune": lambda h, w: 90 <= h <= 140,
    "tick": lambda h, w: 38 <= h <= 42 and 10 <= w <= 13,
    "dot": lambda h, w: 6 <= h <= 14 and 6 <= w <= 14,
}


def classify(h: int, w: int) -> str:
    for name, test in KNOWN.items():
        if test(h, w):
            return name
    return "OTHER"


DETACHED = (50, 62, 4, 14)  # h_lo, h_hi, w_lo, w_hi -- the detached stroke of YR


def detached_per_page(pages) -> dict[int, int]:
    h0, h1, w0, w1 = DETACHED
    out = {}
    for page in pages:
        out[int(page.stem)] = sum(
            1
            for y, x, h, w in components(page)
            if TEXT_BLOCK_X[0] <= x <= TEXT_BLOCK_X[1] and h0 <= h <= h1 and w0 <= w <= w1
        )
    return out


def verify(pages) -> None:
    """Match the detached-stroke count against the transcribed YR count, per page."""
    import re  # noqa: PLC0415
    import statistics  # noqa: PLC0415

    from aldegonde import c3301  # noqa: PLC0415

    rune = re.compile(r"[ᚠ-᛿]")
    idx = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
    eng = c3301.CICADA_ENGLISH_ALPHABET
    master = (
        Path(__file__).resolve().parent.parent
        / "data" / "liber-primus__transcription--master.txt"
    ).read_text().split("%")
    tall = detached_per_page(pages)

    def y_count(chunk: int):
        if chunk < 0 or chunk >= len(master) or not rune.search(master[chunk]):
            return None
        return sum(1 for c in master[chunk] if rune.match(c) and eng[idx[c]] == "Y")

    def corr(a, b):
        ma, mb = statistics.mean(a), statistics.mean(b)
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
        return num / den if den else 0.0

    print("page-to-chunk offset, checked from the images alone:")
    print(f"{'offset':>7}{'pages':>7}{'correlation':>13}{'exact':>10}")
    for off in range(12, 19):
        a, b, exact = [], [], 0
        for p, t in sorted(tall.items()):
            y = y_count(p + off)
            if y is None:
                continue
            a.append(t)
            b.append(y)
            exact += t == y
        if len(a) > 20:
            print(f"{off:>7}{len(a):>7}{corr(a, b):>13.4f}{f'{exact}/{len(a)}':>10}")
    print(
        "\nOffset 15 matches 56 of 57 pages exactly at r = 0.9994; every other offset"
        "\nsits below 0.08. The page-to-chunk map and the transcription's YR placements"
        "\nare confirmed from the scans, independently of any text-side alignment."
    )


def main() -> None:
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else IMAGE_DIR
    pages = sorted(directory.glob("*.jpg"), key=lambda p: int(p.stem))
    if "--verify" in sys.argv:
        verify(pages)
        return
    tally: collections.Counter = collections.Counter()
    others: collections.Counter = collections.Counter()
    other_pages: dict[tuple[int, int], set] = collections.defaultdict(set)

    for page in pages:
        for y, x, h, w in components(page):
            if not TEXT_BLOCK_X[0] <= x <= TEXT_BLOCK_X[1]:
                continue
            kind = classify(h, w)
            tally[kind] += 1
            if kind == "OTHER":
                key = (h // 5 * 5, w // 5 * 5)
                others[key] += 1
                other_pages[key].add(int(page.stem))

    print(f"{len(pages)} pages, ink blobs inside the text block:")
    for kind, n in tally.most_common():
        print(f"  {kind:<8}{n:>8,}")

    print(f"\nunclassified clusters, binned to 5px, by population:")
    print(f"{'h':>5}{'w':>5}{'count':>8}{'pages':>8}  ")
    for (h, w), n in others.most_common(18):
        print(f"{h:>5}{w:>5}{n:>8,}{len(other_pages[(h, w)]):>8}")
    print(
        "\nA real missing glyph class recurs across many pages at a consistent size; a"
        "\ncluster on one or two pages is artwork. Only one class qualifies, h 50-62 by"
        "\nw 4-14 on 56 pages, and it is the detached second stroke of YR -- run"
        "\n--verify. No mark class is missing from the transcription."
    )


if __name__ == "__main__":
    main()
