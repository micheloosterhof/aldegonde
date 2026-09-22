# ABOUTME: Tests the surviving reading that the body's scribe or exemplar differs, using
# ABOUTME: line measure and mark inventory, and finds the encipherment confound instead.
"""Only the body joins short units. Is the body written by a different hand?

`joining_is_not_preparation.py` killed the reading that joining is a preparation step for
enciphering: pages prepared for a monoalphabetic substitution, an interrupted Vigenere
and a prime running key all keep the ordinary 2-rune rate. What survives is that the
body's scribe or exemplar differs -- or that the deficit is not joining at all.

A different hand should show in more than word lengths. Two scribal features are in the
transcription: how long the lines are, and which marks end a block.

The obvious confound has to be handled first. Enciphered text has no word shapes to break
on, so a scribe fills to a measure; plaintext breaks at sentence ends. Any comparison of
the body against the front matter must therefore compare against the front matter's
ENCIPHERED pages, not its plaintext ones.

Paragraph-final lines are dropped throughout, since they are short by construction.

    python does_the_body_have_a_different_hand.py
"""

from __future__ import annotations

import collections
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
LINE = re.compile(r"[/\n]+")


def register():
    spec = importlib.util.spec_from_file_location(
        "lp_plaintext_register", ROOT / "experiments" / "lp_plaintext_register.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def non_final_lines(chunk: str) -> list[int]:
    lines = [len(RUNE.findall(x)) for x in LINE.split(chunk) if RUNE.search(x)]
    return lines[:-1] if len(lines) > 1 else []


def terminating_marks(text: str) -> collections.Counter:
    out, cur = [], 0
    for ch in text:
        if RUNE.match(ch):
            cur += 1
        elif ch in "/\n":
            continue
        elif ch in c3301.WORD_BOUNDARY and cur:
            out.append(ch)
            cur = 0
    return collections.Counter(out)


def main() -> None:
    mod = register()
    chunks = mod.MASTER.read_text().split("%")
    ciphers = {t["page"]: t["cipher"] for t in json.loads(mod.TRIPLES.read_text())}

    groups: dict[str, list[int]] = collections.defaultdict(list)
    for n in range(15):
        label = ("front: plaintext" if n in mod.PLAIN_PAGES
                 else f"front: {ciphers.get(n, 'unknown')}")
        groups[label] += non_final_lines(chunks[n])
    for n in range(15, 71):
        groups["THE BODY"] += non_final_lines(chunks[n])

    print("runes per line, paragraph-final lines dropped\n")
    print(f"{'group':<32}{'lines':>7}{'mean':>9}{'sd':>8}")
    for key in ("front: plaintext", "front: monoalphabetic",
                "front: interrupted vigenere", "THE BODY"):
        v = np.array(groups[key], float)
        if len(v) < 4:
            continue
        print(f"{key:<32}{len(v):>7}{v.mean():>9.2f}{v.std():>8.2f}")

    plain = np.array(groups["front: plaintext"], float)
    keyed = np.array(
        groups["front: monoalphabetic"] + groups["front: interrupted vigenere"], float
    )
    body = np.array(groups["THE BODY"], float)

    def z(a, b):
        return (b.mean() - a.mean()) / math.sqrt(a.var() / len(a) + b.var() / len(b))

    print(f"\nfront plaintext vs front enciphered : z = {z(plain, keyed):+.2f}")
    print(f"front enciphered vs the body        : z = {z(keyed, body):+.2f}")
    print(
        "\nThe spread tightens monotonically -- 6.49, then 2.96 for the enciphered front"
        "\nmatter, then 2.32 for the body -- which is the confound doing its work."
        "\nEnciphered text has no word shapes to break on, so the scribe fills to a"
        "\nmeasure; plaintext breaks where the sentence does."
        "\n\nAgainst the right comparison the body's lines are 1.6 runes longer than the"
        "\nenciphered front matter's, about 8%. Real at six sigma on 539 lines against 83,"
        "\nand far smaller than the front-against-body gap suggests."
    )

    front_marks = terminating_marks("\n".join(chunks[:15]))
    body_marks = terminating_marks("\n".join(chunks[15:71]))
    na, nb = sum(front_marks.values()), sum(body_marks.values())
    print(f"\n\nmarks that end a block: {na:,} in the front matter, {nb:,} in the body\n")
    print(f"{'mark':>7}{'front':>9}{'body':>9}{'front %':>10}{'body %':>9}")
    for k in sorted(set(front_marks) | set(body_marks),
                    key=lambda k: -(front_marks[k] + body_marks[k])):
        if front_marks[k] + body_marks[k] < 5:
            continue
        print(f"{k!r:>7}{front_marks[k]:>9}{body_marks[k]:>9}"
              f"{front_marks[k] / na:>10.4f}{body_marks[k] / nb:>9.4f}")
    print(
        "\nThis one cannot be read as a scribal difference. The front matter uses '.' and"
        "\nnever a circled numeral; the body uses circled numerals and never '.'. Those"
        "\nare the same manuscript feature under two TRANSCRIPTION conventions -- the"
        "\ncircled numeral records a dot count that the '.' does not"
        "\n(`marks-are-not-one-glyph`). Comparing them measures the transcriber."
        "\n\nWhat is comparable is the rate: 12.5% of front-matter blocks end in a dot mark"
        "\nagainst 5.7% in the body. That is a real difference and an ordinary one -- the"
        "\nfront matter is short instructional paragraphs and the body is continuous text."
    )


if __name__ == "__main__":
    main()
