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
CIRCLED = {chr(0x2460 + n) for n in range(20)} | {chr(0x3251 + n) for n in range(15)}
CIRCLED.add("\u2448")          # unrecognised dot count, flagged for review
# Digits and Latin letters are CONTENT, not annotation: the hex block and the
# plaintext Parable in sections 10-11 carry them, and page 10 line 7 has a
# bare "7" inside the runic text. They pass through untouched.
CONTENT = re.compile(r"[0-9A-Za-z]")
CIRCLED_BY_N = {n: chr(0x2460 + n - 1) for n in range(1, 21)}
CIRCLED_BY_N.update({n: chr(0x3251 + n - 21) for n in range(21, 36)})


def normalise(value: str) -> str:
    """Accept a reviewer's shorthand: `(N)` for a dot count, and whitespace
    anywhere for readability. Neither is meaningful in the encoding, so both
    are normalised away rather than refused."""
    def sub(m: re.Match[str]) -> str:
        return CIRCLED_BY_N.get(int(m.group(1)), m.group(0))
    return re.sub(r"\s+", "", re.sub(r"\((\d{1,2})\)", sub, value))


def _payload(text: str) -> list[str]:
    """Runes and content characters, i.e. everything a mark review may not touch."""
    return [c for c in text if RUNE.match(c) or CONTENT.match(c)]


def rebuild(original: str, value: str) -> tuple[str, str | None]:
    """Validate a reviewed line and return it with its trailing structure.

    The value is the line itself: real runes and circled marks. Its runes must
    match the original line's exactly, in order — a mark review may change
    marks and nothing else.
    """
    want, got = _payload(original), _payload(value)
    if got != want:
        if len(got) != len(want):
            return original, f"rune count {len(got)} != {len(want)}"
        return original, "rune or content identities changed"
    bad = {c for c in value
           if not RUNE.match(c) and c not in CIRCLED and not CONTENT.match(c)}
    if bad:
        return original, f"unrecognised characters {''.join(sorted(bad))}"
    return value + original[len(original.rstrip("/")):], None


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip().splitlines()[-1])
    verdicts = json.loads(Path(sys.argv[1]).read_text())
    # an unpaired band carries a slot id like "~9", not a line number
    by_key = {(v["page"], str(v["line"])): v for v in verdicts}

    blocks = SOURCE.read_text().split("%")
    stats: Counter[str] = Counter()
    problems: list[str] = []

    seen: set[tuple[int, int]] = set()
    for page, block in enumerate(blocks):
        lines = block.split("\n")
        idx = -1
        for i, line in enumerate(lines):
            if not RUNE.search(line):
                continue
            idx += 1
            seen.add((page, str(idx)))
            v = by_key.get((page, str(idx)))
            if v is None:
                stats["unreviewed"] += 1
                continue
            new, err = rebuild(line, normalise(v["value"]))
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
    orphan = [k for k in by_key if k not in seen]
    if orphan:
        print(f"\n{len(orphan)} verdicts match no transcription line "
              f"(the reader saw a band the text has no line for -- these are "
              f"content the transcription omits, not corrections):")
        for page, line in sorted(orphan, key=lambda k: (k[0], str(k[1]))):
            note = by_key[(page, line)].get("note", "")
            print(f"   page {page} slot {line}  {note}")
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
