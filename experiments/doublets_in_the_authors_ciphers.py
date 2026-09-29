# ABOUTME: Compares the body's doublet deficit against the author's own plaintext and his
# ABOUTME: own solved ciphertexts, to see whether any of them suppresses adjacent repeats.
"""The body suppresses adjacent repeats. Does anything else the author wrote?

`doublet-deficit-is-global.md` establishes that the body's deficit is uniform across
word boundaries, so it constrains neither `g` nor `sigma`. What it has never been
measured against is the author's own output. Three things could produce a low doublet
rate and only one of them is interesting:

  the language   runeglish has fewer doubled letters than English, since LL and SS and
                 EE are common but TH, EA, NG and OE collapse to single runes
  a weak cipher  a monoalphabetic substitution maps doublets to doublets, so it
                 inherits the plaintext rate exactly
  the cipher     a rule that inspects its own output and refuses to repeat

The book supplies all three as controls: six plaintext pages, five monoalphabetic ones,
four interrupted Vigenere, one prime running key. A Vigenere is the decisive one -- its
key changes between adjacent positions, so a plaintext doublet does NOT become a
ciphertext doublet and the rate should return to 1/29 whatever the language does.

    python doublets_in_the_authors_ciphers.py
"""

from __future__ import annotations

import collections
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402
from fingerprint_battery import lp_words  # noqa: E402
from lp_corpus import load_clean  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
M = 29
CHANCE = 1 / M


def report(seq, label: str, words=None) -> None:
    n = len(seq)
    doublets = sum(1 for i in range(n - 1) if seq[i] == seq[i + 1])
    counts = collections.Counter(seq)
    ioc = sum(v * (v - 1) for v in counts.values()) / (n * (n - 1)) * M
    rate = doublets / (n - 1)
    se = math.sqrt(CHANCE * (1 - CHANCE) / (n - 1))
    seam = ""
    if words:
        pairs = [(a, b) for a, b in zip(words, words[1:]) if a and b]
        if pairs:
            hits = sum(1 for a, b in pairs if a[-1] == b[0])
            seam = f"{hits / len(pairs):.4f}"
    print(
        f"{label:<32}{n:>8,}{doublets:>6}{rate:>9.4f}{(rate - CHANCE) / se:>+8.2f}"
        f"{ioc:>8.3f}{seam:>9}"
    )


def words_of_page(text: str) -> list[list[int]]:
    out, cur = [], []
    for ch in text:
        if RUNE.match(ch):
            cur.append(IDX[ch])
        elif ch in "/\n":
            continue
        elif cur and ch in c3301.WORD_BOUNDARY:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def main() -> None:
    master = (ROOT / "data" / "liber-primus__transcription--master.txt").read_text()
    chunks = master.split("%")
    triples = json.loads(
        (ROOT / "experiments" / "solved_page_triples.json").read_text()
    )
    spec = importlib.util.spec_from_file_location(
        "lp_plaintext_register", ROOT / "experiments" / "lp_plaintext_register.py"
    )
    reg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reg)

    groups: dict[str, list[int]] = collections.defaultdict(list)
    wordsets: dict[str, list[list[int]]] = collections.defaultdict(list)
    for x in triples:
        page = chunks[x["page"]]
        groups[x["cipher"]] += [IDX[ch] for ch in RUNE.findall(page)]
        wordsets[x["cipher"]] += words_of_page(page)

    print(
        f"{'text':<32}{'runes':>8}{'dbl':>6}{'d1 rate':>9}{'z':>8}{'IoC':>8}{'seam':>9}"
    )
    print(
        f"{'chance':<32}{'':>8}{'':>6}{CHANCE:>9.4f}{0.0:>+8.2f}{1.0:>8.3f}"
        f"{CHANCE:>9.4f}"
    )
    plain_words = reg.corpus()
    report([r for w in plain_words for r in w], "the author's plaintext", plain_words)
    for cipher in ("monoalphabetic", "interrupted vigenere", "prime running key"):
        if groups[cipher]:
            short = {
                "monoalphabetic": "monoalphabetic",
                "interrupted vigenere": "interrupted Vigenere",
                "prime running key": "prime running key",
            }[cipher]
            report(groups[cipher], f"his {short}", wordsets[cipher])
    report(load_clean()[0], "THE BODY", lp_words())

    n = len(load_clean()[0])
    expected = (n - 1) * CHANCE
    observed = sum(1 for a, b in zip(load_clean()[0], load_clean()[0][1:]) if a == b)
    print(
        f"\nThe author's plaintext is already below chance -- runeglish collapses TH,"
        f"\nEA, NG and OE, so the doubled letters English is full of do not survive as"
        f"\ndoubled runes. His monoalphabetic ciphertext inherits that rate exactly,"
        f"\nbecause a fixed substitution maps a doublet to a doublet."
        f"\n\nHis Vigenere ciphertext does not. The key changes between adjacent"
        f"\npositions, so a plaintext doublet stops being a ciphertext doublet and the"
        f"\nrate returns to chance. That is the control that matters, and it lands"
        f"\nthere."
        f"\n\nThe body does not. {observed} doublets against {expected:.0f} expected is"
        f"\n{100 * (1 - observed / expected):.0f}% suppression, and nothing else in the"
        f"\nbook is remotely like it. The deficit is not the language and not any cipher"
        f"\nthe author is known to use: something inspects the output and refuses to"
        f"\nrepeat."
    )


if __name__ == "__main__":
    main()
