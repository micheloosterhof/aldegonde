# ABOUTME: Places both DJU-BEI occurrences against the book's own structure -- section
# ABOUTME: starts, rubricated titles and the end of the body.
"""Both occurrences sit at marked positions, which is what a deliberate repeat would do.

`dju-bei-ends-the-body.md` finds the second occurrence to be the final six runes of the
body and notes that a deliberate reading -- a closing refrain -- explains that for free
where a coincidence does not. If the repeat is deliberate, the FIRST occurrence should be
somewhere marked too.

It is. Page 27 opens a section, carries a rubricated title, and the repeat is among its
first blocks.

Everything here was noticed after the fact and is quantified as such: the probabilities
below are what a randomly placed unit would score, not pre-registered tests.

    python dju_bei_structural_position.py
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")


def main() -> None:
    stream, wid = load_clean()
    n = len(stream)
    windows = [tuple(stream[i : i + 6]) for i in range(n - 5)]
    a, b = (
        [i for i, x in enumerate(windows) if windows.count(x) > 1][:2]
        if False
        else (lambda c: [i for i, x in enumerate(windows) if c[x] > 1])(
            collections.Counter(windows)
        )
    )

    master = (
        (ROOT / "data" / "liber-primus__transcription--master.txt")
        .read_text()
        .split("%")
    )
    starts, total = {}, 0
    for k in range(15, 71):
        if not RUNE.search(master[k]):
            continue
        c = sum(1 for ch in master[k] if RUNE.match(ch))
        starts[k] = (total, c)
        total += c

    titles = json.loads((ROOT / "experiments" / "rubricated_titles.json").read_text())
    title_pages = {t["page"]: t for t in titles}

    print(f"body: {n:,} runes, {wid[-1] + 1:,} blocks, {len(starts)} chunks\n")
    for label, off in (("first", a), ("second", b)):
        for k, (s, c) in starts.items():
            if s <= off < s + c:
                page = k - 15
                t = title_pages.get(page)
                print(f"{label} occurrence: rune {off}, chunk {k} (page {page})")
                print(
                    f"  chunk offset {off - s} of {c}; "
                    f"{s + c - off - 6} runes left in the chunk"
                )
                print(
                    f"  block {wid[off]}, {wid[n - 1] - wid[off]} blocks left in the body"
                )
                if t:
                    print(
                        f"  rubricated title on this page: {t['runes']} runes in "
                        f"{t['words']} words -> the repeat begins "
                        f"{off - s - t['runes']} runes after it ends"
                    )
                else:
                    print("  no rubricated title on this page")
        print()

    print("how surprising, for a randomly placed 2-block unit:")
    print(
        f"  landing in the final six runes:            {6 / (n - 5):.5f}"
        f"  (1 in {(n - 5) / 6:,.0f})"
    )
    blocks = wid[-1] + 1
    print(
        f"  landing in the first five blocks of one of"
        f"\n  the {len(title_pages)} rubricated-title pages:            "
        f"{len(title_pages) * 5 / blocks:.4f}  "
        f"(1 in {blocks / (len(title_pages) * 5):,.0f})"
    )
    print(
        "\nBoth occurrences sit where a scribe would put a refrain: one near the opening"
        "\nof a titled section, one as the last words of the enciphered book. That is what"
        "\na deliberate repeat looks like, and it is not what a coincidence looks like --"
        "\nbut both positions were noticed after the fact and neither was predicted."
    )


if __name__ == "__main__":
    main()
