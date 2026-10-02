# ABOUTME: Shared loader for the clean LP corpus (sections 0-9 of page0-56.txt):
# ABOUTME: rune-index stream + per-rune word ids, used by the obs_*.py scripts.
"""One source of truth for corpus tokenization so every observation script
measures the same 12,956-rune / 2,928-word clean stream.

Clean corpus = sections 0-9 (excludes the solved AN END page and the plaintext
Parable). Word boundaries: `- . % & $`; line wraps `/` and newlines are NOT
boundaries (words flow across them).

One caveat on `%`: it is a page break, and in 34 of the 55 page breaks a rune stands
immediately before it, so the default tokenization cuts a block there. See
`load_clean(join_pages=True)` and `page-breaks-cut-blocks.md`.
"""

from __future__ import annotations

import re
from pathlib import Path

from aldegonde import c3301
from aldegonde.c3301 import CICADA_ALPHABET as ALPHABET

ROOT = Path(__file__).resolve().parent.parent
RUNE = re.compile(r"[ᚠ-᛿]")
IDX = {r: i for i, r in enumerate(ALPHABET)}
N = 29


def load_clean(*, join_pages: bool = False) -> tuple[list[int], list[int]]:
    """Return (stream, word_id): rune indices and the word each rune belongs to.

    `join_pages` controls what happens at a page break. `%` is in
    `c3301.WORD_BOUNDARY`, so by default it ends a block even where no separator was
    written -- and in 34 of the 55 page breaks a rune stands immediately before the
    `%`, so the block is cut in two. The evidence that those are cuts rather than
    real short blocks is in `page-breaks-cut-blocks.md`: the first block after such a
    break is 1 rune 28% of the time and 2 runes 38% of the time, against 3.4% and
    15.9% for blocks at large, while after the 21 breaks that DO follow a separator
    the first block is ordinary (mean 4.00, 1 rune 5.9% of the time).

    Passing True treats a page break like a line wrap when no separator was written,
    giving 2,894 blocks instead of 2,928. The default is False so that every number
    recorded before this option existed still reproduces.
    """
    text = (ROOT / "data" / "page0-56.txt").read_text()
    sections = [s for s in text.split("$") if RUNE.search(s)][:10]
    stream: list[int] = []
    word_id: list[int] = []
    w = 0
    for s in sections:
        started = False
        for ch in s:
            if RUNE.match(ch):
                stream.append(IDX[ch])
                word_id.append(w)
                started = True
            elif ch == "%" and join_pages:
                pass  # a page break mid-block is a wrap, not a boundary
            elif ch in c3301.WORD_BOUNDARY:
                if started:
                    w += 1
                    started = False
            # '/' and newline: line wrap, not a boundary
        if started:
            w += 1
    return stream, word_id


if __name__ == "__main__":
    stream, wid = load_clean()
    nwords = wid[-1] + 1
    doublets = sum(1 for i in range(len(stream) - 1) if stream[i] == stream[i + 1])
    print(f"clean corpus: {len(stream)} runes, {nwords} words, {doublets} doublets")
