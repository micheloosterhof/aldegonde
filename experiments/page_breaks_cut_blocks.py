# ABOUTME: Shows that a page break cuts a block in the 34 places where no separator was
# ABOUTME: written, and measures what the corrected tokenization changes.
"""`%` is a page break, and the tokenizer treats it as a word boundary.

`c3301.WORD_BOUNDARY` contains `%`, so `lp_corpus.load_clean` ends a block at every
page break. That is right where the scribe wrote a separator before the page ended and
wrong where he did not -- and in 34 of the 55 breaks a rune stands immediately before
the `%`, so a block that continues onto the next page is counted as two.

The two cases can be told apart without deciding anything in advance: split the page
breaks by whether a separator precedes them, and look at the first block of the next
page. If the break cuts a block, the first block on the new page is a fragment and will
be far shorter than a block should be. If the page genuinely ended at a boundary, it
will be ordinary.

    python page_breaks_cut_blocks.py
"""

from __future__ import annotations

import collections
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from lp_plaintext_register import word_lengths  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")


def blocks_with_page_context():
    """Block lengths, each tagged with the page break it follows, if any."""
    text = (ROOT / "data" / "page0-56.txt").read_text()
    clean = []
    for m in re.finditer("%", text):
        k = m.start() - 1
        while k >= 0 and text[k] in "/\n":
            k -= 1
        clean.append(not RUNE.match(text[k]))
    rows, cur, follows, pending = [], 0, None, None
    seen = -1
    for ch in text:
        if RUNE.match(ch):
            if cur == 0:
                follows = pending
                pending = None
            cur += 1
        elif ch in "/\n":
            continue
        elif ch in c3301.WORD_BOUNDARY:
            if cur:
                rows.append((cur, follows))
                cur, follows = 0, None
            if ch == "%":
                seen += 1
                pending = seen
            else:
                pending = None
    if cur:
        rows.append((cur, follows))
    return rows, clean


def main() -> None:
    rows, clean = blocks_with_page_context()
    lengths = np.array([n for n, _ in rows], float)
    print(
        f"{len(clean)} page breaks: {sum(clean)} with a separator before them, "
        f"{len(clean) - sum(clean)} with a rune\n"
    )

    groups = collections.defaultdict(list)
    for n, follows in rows:
        if follows is not None:
            groups["separator before" if clean[follows] else "rune before"].append(n)
    print(
        f"{'first block of the new page':>30}{'n':>5}{'mean':>8}"
        f"{'1 rune':>9}{'2 runes':>10}"
    )
    for key in ("rune before", "separator before"):
        a = np.array(groups[key], float)
        print(
            f"{key:>30}{len(a):>5}{a.mean():>8.3f}{(a == 1).mean():>9.3f}"
            f"{(a == 2).mean():>10.3f}"
        )
    print(
        f"{'every block':>30}{len(lengths):>5}{lengths.mean():>8.3f}"
        f"{(lengths == 1).mean():>9.3f}{(lengths == 2).mean():>10.3f}"
    )
    print(
        "\nAfter a break with a rune before it the first block is 1 rune eight times as"
        "\noften as a block should be. After a break with a separator before it, it is"
        "\nordinary. So those 34 breaks cut a block; the other 21 do not."
    )

    print("\nWhat the corrected tokenization changes:\n")
    author = word_lengths()
    af2 = sum(1 for x in author if x == 2) / len(author)
    ase = math.sqrt(af2 * (1 - af2) / len(author))
    print(
        f"{'parse':<26}{'blocks':>8}{'mean':>8}{'frac 2':>9}{'seam':>9}"
        f"{'d1 within':>11}{'z vs author':>13}"
    )
    for join in (False, True):
        stream, wid = load_clean(join_pages=join)
        words = [[] for _ in range(wid[-1] + 1)]
        for rune, w in zip(stream, wid):
            words[w].append(rune)
        lens = np.array([len(w) for w in words], float)
        seam = sum(1 for a, b in zip(words, words[1:]) if a and b and a[-1] == b[0]) / (
            len(words) - 1
        )
        hits = pairs = 0
        for w in words:
            for i in range(len(w) - 1):
                pairs += 1
                hits += w[i] == w[i + 1]
        f2 = float((lens == 2).mean())
        se = math.sqrt(f2 * (1 - f2) / len(lens))
        label = "joined at page breaks" if join else "as recorded everywhere"
        print(
            f"{label:<26}{len(lens):>8,}{lens.mean():>8.3f}{f2:>9.4f}{seam:>9.4f}"
            f"{hits / pairs:>11.4f}"
            f"{(f2 - af2) / math.sqrt(se**2 + ase**2):>+13.2f}"
        )
    print(
        "\nThe correction moves every block-level number by about one percent and makes"
        "\nthe hole at length 2 deeper, not shallower. `load_clean` takes join_pages to"
        "\nselect it; the default stays as it was so that recorded numbers reproduce."
    )


if __name__ == "__main__":
    main()
