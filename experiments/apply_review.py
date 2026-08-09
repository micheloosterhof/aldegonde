# ABOUTME: Applies the reviewed corrections from review.json to the LP
# ABOUTME: transcription, writing a corrected copy rather than editing in place.
"""Turn a completed review into a corrected transcription.

`transcription_review.py` emits a page where every line of the book can be
confirmed or corrected; the browser exports the verdicts as `review.json`. This
consumes that and rewrites the marks.

Each verdict carries an explicit source — `txt` keeps the existing
transcription, `scan` takes the reader's version, `edit` takes what was typed —
and the token sequence that choice resolves to: `R` for a rune, a circled
numeral for a dot mark. The stored sequence is always exactly what the line
becomes, so nothing has to be re-derived here. Runes are taken from the original line in order, so a correction can
only change the MARKS — the number and identity of runes must match. A verdict
that changes the rune count is refused and reported, because that is a
rune-level claim about a transcription whose rune values are otherwise settled
(`transcription-is-verified`), and it should be raised deliberately rather than
slipped in through a mark review.

Structural characters the project added itself are not dot marks and pass
through untouched: `/` end of line, `%` end of page, `&` end of paragraph,
`$` end of section.

Nothing is overwritten. The result goes to a new file so the two can be
diffed before anything downstream is repointed.

Usage:  python3 -m experiments.apply_review review/transcription/review.json
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "page0-58.txt"
TARGET = ROOT / "data" / "page0-58.marks.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
CIRCLED = set("①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑈")


def rebuild(original: str, value: str) -> tuple[str, str | None]:
    """Validate a reviewed line and return it with its trailing structure.

    The value is the line itself: real runes and circled marks. Its runes must
    match the original line's exactly, in order — a mark review may change
    marks and nothing else.
    """
    want = [c for c in original if RUNE.match(c)]
    got = [c for c in value if RUNE.match(c)]
    if got != want:
        if len(got) != len(want):
            return original, f"rune count {len(got)} != {len(want)}"
        return original, "rune identities changed"
    bad = {c for c in value if not RUNE.match(c) and c not in CIRCLED}
    if bad:
        return original, f"unrecognised characters {''.join(sorted(bad))}"
    return value + original[len(original.rstrip("/")):], None


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip().splitlines()[-1])
    verdicts = json.loads(Path(sys.argv[1]).read_text())
    by_key = {(v["page"], v["line"]): v for v in verdicts}

    blocks = SOURCE.read_text().split("%")
    stats: Counter[str] = Counter()
    problems: list[str] = []

    for page, block in enumerate(blocks):
        lines = block.split("\n")
        idx = -1
        for i, line in enumerate(lines):
            if not RUNE.search(line):
                continue
            idx += 1
            v = by_key.get((page, idx))
            if v is None:
                stats["unreviewed"] += 1
                continue
            new, err = rebuild(line, v["value"])
            if err:
                stats["refused"] += 1
            else:
                stats[{"txt": "txt kept", "scan": "scan taken",
                       "edit": "edited"}.get(v.get("source"), "applied")] += 1
            if err:
                problems.append(f"page {page} line {idx}: {err}")
                continue
            if new != line:
                stats["lines changed"] += 1
            lines[i] = new
        blocks[page] = "\n".join(lines)

    TARGET.write_text("%".join(blocks), encoding="utf-8")

    print(f"read {len(verdicts)} verdicts")
    for k in ("txt kept", "scan taken", "edited", "refused",
              "lines changed", "unreviewed"):
        print(f"   {k:>15}: {stats[k]}")
    if problems:
        print(f"\n{len(problems)} refused:")
        for p in problems[:20]:
            print(f"   {p}")
    text = TARGET.read_text()
    print(f"\nwrote {TARGET.relative_to(ROOT)}")
    print("   mark census: " + "  ".join(
        f"{c} {text.count(c)}" for c in sorted(CIRCLED) if text.count(c)))
    print(f"   remaining legacy '-' {text.count('-')}  '.' {text.count('.')}")


if __name__ == "__main__":
    main()
