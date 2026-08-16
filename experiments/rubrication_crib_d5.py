# ABOUTME: Reads the key-free d5 plaintext-equality pattern of each rubricated span
# ABOUTME: word (length >=6) and prunes it to dictionary candidates -- crib step 1.
"""Constrain the rubricated section-title cribs with the key-free d5 channel.

`rubrication_cribs.py` lists the rubricated section-title spans and their word
patterns. Within any word, c[j] == c[j+5] <=> p[j] == p[j+5] with no key
(`d5_crib_targets.py`), so every span word of length >= 6 carries free
plaintext-equality facts. Requiring a dictionary word to satisfy every d5
equality and inequality prunes the candidates for that title word -- narrowing
the guess a crib match needs, before any (g, sigma) work.

Caveat (from d5_crib_targets.py): the counts are ordinary and the LP's titular
vocabulary is philosophical, so a candidate list is a LEAD, not an answer, and an
empty list means the true word is outside a frequency-ranked English dictionary,
not that the span is invalid.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402, I001
from d5_crib_targets import d5_constraints, dictionary  # noqa: E402
from mark_type_split import CORPUS, line_bands, page_glyphs  # noqa: E402
from rubrication_cribs import line_words, red_rows_and_counts, span_words  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ALPHA = c3301.CICADA_ALPHABET
IDX = {r: i for i, r in enumerate(ALPHA)}
SHOW = 12


def candidate_span_words() -> list[tuple[int, list[int]]]:
    """(page, ciphertext rune indices) for every rubricated span word, in order."""
    blocks = CORPUS.read_text().split("%")
    out: list[tuple[int, list[int]]] = []
    for page in range(58):
        lines = [ln for ln in blocks[page].split("\n") if RUNE.search(ln)]
        reds = red_rows_and_counts(page)
        if not reds:
            continue
        bands = line_bands(page_glyphs(page), len(lines))
        if len(bands) != len(lines):
            continue
        band_y = [min(g[1] for g in b) for b in bands]
        for ry, n in reds:
            i = min(range(len(band_y)), key=lambda k: abs(band_y[k] - ry))
            for w in span_words(line_words(lines[i]), n):
                out.append((page, [IDX[r] for r in w]))
    return out


def main() -> None:
    vocab = dictionary()
    print("d5 pruning of rubricated section-title words (length >= 6):\n")
    total_constrained = 0
    for page, word in candidate_span_words():
        if len(word) < 6:
            continue
        equal, unequal = d5_constraints(word)
        if not equal:
            continue  # no d5 equality -> this channel adds nothing here
        total_constrained += 1
        fits = sorted(
            (
                (f, eng)
                for runes, eng, f in vocab.get(len(word), [])
                if all(runes[a] == runes[b] for a, b in equal)
                and all(runes[a] != runes[b] for a, b in unequal)
            ),
            reverse=True,
        )
        cipher = "".join(ALPHA[r] for r in word)
        needs = ", ".join(f"p{a}=p{b}" for a, b in equal)
        listed = ", ".join(eng for _f, eng in fits[:SHOW]) or "-- none in dict"
        print(f"page {page:>2}  L={len(word):<2} {cipher}  ({needs})")
        print(f"        {len(fits)} candidates: {listed}")
    print(
        f"\n{total_constrained} span words carry a d5 equality. Empty lists mean the"
        "\ntitle word is outside a frequency-ranked dictionary (expected for LP"
        " vocabulary),\nnot that the span is wrong. Words with a short list are the"
        " leads to match by hand."
    )


if __name__ == "__main__":
    main()
