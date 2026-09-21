# ABOUTME: Tests whether the body could be short-keyed per page or per section, pooling the
# ABOUTME: per-page IoC so a weak individual test becomes a strong aggregate one.
"""Could the body rekey per page, the way the front matter rekeys per page group?

`alphabet_count_bound.py` shows the body needs ~950 alphabets if one key covers it.
The obvious reply is that the body need not use one key: the solved front matter
changes key between page groups, so the body might rekey per page or per section,
leaving every stretch short-keyed while the pooled index of coincidence goes flat.

That reply is testable, because rekeying does not flatten a page's OWN IoC. A page
enciphered under a length-L key sits at 1 + (I_p - 1)/L whatever the neighbouring
pages use. Measuring each page separately is weak -- 250 runes give an IoC standard
error near 0.03 -- but the pages can be pooled, and 49 of them turn that into 0.0044.

    python per_page_key_bound.py [--draws 600]
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

from aldegonde import c3301
from aldegonde.stats import ioc

ROOT = Path(__file__).resolve().parent.parent
RUNE = re.compile(r"[ᚠ-᛿]")
M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
I_P = 1.788  # the author's own plaintext, lp-plaintext-register.md
MIN_RUNES = 150


def units(split: str) -> list[list[int]]:
    text = (ROOT / "data" / "page0-56.txt").read_text()
    out = []
    for chunk in text.split(split):
        runes = [IDX[c] for c in chunk if RUNE.match(c)]
        if len(runes) >= MIN_RUNES:
            out.append(runes)
    return out


def main() -> None:
    draws = 600
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])
    rng = random.Random(3301)

    for split, name in (("$", "section"), ("%", "page")):
        chunks = units(split)
        obs = sum(ioc(c) * M for c in chunks) / len(chunks)
        sims = []
        for _ in range(draws):
            sims.append(
                sum(ioc([rng.randrange(M) for _ in range(len(c))]) * M for c in chunks)
                / len(chunks)
            )
        mu = sum(sims) / len(sims)
        sd = (sum((x - mu) ** 2 for x in sims) / len(sims)) ** 0.5
        print(
            f"{len(chunks)} {name}s, {sum(len(c) for c in chunks):,} runes: "
            f"mean IoC {obs:.4f} vs flat {mu:.4f} +- {sd:.4f}, z = {(obs - mu) / sd:+.2f}"
        )
        if name == "page":
            print(f"\n  a fresh key on every {name} would have to be:")
            print(f"  {'L':>5}{'mean IoC':>11}{'z':>9}")
            for length in (8, 13, 20, 40, 80):
                pred = 1 + (I_P - 1) / length
                print(f"  {length:>5}{pred:>11.4f}{(pred - mu) / sd:>+9.1f}")
            floor = (I_P - 1) / (mu + 3 * sd - 1)
            print(
                f"\n  smallest per-{name} key not excluded at 3 sigma: {floor:.0f} runes"
            )
        print()


if __name__ == "__main__":
    main()
