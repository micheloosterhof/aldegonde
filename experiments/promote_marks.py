# ABOUTME: Promotes the remaining '.' marks to their circled dot count, taking
# ABOUTME: the reviewed verdict where there is one and the scan otherwise.
"""Encode every remaining `.` as the glyph the page actually carries.

`-` is already migrated to ①. `.` was held back because it collapses at least
four glyphs — 4-dot, 10-dot, 13-dot and a 23-dot — and 51 of 175 turned out not
to be the 4-dot mark, so a blanket conversion would have baked in wrong counts.

Two sources resolve it, in this order:

1. **A reviewed verdict.** Michel adjudicated every line where scan and
   transcription disagreed, against the page images. Those lines take their
   verdict verbatim.

2. **The scan, on lines that were never flagged.** A line went unflagged only
   if the reader read a 4-dot cluster at every position the transcription marks
   `.`, so `.` → ④ there is confirmed by the image rather than assumed. The
   reader's own count is used, not a fixed ④, so a line whose marks were
   already agreed cannot silently acquire the wrong one.

A line whose mark COUNT differs between reader and transcription is left alone
and reported: the two disagree about how many marks exist, which is not
something a promotion should guess at.

Invariants, all enforced: no line added or removed, no rune or content
character altered, and only mark characters differ.

Usage:  python3 -m experiments.promote_marks [--write]
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from experiments.page_reader import read_page
from experiments.transcription_review import CIRCLED_SET, align, circled

ROOT = Path(__file__).resolve().parent.parent
# A transcription tool, not an analysis: it reads and writes the full
# transcription, so the cipher-only corpus is not its reference.
PAGES = ROOT / "data" / "page0-58.txt"
TARGETS = [
    ROOT / "data" / "page0-58.txt",
    ROOT / "data" / "page0-56.txt",
    ROOT / "data" / "liber-primus__transcription--master.txt",
]
REVIEW = Path.home() / "Downloads" / "review (1).json"
RUNE = re.compile(r"[ᚠ-᛿]")
PAYLOAD = re.compile(r"[ᚠ-᛿0-9A-Za-z'\"]")
LEGACY = "."


def verdicts() -> dict[tuple[int, str], str]:
    if not REVIEW.exists():
        return {}
    return {
        (v["page"], str(v["line"])): v["value"] for v in json.loads(REVIEW.read_text())
    }


def reader_marks(band) -> list[str]:
    """Dot-mark characters the scan reads on this line, in order.

    Apostrophes and quotes are excluded: the transcription carries them as
    content, so counting them here would make every tick line look as though
    the page held one mark more than the text does.
    """
    return [circled(g.dots) for g in band if g.kind == "M"]


def promote(line: str, marks: list[str]) -> tuple[str, str | None]:
    """Replace each legacy `.` with the scan's glyph for that position."""
    body = line.rstrip("/")
    slots = [i for i, c in enumerate(body) if not PAYLOAD.match(c)]
    if len(slots) != len(marks):
        return line, f"{len(slots)} marks in the text, {len(marks)} on the page"
    out = list(body)
    for i, m in zip(slots, marks):
        if out[i] == LEGACY:
            if m not in CIRCLED_SET:
                return line, f"scan reads {m!r} where the text has '.'"
            out[i] = m
    return "".join(out) + line[len(body) :], None


def main() -> None:
    review = verdicts()
    blocks = PAGES.read_text().split("%")
    pairs: list[tuple[str, str]] = []
    stats: Counter[str] = Counter()
    problems: list[str] = []

    for page in range(len(blocks)):
        lines = [line for line in blocks[page].split("\n") if RUNE.search(line)]
        for band, text, lineno in align(read_page(page), lines):
            if lineno is None or band is None or LEGACY not in text:
                continue
            got = review.get((page, str(lineno)))
            if got is not None:
                new, err = promote(text, [c for c in got if not PAYLOAD.match(c)])
                stats["from a reviewed verdict" if not err else "refused"] += 1
            else:
                new, err = promote(text, reader_marks(band))
                stats["from the scan" if not err else "refused"] += 1
            if err:
                problems.append(f"page {page} line {lineno}: {err}")
                continue
            if new != text:
                pairs.append((text, new))

    print(f"lines carrying a legacy '.': {sum(stats.values())}")
    for k in ("from a reviewed verdict", "from the scan", "refused"):
        print(f"   {k:>24}: {stats[k]}")
    census = Counter(c for _, new in pairs for c in new if c in CIRCLED_SET)
    print(
        "\nglyphs introduced: "
        + "  ".join(f"{c}{n}" for c, n in sorted(census.items()) if c != "①")
    )
    if problems:
        print(f"\n{len(problems)} lines left alone:")
        for p in problems[:15]:
            print(f"   {p}")

    if "--write" not in sys.argv:
        print(f"\n(dry run; {len(pairs)} lines would change, pass --write)")
        return

    for path in TARGETS:
        text = path.read_text()
        before, applied = text, 0
        for old, new in pairs:
            if text.count(old) == 1:
                text = text.replace(old, new)
                applied += 1
        if PAYLOAD.findall(before) != PAYLOAD.findall(text):
            sys.exit(f"{path.name}: payload changed; refusing")
        if before.count("\n") != text.count("\n"):
            sys.exit(f"{path.name}: line count changed; refusing")
        path.write_text(text, encoding="utf-8")
        print(f"{path.name}: {applied} lines, '.' now {text.count(LEGACY)}")


if __name__ == "__main__":
    main()
