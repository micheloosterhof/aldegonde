# ABOUTME: Builds the LP's own plaintext register from the solved pages and measures the
# ABOUTME: statistics the battery calibrates against, replacing an imported prose corpus.
"""The register this project fits against has never been the LP's own.

Word lengths, letter frequencies and the within-word coincidence profile are all
calibrated here against an outside prose corpus (Pride and Prejudice). That is the
mis-calibration recorded in `battery-register-is-unmatched`, which by itself flipped
three verdicts once it was noticed.

`solved-page-testbed.md` now supplies the alternative: real LP plaintext, in the
author's own runeglish, with the author's own word boundaries.

  six pages plaintext in the transcription     3, 8, 9, 10, 11, 14
  five pages recovered as monoalphabetic       0, 4, 5, 6, 7

Monoalphabetic substitution is position-preserving, so the recovered pages keep their
word boundaries exactly and can be pooled with the plaintext ones. The four Vigenere
pages are excluded here: their interrupts make the plaintext-to-ciphertext position
map non-trivial, and nothing below needs them.

What it measures, all of it feeding models fitted elsewhere in this directory:

  word lengths    the LP's own distribution, which sets every length-matched control
  unigrams        the plaintext frequency table the cipher has to flatten
  d1..d7          the within-word coincidence profile. d1 is the plaintext doublet
                  rate, which is what `quagmire-dodge.md` calls "P(would-be doublet)"
                  and currently takes from prose

    python lp_plaintext_register.py
"""

from __future__ import annotations

import collections
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
TRIPLES = ROOT / "experiments" / "solved_page_triples.json"
RUNE = re.compile(r"[ᚠ-᛿]")
M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
ENG = c3301.CICADA_ENGLISH_ALPHABET
PLAIN_PAGES = (3, 8, 9, 10, 11, 14)


WRAP = "/\n"  # line wrap and newline: words flow across them, as in lp_corpus


def words_of(page: str, key: list[int] | None = None) -> list[list[int]]:
    """Words as rune-index lists. `key` applies a position-preserving substitution.

    Line wraps are NOT word boundaries. `lp_corpus.load_clean` is explicit about this
    and an earlier version of this file split on them, which inflated the 1- and
    2-rune buckets and shortened the words every statistic below is measured over.
    """
    out: list[list[int]] = []
    current: list[int] = []
    for ch in page:
        if RUNE.match(ch):
            r = IDX[ch]
            current.append(key[r] if key else r)
        elif ch in WRAP:
            continue
        elif current:
            out.append(current)
            current = []
    if current:
        out.append(current)
    return out


def corpus() -> list[list[int]]:
    """Every word of authentic LP plaintext available, from both sources."""
    pages = MASTER.read_text().split("%")
    words: list[list[int]] = []
    for n in PLAIN_PAGES:
        words += words_of(pages[n])
    for t in json.loads(TRIPLES.read_text()):
        # only the monoalphabetic triples are position-preserving with a 29-rune
        # key; the Vigenere and running-key ones carry a keystream, not a
        # substitution, and must not be applied here
        if t["cipher"] == "monoalphabetic":
            words += words_of(pages[t["page"]], t["key"])
    return words


def profile(words: list[list[int]], lag: int) -> tuple[int, int]:
    """(matches, pairs) at a within-word distance."""
    hits = pairs = 0
    for w in words:
        for i in range(len(w) - lag):
            pairs += 1
            hits += w[i] == w[i + lag]
    return hits, pairs


def main() -> None:
    words = corpus()
    runes = sum(len(w) for w in words)
    print(f"LP plaintext register: {len(words):,} words, {runes:,} runes\n")

    lens = collections.Counter(len(w) for w in words)
    mean = runes / len(words)
    print(f"word lengths (mean {mean:.2f}):")
    for length in sorted(lens):
        if length <= 12:
            bar = "#" * round(60 * lens[length] / len(words))
            print(
                f"  {length:>2} {lens[length]:>4} {lens[length] / len(words):>6.1%} {bar}"
            )

    flat = collections.Counter(r for w in words for r in w)
    top = sorted(flat.items(), key=lambda kv: -kv[1])[:8]
    print("\ncommonest plaintext runes: " + "  ".join(f"{ENG[i]}={n}" for i, n in top))
    chi = sum((flat[i] - runes / M) ** 2 / (runes / M) for i in range(M))
    print(f"unigram chi2 vs uniform: {chi:.0f} on 28 df (the cipher must flatten this)")

    print(f"\nwithin-word coincidence profile (chance = 1/29 = {1 / M:.4f}):")
    print(f"{'lag':>4}{'matches':>9}{'pairs':>8}{'rate':>9}{'x chance':>10}{'z':>8}")
    for lag in range(1, 8):
        hits, pairs = profile(words, lag)
        if not pairs:
            continue
        rate = hits / pairs
        se = math.sqrt((1 / M) * (1 - 1 / M) / pairs)
        print(
            f"{lag:>4}{hits:>9}{pairs:>8}{rate:>9.4f}{rate * M:>10.2f}"
            f"{(rate - 1 / M) / se:>+8.2f}"
        )
    d1 = profile(words, 1)
    print(
        f"\nThe plaintext doublet rate is {d1[0] / d1[1]:.4f} ({d1[0]}/{d1[1]}), "
        f"{d1[0] / d1[1] * M:.2f}x chance."
    )
    print(
        "quagmire-dodge.md multiplies its 1/5 schedule factor by a 'would-be doublet'"
        "\nrate taken from prose; this is that quantity measured on the LP's own words."
    )


if __name__ == "__main__":
    main()
