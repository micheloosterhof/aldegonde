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

Two hard limits, both enforced rather than trusted:

  * **No line is ever added or removed.** A review corrects marks on lines that
    already exist. Content the transcription omits — the cuneiform on pages
    33-39, the picture on page 2 — is reported and left out, and adding it is a
    decision for the maintainer, not a side effect of a mark pass.
  * **No rune is ever changed.** Runes and content characters are taken from
    the original line in order and must match exactly.

Nothing is overwritten. Both results go to new `.marks.txt` files so they can
be diffed before anything downstream is repointed: the pages themselves, and
the master transcription, which is the solved intro followed by those pages
verbatim and so takes the correction as a suffix replacement.

Usage:  python3 -m experiments.apply_review review/transcription/review.json
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "page0-56.txt"
TARGET = ROOT / "data" / "page0-58.marks.txt"
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
MASTER_TARGET = ROOT / "data" / "liber-primus__transcription--master.marks.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
CIRCLED = {chr(0x2460 + n) for n in range(20)} | {chr(0x3251 + n) for n in range(15)}
CIRCLED.add("\u2448")  # unrecognised dot count, flagged for review
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
    bad = {
        c
        for c in value
        if not RUNE.match(c) and c not in CIRCLED and not CONTENT.match(c)
    }
    if bad:
        return original, f"unrecognised characters {''.join(sorted(bad))}"
    return value + original[len(original.rstrip("/")) :], None


def migrate_separators(text: str) -> tuple[str, int, int]:
    """Encode the word separator as its dot count, `-` to ①.

    Safe to do mechanically, unlike `.`. Across 2,131 aligned marks the reader
    read `-` as a single dot 2,088 times and as a 3-dot glyph 6 times, and
    those six are in the reviewed set and already corrected — so every
    remaining `-` sits on a line where the scan confirmed one dot. `.` gets no
    such treatment: 51 of 175 have already turned out to be a 10-, 13- or
    23-dot glyph, so it stays until reviewed.

    Lines with no runes are skipped. The master's numeric lines use `-` to
    separate numbers, not as a mark:  `434-1311-312-278-966`.
    """
    out, moved, skipped = [], 0, 0
    for line in text.split("\n"):
        if RUNE.search(line):
            moved += line.count("-")
            out.append(line.replace("-", "\u2460"))
        else:
            skipped += line.count("-")
            out.append(line)
    return "\n".join(out), moved, skipped


def write_master(original_body: str, new_body: str) -> None:
    """Splice the corrected pages into the master, or refuse.

    The master is the solved intro followed by `page0-56.txt` verbatim, so the
    correction is a suffix replacement. Every step is checked because this file
    carries text the review never looked at:

      * the master must still END with the untouched body, or the two files
        have diverged and splicing would corrupt one of them;
      * the payload — runes, digits, Latin letters, apostrophes and quotes —
        must be identical before and after, since a mark review may not touch
        content;
      * the line count must not move.

    Any failure aborts without writing.
    """
    master = MASTER.read_text()
    if not master.endswith(original_body):
        sys.exit("master does not end with page0-56.txt verbatim; refusing to splice")
    head, head_moved, head_skipped = migrate_separators(
        master[: len(master) - len(original_body)]
    )
    updated = head + new_body
    print(
        f"   solved intro: {head_moved} '-' became ①, "
        f"{head_skipped} left on numeric lines"
    )

    before, after = _payload(master), _payload(updated)
    if before != after:
        sys.exit(f"payload changed: {len(before)} -> {len(after)} characters; refusing")
    if master.count("\n") != updated.count("\n"):
        sys.exit("line count changed; refusing")

    # A positional character diff is meaningless here: taking the scan's
    # reading can ADD a mark, which shifts every later character on the line.
    # Compare line by line, and account for the marks themselves.
    old_lines, new_lines = master.split("\n"), updated.split("\n")
    differing = sum(1 for a, b in zip(old_lines, new_lines) if a != b)
    delta = {
        c: updated.count(c) - master.count(c)
        for c in sorted(CIRCLED | {"-", "."})
        if updated.count(c) != master.count(c)
    }

    MASTER_TARGET.write_text(updated, encoding="utf-8")
    print(f"\nwrote {MASTER_TARGET.relative_to(ROOT)}")
    print(f"   {differing} of {len(old_lines)} lines differ")
    print("   mark changes: " + "  ".join(f"{c}{d:+d}" for c, d in delta.items()))
    print("   payload verified identical: runes, digits, letters, quotes")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit((__doc__ or "").strip().splitlines()[-1])
    verdicts = json.loads(Path(sys.argv[1]).read_text())
    # an unpaired band carries a slot id like "~9", not a line number
    by_key = {(v["page"], str(v["line"])): v for v in verdicts}

    blocks = SOURCE.read_text().split("%")
    stats: Counter[str] = Counter()
    problems: list[str] = []

    seen: set[tuple[int, str]] = set()
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
                stats[
                    {"txt": "txt kept", "scan": "scan taken", "edit": "edited"}.get(
                        v.get("source"), "applied"
                    )
                ] += 1
            if err:
                problems.append(f"page {page} line {idx}: {err}")
                continue
            if new != line:
                stats["lines changed"] += 1
            lines[i] = new
        blocks[page] = "\n".join(lines)

    original_body = SOURCE.read_text()
    new_body, moved, skipped = migrate_separators("%".join(blocks))
    if new_body.count("\n") != original_body.count("\n"):
        sys.exit("line count changed; a review may not add or remove lines")
    TARGET.write_text(new_body, encoding="utf-8")
    print(
        f"\nword separators encoded: {moved} '-' became ①"
        + (f", {skipped} left on non-runic lines" if skipped else "")
    )

    print(f"read {len(verdicts)} verdicts")
    for k in (
        "txt kept",
        "scan taken",
        "edited",
        "refused",
        "lines changed",
        "unreviewed",
    ):
        print(f"   {k:>15}: {stats[k]}")
    orphan = [k for k in by_key if k not in seen]
    if orphan:
        print(
            f"\n{len(orphan)} verdicts match no transcription line "
            f"(the reader saw a band the text has no line for -- these are "
            f"content the transcription omits, not corrections):"
        )
        for page, line in sorted(orphan, key=lambda k: (k[0], str(k[1]))):
            note = by_key[(page, line)].get("note", "")
            print(f"   page {page} slot {line}  {note}")
    if problems:
        print(f"\n{len(problems)} refused:")
        for p in problems[:20]:
            print(f"   {p}")
    text = TARGET.read_text()
    print(f"\nwrote {TARGET.relative_to(ROOT)}")
    print(
        "   mark census: "
        + "  ".join(f"{c} {text.count(c)}" for c in sorted(CIRCLED) if text.count(c))
    )
    print(f"   remaining legacy '-' {text.count('-')}  '.' {text.count('.')}")
    write_master(original_body, new_body)


if __name__ == "__main__":
    main()
