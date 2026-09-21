# ABOUTME: Recovers the keys of the LP's solved pages from their own ciphertext, giving
# ABOUTME: the project a ground-truth testbed of real LP ciphertext instead of simulations.
"""Every positive control in this project is a simulation. This one is not.

Scorers, batteries and key searches here are validated by enciphering prose with a
PLANTED key and checking the pipeline recovers it. That tests the pipeline against
the model it already assumes. It cannot catch a tokenization error, a register
mismatch, or a scorer that is blind to real LP text, because the ciphertext was
manufactured by the same code being tested.

The LP's front pages are real text, transcribed with the ASCII '.' delimiter where
later pages use the 4/10/13-dot glyphs. That is a TRANSCRIPTION convention and says
nothing about whether a page is solved, which is what this script establishes by
scoring each page as runeglish and trying a small key family:

    identity, Atbash, all 29 shifts, and Atbash composed with a shift either way

The result: six of the fifteen '.' pages (3, 8, 9, 10, 11, 14) are already PLAINTEXT
in the transcription -- "identity" wins by 3 nats per rune and page 8 reads "THE LOSS
OF DIUINITY THE CIRCUMFERENCE PRACTICES THREE BEHAUIARS..." -- and the other nine are
still enciphered and are NOT cracked by this family.

That matters twice over. It supplies six pages of genuine LP plaintext to calibrate
against, and it corrects `marks-are-not-clause-punctuation.md`, which had treated all
fifteen as a solved-page control.

The point is not to re-solve anything. It is to know which pages are plaintext before
using them as a control.

    python solved_page_testbed.py [--top 3]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
M = 29
ALPHABET = c3301.CICADA_ALPHABET
IDX = {r: i for i, r in enumerate(ALPHABET)}


def solved_pages() -> list[tuple[int, list[int]]]:
    """(page number, rune indices) for the pages using the '.' convention."""
    out = []
    for n, page in enumerate(MASTER.read_text().split("%")):
        if "." not in page:
            continue
        runes = [IDX[c] for c in page if RUNE.match(c)]
        if runes:
            out.append((n, runes))
    return out


def candidates():
    """(name, map) for every key in the family, as a length-29 substitution."""
    keys = [("identity", list(range(M)))]
    keys.append(("atbash", [(M - 1 - i) % M for i in range(M)]))
    for s in range(1, M):
        keys.append((f"shift+{s}", [(i + s) % M for i in range(M)]))
    for s in range(M):
        keys.append(
            (f"atbash then shift+{s}", [((M - 1 - i) + s) % M for i in range(M)])
        )
        keys.append(
            (f"shift+{s} then atbash", [(M - 1 - ((i + s) % M)) % M for i in range(M)])
        )
    return keys


def score(runes: list[int]) -> float:
    """Runeglish quadgram score per rune, so pages of different length compare."""
    text = "".join(ALPHABET[r] for r in runes)
    return c3301.quadgramscore(text) / max(1, len(runes))


def main() -> None:
    top = 3
    for i, a in enumerate(sys.argv):
        if a == "--top" and i + 1 < len(sys.argv):
            top = int(sys.argv[i + 1])

    pages = solved_pages()
    keys = candidates()
    print(f"{len(pages)} solved pages, {len(keys)} candidate keys\n")
    print(
        f"{'page':>5}{'runes':>7}  {'best key':<24}{'score':>9}{'runner-up':>10}{'gap':>8}"
    )
    hits = 0
    for n, runes in pages:
        scored = sorted(
            ((score([k[r] for r in runes]), name) for name, k in keys), reverse=True
        )
        best, second = scored[0], scored[1]
        gap = best[0] - second[0]
        flag = " <-" if gap > 0.05 else ""
        hits += gap > 0.05
        print(
            f"{n:>5}{len(runes):>7}  {best[1]:<24}{best[0]:>9.3f}"
            f"{second[0]:>10.3f}{gap:>8.3f}{flag}"
        )
    print(f"\n{hits} of {len(pages)} pages separate from their runner-up by > 0.05")
    if top:
        print("\nplaintext head of each clear hit:")
        for n, runes in pages:
            scored = sorted(
                ((score([k[r] for r in runes]), name) for name, k in keys), reverse=True
            )
            if scored[0][0] - scored[1][0] <= 0.05:
                continue
            name = scored[0][1]
            k = dict(keys)[name]
            plain = "".join(ALPHABET[k[r]] for r in runes[:40])
            print(f"  page {n:>2} [{name}]: {plain}")
            print("           -> ", end="")
            c3301.print_english(plain)


if __name__ == "__main__":
    main()
