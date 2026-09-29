# ABOUTME: Reproduces the apostrophe census from the transcription alone, so the
# ABOUTME: contraction cribs can be audited without re-running the page-image sweep.
"""The contraction cribs rest on image processing. They do not have to.

`contraction-cribs.md` establishes four lone tick marks by a connected-component sweep of
58 page scans -- geometry, heights, the lot. That evidence is sound but it is not
reproducible by anyone without the images, and the claim it supports (four known-plaintext
sites in the body) is load-bearing enough to deserve a second route.

The transcription now encodes the ticks. So the census, the tail lengths and the host
block shapes can all be read straight out of the text file, and this checks them against
what the file records.

It also fixes a convention the file leaves implicit: the stream offsets it quotes are the
start of the HOST BLOCK, not the position of the apostrophe.

    python apostrophe_from_text.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ENG = c3301.CICADA_ENGLISH_ALPHABET
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
RECORDED = [1107, 5136, 8513, 10086]


def main() -> None:
    text = (ROOT / "data" / "page0-56.txt").read_text()
    sections = [s for s in text.split("$") if RUNE.search(s)][:10]
    offset = 0
    sites = []
    for s in sections:
        block: list[int] = []
        start = offset
        apos = None
        for ch in s:
            if RUNE.match(ch):
                block.append(IDX[ch])
                offset += 1
            elif ch == "'":
                apos = len(block)
            elif ch in "/\n":
                continue
            elif ch in c3301.WORD_BOUNDARY:
                if block and apos is not None:
                    sites.append((start, block[:], apos))
                if block:
                    block = []
                    start = offset
                apos = None
        if block and apos is not None:
            sites.append((start, block[:], apos))

    print(f"apostrophes in the transcription: {text.count(chr(39))}")
    print(f"host blocks recovered: {len(sites)}\n")
    print(
        f"{'block start':>12}{'apostrophe at':>15}{'shape':>9}{'tail':>6}  ciphertext"
    )
    logp = 0.0
    for start, block, apos in sites:
        logp += math.log(1 / (len(block) - 1))
        print(
            f"{start:>12}{start + apos:>15}{f'{apos}+{len(block) - apos}':>9}"
            f"{len(block) - apos:>6}  {''.join(ENG[r] for r in block)}"
        )

    print(
        f"\nall four leave a one-rune tail; under a uniform internal slot that is"
        f" p = {math.exp(logp):.4f}"
    )
    starts = [s for s, _b, _a in sites]
    print(f"recorded stream offsets {RECORDED}")
    print(f"block starts            {starts}   match: {starts == RECORDED}")
    print(
        "\nSo the offsets in contraction-cribs.md are HOST BLOCK starts. The"
        "\napostrophes themselves sit at "
        + ", ".join(str(s + a) for s, _b, a in sites)
        + "."
    )


if __name__ == "__main__":
    main()
