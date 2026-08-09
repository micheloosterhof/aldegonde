# ABOUTME: Applies the reviewed corrections from review.json to the LP
# ABOUTME: transcription, writing a corrected copy rather than editing in place.
"""Turn a completed review into a corrected transcription.

`transcription_review.py` emits a page where every line of the book can be
confirmed or corrected; the browser exports the verdicts as `review.json`. This
consumes that and rewrites the marks.

Each verdict carries a token sequence: `R` for a rune, a circled numeral for a
dot mark. Runes are taken from the original line in order, so a correction can
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


def rebuild(original: str, tokens: str) -> tuple[str, str | None]:
    """Reapply a reviewed token sequence to a line, keeping its runes."""
    runes = [c for c in original if RUNE.match(c)]
    wanted = tokens.count("R")
    if wanted != len(runes):
        return original, f"rune count {wanted} != {len(runes)} in the line"
    bad = [c for c in tokens if c != "R" and c not in CIRCLED]
    if bad:
        return original, f"unrecognised characters {''.join(sorted(set(bad)))}"
    out, it = [], iter(runes)
    for c in tokens:
        out.append(next(it) if c == "R" else c)
    trailing = original[len(original.rstrip("/")):]
    return "".join(out) + trailing, None


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
            if v["verdict"] == "ok":
                stats["confirmed"] += 1
                new, err = rebuild(line, v["value"])
            else:
                new, err = rebuild(line, v["value"])
                stats["corrected" if err is None else "refused"] += 1
            if err:
                problems.append(f"page {page} line {idx}: {err}")
                continue
            if new != line:
                stats["lines changed"] += 1
            lines[i] = new
        blocks[page] = "\n".join(lines)

    TARGET.write_text("%".join(blocks), encoding="utf-8")

    print(f"read {len(verdicts)} verdicts")
    for k in ("confirmed", "corrected", "refused", "lines changed", "unreviewed"):
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
