# ABOUTME: Maps each rubricated rune-span to its transcription: word-length pattern,
# ABOUTME: ciphertext and section, giving the candidate-crib list for the (g,sigma) route.
"""Turn the rubricated rune-spans into candidate cribs.

`rubrication_spans.py` finds the red rune-spans; this aligns each to its
transcription line and reads off what a crib needs: the word-length pattern (to
match against Cicada phrases the way DIVINITY WITHIN = [8, 5] was matched) and
the ciphertext (garbage transliteration confirms the span is enciphered, not the
plaintext Parable). On page 0 the rubricated title is DIVINITY WITHIN, delimited
by the 13-dot section mark that follows it -- the rubricated spans are SECTION
TITLES, each a short titular phrase whose plaintext may be guessable.

Words are maximal runs of rune characters; every non-rune (the circled-numeral
separators, marks, wraps) is a boundary. The span is the leading whole words that
cover the red-rune count.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402, I001
from mark_type_split import CORPUS, line_bands, page_glyphs  # noqa: E402
from rubrication_spans import lines_from_rows, red_rune_rows  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ALPHA = c3301.CICADA_ALPHABET
ENG = c3301.CICADA_ENGLISH_ALPHABET
I2 = {r: i for i, r in enumerate(ALPHA)}


def tr(runes: str) -> str:
    return "".join(ENG[I2[c]] for c in runes if c in I2)


def red_rows_and_counts(page: int) -> list[tuple[int, int]]:
    return [(y, n) for y, n in lines_from_rows(red_rune_rows(page)) if n >= 3]


def line_words(text: str) -> list[str]:
    """Maximal rune-runs = words; every non-rune char is a separator."""
    return "".join(c if RUNE.match(c) else " " for c in text).split()


def span_words(words: list[str], red_count: int) -> list[str]:
    """Leading whole words covering ~red_count runes (allow the red count to be
    one short, as the initial or a merged rune is often miscounted)."""
    out, acc = [], 0
    for w in words:
        if acc >= red_count:
            break
        out.append(w)
        acc += len(w)
    return out


def main() -> None:
    blocks = CORPUS.read_text().split("%")
    print(
        "rubricated section-title crib candidates (word-length pattern + ciphertext):\n"
    )
    # spans in the plaintext Parable (section 11) transliterate to readable English
    plain_words = ("PARABLE", "INSTAR", "DIVINITY", "WITHIN", "EMERGE", "SURFACE")
    print(f"{'page':>4}  {'pattern':>16}  {'transliteration':<34}note")
    cands = 0
    for page in range(58):
        lines = [ln for ln in blocks[page].split("\n") if RUNE.search(ln)]
        reds = red_rows_and_counts(page)
        if not reds:
            continue
        gs = page_glyphs(page)
        bands = line_bands(gs, len(lines))
        if len(bands) != len(lines):
            print(f"{page:>4}  (band/line mismatch -- needs the reader; skipped)")
            continue
        band_y = [min(g[1] for g in b) for b in bands]
        for ry, n in reds:
            i = min(range(len(band_y)), key=lambda k: abs(band_y[k] - ry))
            words = span_words(line_words(lines[i]), n)
            pat = [len(w) for w in words]
            cipher = tr("".join(words))
            note = (
                "PLAINTEXT (Parable)"
                if any(w in cipher for w in plain_words)
                else "crib candidate"
            )
            print(f"{page:>4}  {str(pat):>16}  {cipher:<34}{note}")
            cands += 1
    print(f"\n{cands} candidate section-title cribs. page 0 = [8, 5] DIVINITY WITHIN.")
    print("Next: match each pattern to Cicada titular phrases; confirmed ones feed")
    print(
        "crib_divinity_within's (g, sigma) constraints, and the key-free d5 reads prune."
    )


if __name__ == "__main__":
    main()
