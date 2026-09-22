# ABOUTME: One correct parser for the body: blocks carry across line breaks, and each
# ABOUTME: mark keeps its own line-end status, which several files got wrong separately.
"""Words span line breaks. Several experiments written this session forgot that.

`hypotheses/README.md` states the convention: "`/` and newlines are line wraps, **not**
word boundaries -- words span them (verified in the readable sections: `ᛋᚪᚳ/ᚱᛖᛞ` =
SAC/RED)". And 76% of the body's lines end mid-word.

A parser that iterates line by line and resets its rune counter at each line start cuts
every wrapped word in two. On the body that is roughly 450 spurious block boundaries out
of 2,900, and it moves the session's central statistic from **-0.24 to +0.13**.

Three files written this session had that bug independently, because each grew its own
parser to get line-end status for the marks. This module supplies both facts at once so
they cannot drift apart again:

- the rune counter carries across line breaks, so a block is a whole word;
- each mark records whether a rune follows it **on its own line**, which is well defined
  even when the block it closes began on the previous line.

It also reproduces the word indexing that `rubricated_titles.json` was built with, so
title word ranges line up. They disagree on 45 of 58 chunks under the per-line reading.

    python body_parse.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
MARKS = set("④⑬③⑩㉓.")
SEPARATORS = set("①-")
BODY = range(15, 71)
FRONT = range(15)


def chunk_blocks(chunk: str):
    """[(length, closing glyph, mark at a line end?)] with blocks spanning line wraps.

    Annotation lines -- those with no rune -- are dropped, since their delimiters are not
    word separators. A block that begins on one line and ends on the next is one block,
    and the line-end flag belongs to the closing glyph's own line.
    """
    out: list[tuple[int, str, bool]] = []
    n = 0
    for line in re.split(r"[/\n]", chunk):
        if not RUNE.search(line):
            continue
        for i, ch in enumerate(line):
            if RUNE.match(ch):
                n += 1
            elif (ch in MARKS or ch in SEPARATORS) and n:
                out.append((n, ch, not RUNE.search(line[i + 1 :])))
                n = 0
    if n:
        out.append((n, "", False))
    return out


def blocks(chunks=BODY):
    text = MASTER.read_text().split("%")
    out = []
    for ci in chunks:
        if ci < len(text):
            out.extend(chunk_blocks(text[ci]))
    return out


def spans(closer: set[str], chunks=BODY, minimum: int = 3):
    """Runs of block lengths closed by any glyph in `closer`."""
    out, cur = [], []
    for length, glyph, _ in blocks(chunks):
        cur.append(length)
        if glyph in closer:
            if len(cur) >= minimum:
                out.append(cur)
            cur = []
    return out


def main() -> None:
    body = blocks()
    print(f"{len(body):,} body blocks, mean length "
          f"{sum(b[0] for b in body) / len(body):.2f}")
    print("  the canonical figures are 2,928 blocks at mean 4.42\n")

    wrong, n = [], 0
    text = MASTER.read_text().split("%")
    for ci in BODY:
        if ci >= len(text):
            continue
        for line in re.split(r"[/\n]", text[ci]):
            if not RUNE.search(line):
                continue
            n = 0
            for ch in line:
                if RUNE.match(ch):
                    n += 1
                elif (ch in MARKS or ch in SEPARATORS) and n:
                    wrong.append(n)
                    n = 0
    print(f"a per-line parser finds {len(wrong):,} blocks at mean "
          f"{sum(wrong) / len(wrong):.2f} -- {len(wrong) - len(body):,} spurious")

    s = spans({"④"})
    last = [x[-1] for x in s]
    inner = [x for row in s for x in row[1:-1]]
    print(
        f"\nfour-dot spans: {len(s)}   final gap "
        f"{sum(last) / len(last) - sum(inner) / len(inner):+.2f}"
    )
    print("  the session's central number is -0.24; a per-line parser gives +0.13")


if __name__ == "__main__":
    main()
