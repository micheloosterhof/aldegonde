# ABOUTME: Applies a review export to all three transcription files at once,
# ABOUTME: matching lines by content so differing page numbering cannot misplace one.
"""Apply a review pass to the transcription files.

`apply_review.py` writes `.marks.txt` copies for inspection. Once a pass is
trusted this puts it into the files themselves.

Lines are matched by CONTENT, not by page and line index. The three files
number their pages differently — the master carries the solved intro's own `%`
markers, and `page0-56.txt` holds pages 0-55 — so a coordinate correct in one
file lands on the wrong line in another. An earlier pass keyed by index put 1 of
6 corrections into the master and looked like it had worked.

Four limits, enforced rather than trusted, each aborting without a write:

  * no line added or removed;
  * no rune or content character altered — a review corrects marks only;
  * every replaced line must occur exactly once in the file, so a correction
    cannot be applied to the wrong copy of an ambiguous line;
  * only characters in the mark alphabet may differ.

Usage:  python3 -m experiments.apply_verdicts <review.json> [--write]
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from aldegonde import c3301
from experiments.apply_review import normalise
from experiments.page_reader import read_page
from experiments.transcription_review import align

ROOT = Path(__file__).resolve().parent.parent
# A transcription tool, not an analysis: it reads and writes the full
# transcription, so the cipher-only corpus is not its reference.
PAGES = ROOT / "data" / "page0-58.txt"
TARGETS = [
    ROOT / "data" / "page0-58.txt",
    ROOT / "data" / "page0-56.txt",
    ROOT / "data" / "liber-primus__transcription--master.txt",
]
RUNE = re.compile(r"[ᚠ-᛿]")
PAYLOAD = re.compile(r"[ᚠ-᛿0-9A-Za-z'\"]")


def pairs_from(review: Path) -> tuple[list[tuple[str, str]], Counter, list[str]]:
    verdicts = {(v["page"], str(v["line"])): v for v in json.loads(review.read_text())}
    blocks = PAGES.read_text().split("%")
    pairs: list[tuple[str, str]] = []
    stats: Counter[str] = Counter()
    problems: list[str] = []

    for page in range(len(blocks)):
        lines = [line for line in blocks[page].split("\n") if RUNE.search(line)]
        for _band, text, lineno in align(read_page(page), lines):
            if lineno is None or text is None:
                continue
            v = verdicts.pop((page, str(lineno)), None)
            if v is None:
                stats["unreviewed"] += 1
                continue
            body = text.rstrip("/")
            # a reviewer may write (23) for a dot count, or space a line out
            want = normalise(v["value"])
            if PAYLOAD.findall(body) != PAYLOAD.findall(want):
                problems.append(f"page {page} line {lineno}: runes or content differ")
                stats["refused"] += 1
                continue
            bad = {c for c in want if not PAYLOAD.match(c) and c not in c3301.MARKS}
            if bad:
                problems.append(
                    f"page {page} line {lineno}: unrecognised {''.join(sorted(bad))}"
                )
                stats["refused"] += 1
                continue
            stats[
                {"txt": "txt kept", "scan": "scan taken", "edit": "edited"}.get(
                    v.get("source"), "applied"
                )
            ] += 1
            new = want + text[len(body) :]
            if new != text:
                pairs.append((text, new))
    stats["no such line"] = len(verdicts)
    return pairs, stats, problems


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: python3 -m experiments.apply_verdicts <review.json> [--write]")
    pairs, stats, problems = pairs_from(Path(sys.argv[1]))

    for k in (
        "txt kept",
        "scan taken",
        "edited",
        "refused",
        "unreviewed",
        "no such line",
    ):
        if stats[k]:
            print(f"   {k:>14}: {stats[k]}")
    print(f"\n{len(pairs)} lines would change")
    if problems:
        print(f"\n{len(problems)} refused:")
        for p in problems[:15]:
            print(f"   {p}")

    if "--write" not in sys.argv:
        print("\n(dry run; pass --write)")
        return

    for path in TARGETS:
        text = before = path.read_text()
        applied = skipped = 0
        for old, new in pairs:
            n = text.count(old)
            if n == 1:
                text = text.replace(old, new)
                applied += 1
            elif n == 0:
                skipped += 1
            else:
                sys.exit(f"{path.name}: a line occurs {n} times; refusing")
        if PAYLOAD.findall(before) != PAYLOAD.findall(text):
            sys.exit(f"{path.name}: payload changed; refusing")
        if before.count("\n") != text.count("\n"):
            sys.exit(f"{path.name}: line count changed; refusing")
        path.write_text(text, encoding="utf-8")
        print(
            f"{path.name}: {applied} applied"
            + (f", {skipped} lines absent from this file" if skipped else "")
        )


if __name__ == "__main__":
    main()
