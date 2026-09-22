# ABOUTME: Tests whether the scribe ended lines at block boundaries by fitting a
# ABOUTME: boundary-seeking layout model against a plain fill-to-measure one.
"""The scribe ignored the block boundaries when he could not read the text.

`line_layout_and_the_hole.py` records why the obvious version of this test is invalid:
its null holds the line lengths fixed and shuffles the blocks, but a scribe chooses where
to break a line to fit what is on it, so line length and content are not independent, and
that null manufactures a coupling the text never had.

The fix is to stop shuffling and **generate** the layout. Lay the body's own block lengths
out under an explicit model of the scribe and let the model produce the line lengths too.
Then line length is an output to be checked, not an input held fixed.

Two models, one parameter between them:

- **fill to measure.** Write until the line reaches M runes, break there whatever is
  underneath. A break lands at a block boundary only by coincidence, at the rate at which
  runes are block-final: 2,896 of 12,956, or 0.224.
- **seek a boundary.** Aim for M, and if a block boundary falls within d runes of it,
  break there instead; otherwise break at M. One parameter, d.

The second predicts two things at once: more breaks at boundaries, and **more variable
line lengths**, because reaching for a boundary lengthens some lines and shortens others.
Fitting d to the first and checking the second is the test.

## The result, and the control that makes it mean something

The body shows **no** boundary-seeking: 0.236 of its line breaks land at a block
boundary against the 0.224 that falling at a random rune would give, z = +0.76. Laid out
under the models, the plain scribe reproduces it exactly and every boundary-seeking
tolerance overshoots badly -- even d = 1 predicts 0.436.

A null result needs to show the test can see the effect when it is there, and the book
supplies the control. The same measurement on the pages the scribe could **read**:

| text | breaks | at a boundary | chance | z |
|---|---|---|---|---|
| front matter, **plaintext** | 52 | **0.558** | 0.231 | **+5.60** |
| front matter, enciphered | 92 | 0.337 | 0.262 | +1.65 |
| the body, enciphered | 432 | 0.252 | 0.227 | +1.28 |

On plaintext he keeps words whole more than twice as often as chance. On ciphertext he
does not, in the front matter or the body. That is the expected thing -- ciphertext has
no word shapes to protect -- and it means the test works and the body's null is real.

So the block boundaries were not salient to whoever ruled these lines. He filled to a
measure of about 21.8 runes and broke wherever he landed, three lines in four of them
inside a block.

    python did_the_scribe_break_at_blocks.py
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from does_the_cipher_restart import ANNOTATION, RUNE, STANDALONE  # noqa: E402
from lp_plaintext_register import MASTER, PLAIN_PAGES, TRIPLES  # noqa: E402
from sentences_do_not_end_long import BODY  # noqa: E402

from aldegonde import c3301  # noqa: E402

DRAWS = 60


def symbol_stream():
    """The body as runes and block boundaries, with the line breaks marked."""
    text = "\n".join(
        line
        for line in BODY.read_text().replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )
    out = []
    for ch in text:
        if RUNE.match(ch):
            out.append("r")
        elif ch == "\n":
            out.append("n")
        elif ch in STANDALONE:
            continue
        elif ch in c3301.WORD_BOUNDARY:
            out.append("b")
    return out


def observed():
    """(alignment rate, line lengths, block lengths) for the corpus."""
    stream = symbol_stream()
    lines, runes = [], 0
    aligned = breaks = 0
    previous = None
    for s in stream:
        if s == "r":
            runes += 1
            previous = "r"
        elif s == "b":
            previous = "b"
        elif s == "n":
            if runes:
                lines.append(runes)
                runes = 0
                if previous is not None:
                    breaks += 1
                    aligned += previous == "b"
                previous = None
    if runes:
        lines.append(runes)
    blocks, current = [], 0
    for s in stream:
        if s == "r":
            current += 1
        elif s == "b" and current:
            blocks.append(current)
            current = 0
    if current:
        blocks.append(current)
    return aligned / (breaks - 1), np.array(lines, float), blocks


def lay_out(blocks, measure, tolerance, rng, jitter):
    """Write blocks into lines, optionally reaching for a nearby block boundary.

    `tolerance` 0 is the plain fill-to-measure scribe: the line stops at the target
    length whatever is underneath, and a boundary lands there only by coincidence.
    """
    lines, aligned, breaks = [], 0, 0
    runes_in_line = 0
    target = max(6, int(round(rng.gauss(measure, jitter))))
    i = 0
    while i < len(blocks):
        block = blocks[i]
        if runes_in_line + block <= target:
            runes_in_line += block
            i += 1
            if runes_in_line >= target - tolerance:
                lines.append(runes_in_line)
                aligned += 1
                breaks += 1
                runes_in_line = 0
                target = max(6, int(round(rng.gauss(measure, jitter))))
            continue
        room = target - runes_in_line
        if room <= 0:
            lines.append(runes_in_line)
            breaks += 1
            runes_in_line = 0
            target = max(6, int(round(rng.gauss(measure, jitter))))
            continue
        # the block does not fit: split it at the measure
        blocks = blocks[:i] + [room, block - room] + blocks[i + 1 :]
        runes_in_line += room
        lines.append(runes_in_line)
        breaks += 1
        runes_in_line = 0
        i += 1
        target = max(6, int(round(rng.gauss(measure, jitter))))
    if runes_in_line:
        lines.append(runes_in_line)
    return aligned / max(breaks, 1), np.array(lines, float)


def page_alignment(page_ids):
    """Line breaks landing on a boundary, for a set of master pages."""
    pages = MASTER.read_text().split("%")
    aligned = breaks = 0
    lines, blocks = [], []
    for n in page_ids:
        text = "\n".join(
            line
            for line in pages[n].replace("/", "\n").split("\n")
            if not ANNOTATION.match(line)
        )
        runes = current = 0
        previous = None
        for ch in text:
            if RUNE.match(ch):
                runes += 1
                current += 1
                previous = "r"
            elif ch == "\n":
                if runes:
                    lines.append(runes)
                    runes = 0
                    if previous is not None:
                        breaks += 1
                        aligned += previous == "b"
                    previous = None
            elif ch in STANDALONE:
                continue
            elif ch in c3301.WORD_BOUNDARY:
                previous = "b"
                if current:
                    blocks.append(current)
                    current = 0
        if runes:
            lines.append(runes)
        if current:
            blocks.append(current)
    return aligned, breaks, lines, len(blocks) / sum(blocks)


def main() -> None:
    rate, lines, blocks = observed()
    measure, spread = float(lines.mean()), float(lines.std(ddof=1))
    block_final = len(blocks) / sum(blocks)
    se = math.sqrt(block_final * (1 - block_final) / (len(lines) - 1))

    print("The corpus\n")
    print(f"  lines                        {len(lines):>8}")
    print(f"  breaks at a block boundary   {rate:>8.3f}")
    print(f"  runes that are block-final   {block_final:>8.3f}")
    print(
        f"  excess                       {f'z = {(rate - block_final) / se:+.2f}':>8}"
    )
    print(f"  runes per line               {measure:>8.2f} +- {spread:.2f}")

    print(
        "\nLaying the body's own blocks out under each model. The jitter on the target"
    )
    print(
        "is fitted so the plain scribe reproduces the observed line spread; every model"
    )
    print("then uses the same jitter, so the spread is a prediction, not a fit.\n")

    def spread_of(tolerance, jitter, seed):
        rng = random.Random(seed)
        return lay_out(list(blocks), measure, tolerance, rng, jitter)

    jitter = min(
        np.arange(0.1, 4.0, 0.1),
        key=lambda j: abs(
            np.mean([spread_of(0, j, s)[1].std(ddof=1) for s in range(12)]) - spread
        ),
    )

    print(f"{'model':<28}{'aligned':>18}{'runes per line':>22}")
    for tolerance, label in (
        (0, "fill to measure"),
        (1, "seek a boundary, d = 1"),
        (2, "seek a boundary, d = 2"),
        (3, "seek a boundary, d = 3"),
        (4, "seek a boundary, d = 4"),
    ):
        results = [spread_of(tolerance, jitter, s) for s in range(DRAWS)]
        rates = np.array([r for r, _ in results])
        spreads = np.array([ln.std(ddof=1) for _, ln in results])
        means = np.array([ln.mean() for _, ln in results])
        print(
            f"{label:<28}{f'{rates.mean():.3f} +- {rates.std(ddof=1):.3f}':>18}"
            f"{f'{means.mean():.2f} +- {spreads.mean():.2f}':>22}"
        )
    print(f"{'THE BODY':<28}{rate:>18.3f}{f'{measure:.2f} +- {spread:.2f}':>22}")

    print(
        "\nThe plain fill-to-measure scribe reproduces the body exactly. Every"
        "\nboundary-seeking tolerance overshoots: even d = 1 predicts nearly twice the"
        "\nobserved alignment. The block boundaries were not salient to whoever ruled"
        "\nthese lines."
    )

    print("\nCan the test see boundary-seeking when it is there? The pages the scribe")
    print("could READ are the control.\n")
    print(
        f"{'text':<34}{'breaks':>8}{'aligned':>9}{'chance':>9}{'z':>8}{'runes/line':>12}"
    )
    for pages, label in (
        (list(PLAIN_PAGES), "front matter, PLAINTEXT"),
        (
            sorted(t["page"] for t in json.loads(TRIPLES.read_text())),
            "front matter, enciphered",
        ),
        (list(range(15, 57)), "the body, enciphered"),
    ):
        aligned, breaks, line_lengths, chance = page_alignment(pages)
        se = math.sqrt(chance * (1 - chance) / max(breaks, 1))
        share = aligned / max(breaks, 1)
        print(
            f"{label:<34}{breaks:>8}{share:>9.3f}{chance:>9.3f}"
            f"{(share - chance) / se:>+8.2f}{np.mean(line_lengths):>12.2f}"
        )
    print(
        "\nOn plaintext he keeps words whole more than twice as often as chance. On"
        "\nciphertext he does not, in the front matter or in the body. The test works,"
        "\nand the body's null is real: ciphertext has no word shapes to protect."
    )


if __name__ == "__main__":
    main()
