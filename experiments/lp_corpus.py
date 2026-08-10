# ABOUTME: Shared loader for the clean LP corpus (sections 0-9 of page0-58.txt):
# ABOUTME: rune-index stream + per-rune word ids, used by the obs_*.py scripts.
"""One source of truth for corpus tokenization so every observation script
measures the same 12,956-rune / 2,928-word clean stream.

Clean corpus = sections 0-9 (excludes the solved AN END page and the plaintext
Parable). Word boundaries: `- . % & $`; line wraps `/` and newlines are NOT
boundaries (words flow across them).
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


def load_clean() -> tuple[list[int], list[int]]:
    """Return (stream, word_id): rune indices and the word each rune belongs to."""
    text = (ROOT / "data" / "page0-58.txt").read_text()
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
