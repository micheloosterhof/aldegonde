# ABOUTME: Tests whether the body's joining of short units tracks how hard the page's
# ABOUTME: cipher is, which would make it a preparation step, and finds it does not.
"""Only the body joins short units. Is that because the body's cipher is the hard one?

`short-units-are-written-joined.md` explains the body's block lengths by joining about
40% of 2-rune units to the unit before them, and records that the front matter does not
do it. Three readings were offered for that, of which the one fitting the book's pattern
without needing a second hand was:

    the joining is part of the ENCIPHERING, done when the plaintext was prepared rather
    than when it was composed

That is testable. The book escalates its cipher page by page -- plaintext, then
monoalphabetic, then interrupted Vigenere, then, after the body, a prime running key. If
joining is preparation, it should appear on the pages prepared for a keyed cipher and not
on the plain ones.

Word lengths are available for all sixteen solved pages, since every one is
position-aligned (`register_is_bigger.py`).

    python joining_is_not_preparation.py
"""

from __future__ import annotations

import collections
import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import lp_words  # noqa: E402

ORDER = (
    "plaintext (no cipher)",
    "monoalphabetic",
    "interrupted vigenere",
    "prime running key",
)


def register():
    spec = importlib.util.spec_from_file_location(
        "lp_plaintext_register", ROOT / "experiments" / "lp_plaintext_register.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    mod = register()
    pages = mod.MASTER.read_text().split("%")
    triples = json.loads(mod.TRIPLES.read_text())

    groups: dict[str, list[int]] = collections.defaultdict(list)
    counts: collections.Counter = collections.Counter()
    per_page = {}
    for n in mod.PLAIN_PAGES:
        w = mod.words_of(pages[n])
        if w:
            groups["plaintext (no cipher)"] += [len(x) for x in w]
            counts["plaintext (no cipher)"] += 1
    for t in triples:
        key = t["key"] if t["cipher"] == "monoalphabetic" else None
        w = mod.words_of(pages[t["page"]], key)
        if w:
            lengths = [len(x) for x in w]
            groups[t["cipher"]] += lengths
            counts[t["cipher"]] += 1
            per_page[t["page"]] = (t["cipher"], lengths)

    body = [len(w) for w in lp_words()]
    bf = sum(1 for x in body if x == 2) / len(body)
    bse = math.sqrt(bf * (1 - bf) / len(body))

    print("fraction of 2-rune units, by how the page is enciphered\n")
    print(f"{'cipher':<24}{'pages':>7}{'words':>7}{'frac 2':>9}{'se':>8}"
          f"{'z vs the body':>15}")
    for cipher in ORDER:
        lengths = groups[cipher]
        if not lengths:
            continue
        f = sum(1 for x in lengths if x == 2) / len(lengths)
        se = math.sqrt(f * (1 - f) / len(lengths))
        print(f"{cipher:<24}{counts[cipher]:>7}{len(lengths):>7}{f:>9.4f}{se:>8.4f}"
              f"{(bf - f) / math.sqrt(se**2 + bse**2):>15.2f}")
    enciphered = [x for c in ORDER[1:] for x in groups[c]]
    f = sum(1 for x in enciphered if x == 2) / len(enciphered)
    se = math.sqrt(f * (1 - f) / len(enciphered))
    print(f"{'ALL enciphered pages':<24}{'':>7}{len(enciphered):>7}{f:>9.4f}{se:>8.4f}"
          f"{(bf - f) / math.sqrt(se**2 + bse**2):>15.2f}")
    print(f"{'THE BODY':<24}{'':>7}{len(body):>7}{bf:>9.4f}{bse:>8.4f}")

    print(
        "\nThere is no gradient. All four groups sit between 0.22 and 0.32, within each"
        "\nother's errors and around the 0.2422 median of twenty-two English registers."
        "\nPooled, the 492 words on enciphered front-matter pages read 0.2337 against the"
        "\nbody's 0.1588, z = -3.70."
        "\n\nSo joining is NOT a preparation step. Pages prepared for a monoalphabetic"
        "\nsubstitution, for an interrupted Vigenere and for a prime running key all keep"
        "\nthe ordinary rate. Only the body joins, and being enciphered is not what"
        "\ndistinguishes it."
        "\n\nThe AN END page is the sharpest single case -- the hardest cipher the author"
        f"\never solved, and it reads {sum(1 for x in per_page[71][1] if x == 2) / len(per_page[71][1]):.3f} on "
        f"{len(per_page[71][1])} words, the highest of any group. Too few words to carry"
        "\nthe argument alone, but it points the same way as the pooled figure."
    )


if __name__ == "__main__":
    main()
