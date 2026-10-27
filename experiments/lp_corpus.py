# ABOUTME: Shared loader for the clean LP corpus (sections 0-9 of page0-56.txt):
# ABOUTME: a thin wrapper over c3301.tokenize so every script measures one stream.
"""One source of truth for corpus tokenization so every observation script
measures the same 12,956-rune / 2,928-word clean stream.

Clean corpus = sections 0-9 of `data/page0-56.txt`. The tokenization rules live
in `aldegonde.c3301.tokenize`; this module only supplies the file and the
section selection. Word boundaries: the marks, `% & $`, numerals and quotes;
line wraps `/` and newlines are NOT boundaries (words flow across them).

One caveat on `%`: it is a page break, and in 34 of the 55 page breaks a rune
stands immediately before it, so the default tokenization cuts a block there.
See `load_clean(join_pages=True)` and `page-breaks-cut-blocks.md`.
"""

from __future__ import annotations

from pathlib import Path

from aldegonde import c3301
from aldegonde.c3301 import CICADA_ALPHABET as ALPHABET

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-56.txt"
IDX = {r: i for i, r in enumerate(ALPHABET)}
N = 29
CLEAN_SECTIONS = range(10)


def load_tokenized(*, join_pages: bool = False) -> c3301.Tokenized:
    """The clean corpus with word, line, page and section ids per rune.

    `join_pages` controls what happens at a page break. `%` is in
    `c3301.WORD_BOUNDARY`, so by default it ends a block even where no separator
    was written -- and in 34 of the 55 page breaks a rune stands immediately
    before the `%`, so the block is cut in two. The evidence that those are cuts
    rather than real short blocks is in `page-breaks-cut-blocks.md`: the first
    block after such a break is 1 rune 28% of the time and 2 runes 38% of the
    time, against 3.4% and 15.9% for blocks at large, while after the 21 breaks
    that DO follow a separator the first block is ordinary (mean 4.00, 1 rune
    5.9% of the time).

    Passing True treats a page break like a line wrap when no separator was
    written, giving 2,896 blocks instead of 2,928. The default is False so that
    every number recorded before this option existed still reproduces.
    """
    text = CORPUS.read_text(encoding="utf-8")
    return c3301.tokenize(text, join_pages=join_pages, sections=CLEAN_SECTIONS)


def load_clean(*, join_pages: bool = False) -> tuple[list[int], list[int]]:
    """Return (stream, word_id): rune indices and the word each rune belongs to."""
    tok = load_tokenized(join_pages=join_pages)
    return tok.stream, tok.word


def load_words(*, join_pages: bool = False) -> list[list[int]]:
    """The clean corpus cut into words of rune indices."""
    return load_tokenized(join_pages=join_pages).words()


if __name__ == "__main__":
    stream, wid = load_clean()
    nwords = wid[-1] + 1
    doublets = sum(1 for i in range(len(stream) - 1) if stream[i] == stream[i + 1])
    print(f"clean corpus: {len(stream)} runes, {nwords} words, {doublets} doublets")
