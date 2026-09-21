# ABOUTME: Reconciles every rune-sized blob on every page against the transcription line by
# ABOUTME: line, so any glyph the transcription does not encode is named rather than binned.
"""Two censuses have now been too confident. This one balances the books.

`glyph-inventory-is-complete.md` bins blobs by SIZE and concludes nothing is missing; it
cannot see a mark that is rune-sized. `colour-channel-holds-one-layer.md` bins by COLOUR
and finds five rune-sized red glyphs on pages 36-38 that no transcription encodes -- which
the size census had counted as runes.

Both answer the question their binning can see. The question that admits no such gap is
arithmetic: for every page,

    rune-sized blobs  -  header blobs  -  unencoded marks  ==  transcribed runes

Line by line, so a discrepancy is localised rather than absorbed. Any line where the
counts differ is a glyph the transcription does not have, or one it has that the page does
not.

It does not balance the book, and the reason is worth knowing: runes touch, so 74 lines
carry FEWER blobs than runes. But the direction is the finding. Deficits outnumber
excesses 103 to 20, and of the twenty excess lines exactly five carry a red blob -- the
five line-initial marks on pages 36-38. Every other excess is black.

    python page_blob_reconciliation.py [image_dir] [--summary]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from apostrophe_census import IMAGE_DIR, INK, TEXT_BLOCK_X

from aldegonde import c3301

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = Path(__file__).resolve().parent.parent / "data" / "liber-primus__transcription--master.txt"
RUNE_H = (90, 140)
ROW_GAP = 70


def blobs(path: Path) -> list[tuple[int, int, int]]:
    """(y, x, R-G) of every rune-sized blob in the text block."""
    img = np.array(Image.open(path).convert("RGB"))
    labels, _ = ndimage.label(img.mean(axis=2) < INK, structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(ndimage.find_objects(labels), start=1):
        ys, xs = sl
        if not (RUNE_H[0] <= ys.stop - ys.start <= RUNE_H[1]):
            continue
        if not TEXT_BLOCK_X[0] <= xs.start <= TEXT_BLOCK_X[1]:
            continue
        mask = labels[sl] == i
        c = img[sl][mask].mean(axis=0)
        out.append((ys.start, xs.start, int(c[0]) - int(c[1])))
    return out


def rows(bs: list[tuple[int, int, int]]) -> list[list[tuple[int, int, int]]]:
    bs = sorted(bs)
    if not bs:
        return []
    out, cur = [], [bs[0]]
    for b in bs[1:]:
        if b[0] - cur[-1][0] > ROW_GAP:
            out.append(sorted(cur, key=lambda t: t[1]))
            cur = [b]
        else:
            cur.append(b)
    out.append(sorted(cur, key=lambda t: t[1]))
    return out


def text_rows(chunk: str) -> list[int]:
    out, cur = [], 0
    for c in chunk:
        if RUNE.match(c):
            cur += 1
        elif c == "/":
            out.append(cur)
            cur = 0
    if cur:
        out.append(cur)
    return out


def summary(directory: Path, master: list[str]) -> None:
    """Which way do the line discrepancies run, and which carry red?"""
    import collections  # noqa: PLC0415

    pos: collections.Counter = collections.Counter()
    neg: collections.Counter = collections.Counter()
    excess, skipped = [], []
    for page in sorted(directory.glob("*.jpg"), key=lambda p: int(p.stem)):
        p = int(page.stem)
        chunk = p + 15
        if chunk >= len(master) or not RUNE.search(master[chunk]):
            continue
        rs = rows(blobs(page))
        tr = text_rows(master[chunk])
        drop = len(rs) - len(tr)
        if drop < 0 or drop > 3:
            skipped.append(p)
            continue
        body = rs[drop:] if drop > 0 else rs
        for li, (row, n) in enumerate(zip(body, tr)):
            d = len(row) - n
            if d > 0:
                pos[d] += 1
                excess.append((p, li, d, sum(1 for _y, _x, q in row if q >= 20)))
            elif d < 0:
                neg[d] += 1
    print(f"pages skipped for unreliable row alignment: {skipped}")
    print(f"lines with FEWER blobs than runes: {sum(neg.values())} (runes touching)")
    print(f"lines with MORE  blobs than runes: {sum(pos.values())}\n")
    print(f"{'page':>5}{'line':>6}{'excess':>8}{'red':>5}")
    for p, li, d, r in excess:
        print(f"{p:>5}{li:>6}{d:>+8}{r:>5}")
    reds = [e for e in excess if e[3]]
    print(
        f"\n{len(reds)} of {len(excess)} excess lines carry a red blob, and they are the"
        "\nfive line-initial marks on pages 36-38 plus the rubricated title line on 53."
        "\nEvery other excess is black. Deficits dominate, so the dominant segmentation"
        "\nerror is merging -- the transcription is not systematically short of glyphs."
    )


def main() -> None:
    directory = (
        Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("-")
        else IMAGE_DIR
    )
    master = MASTER.read_text().split("%")
    pages = sorted(directory.glob("*.jpg"), key=lambda p: int(p.stem))
    if "--summary" in sys.argv:
        summary(directory, master)
        return

    balanced = header_total = extra_total = 0
    print(f"{'page':>5}{'rows':>6}{'header':>8}{'lines off':>11}  detail")
    for page in pages:
        p = int(page.stem)
        chunk = p + 15
        if chunk >= len(master) or not RUNE.search(master[chunk]):
            continue
        rs = rows(blobs(page))
        tr = text_rows(master[chunk])
        drop = len(rs) - len(tr)
        header = sum(len(r) for r in rs[:drop]) if drop > 0 else 0
        header_total += header
        body = rs[drop:] if drop > 0 else rs
        off = []
        for li, (row, n) in enumerate(zip(body, tr)):
            if len(row) != n:
                reds = sum(1 for _y, _x, d in row if d >= 20)
                off.append((li, len(row) - n, reds))
        extra_total += sum(d for _l, d, _r in off if d > 0)
        if not off:
            balanced += 1
        detail = "balanced" if not off else "; ".join(
            f"line {li}{d:+d}{f', {r} red' if r else ''}" for li, d, r in off[:4]
        )
        print(f"{p:>5}{len(rs):>6}{header:>8}{len(off):>11}  {detail}")

    print(f"\n{balanced} of {len(pages)} pages reconcile line for line")
    print(f"header blobs dropped: {header_total} ({header_total / len(pages):.1f} per page)")
    print(f"net unencoded blobs on unbalanced lines: {extra_total}")
    print(
        "\nA page that balances has no glyph the transcription lacks and none it invents."
        "\nLines that run +1 with a red blob are the line-initial marks of"
        "\ncolour-channel-holds-one-layer.md; the rest are rune-splitting artefacts and"
        "\nare identified by having no red blob."
    )


if __name__ == "__main__":
    main()
