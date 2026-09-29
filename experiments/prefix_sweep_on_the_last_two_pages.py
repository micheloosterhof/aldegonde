# ABOUTME: Prefix-scored key sweep, validated on two pages with known answers; the front
# ABOUTME: matter turns out to be fully solved, so this is a tool rather than a result.
"""An interrupted keystream is readable until its first interrupt. Score only that.

**The front matter is already fully solved and this file found nothing new.** All fifteen
chunks are accounted for: six are plaintext in the transcription and nine are in
`experiments/solved_page_triples.json` with their keys. `solved-page-testbed.md` is stale
in two places and says otherwise -- see the corrections below.

What the file leaves behind is a sharper instrument than the sweep already on record, and
two pages of validation for it.

## The idea

`solved_page_keywords.py` scores whole pages. That buries a correct key on an interrupted
keystream: page 1 under plain Vigenere with DIVINITY reads *WELCOME WELCOME PILGRIM TO THE
GREAT JOURNEY TOWARD THE END* for 49 runes and then loses sync, so the page average sits
near a wrong key's.

**Scoring only the leading runes removes the dilution.** A correct key shows at full
plaintext strength whether or not the keystream is later interrupted, and no interrupt
model is needed to find it.

## Validation on two known answers

321 keys from the author's own vocabulary, four families, with and without the
F-interrupt convention, scored on the first 40 runes:

| page | known key | rank found | prefix score | z above the rest |
|---|---|---|---|---|
| 1 | DIVINITY | **1** | -4.786 | +6.30 |
| 12 | FIRFUMFERENFE | **1** | -3.919 | **+7.81** |

Page 12's reading is *A COAN DURNG A LESSON THE MASTER EXPLAINE[D]*, recovered with
interrupt handling switched **off**. Both are the keys already in the triples file.

Page 13 does not surface: its best is EMERGE at -6.295, z = +3.77, and unreadable. It is
solved in the triples file under the same FIRFUMFERENFE keystream continued from page 12,
which a per-page sweep cannot find because the keystream does not restart.

## Two stale claims in `solved-page-testbed.md`

- "a period estimate on those four is cheap and **has not been run**" -- it has, and the
  same file records the result thirty lines later: no period at any k from 1 to 12.
- "Four pages are still enciphered: 1, 2, 12 and 13" -- all four are solved in the same
  file and stored in the triples.

## What this settles about the reference

The motivation was to enlarge the author's plaintext, which is the binding constraint on
almost every result here: `what_would_it_take.py` needs 29 times his solved pages to
establish one arm, and `are_the_headline_numbers_seed_stable.py` shows his 94 spans are
small enough for a single joining draw to flip a sign.

**It cannot be enlarged.** `solved_pages()` already covers chunks 0-14 and 71, block
lengths pass through a length-preserving cipher unchanged, and there is no further LP
plaintext. 94 spans and 719 blocks is the ceiling, so those power limits are permanent
rather than a gap to be filled.

    python prefix_sweep_on_the_last_two_pages.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from solved_page_keywords import (  # noqa: E402
    FAMILIES,
    decrypt,
    key_runes,
    score,
    vocabulary,
)

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
ALPHABET = c3301.CICADA_ALPHABET
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET
IDX = {r: i for i, r in enumerate(ALPHABET)}
VOCAB = ROOT / "data" / "register_vocab.txt"
PREFIX = 40
TARGETS = (12, 13)
CONTROL = 1
SHOW = 6


def runes_of(page: int) -> list[int]:
    chunks = MASTER.read_text().split("%")
    return [IDX[c] for c in chunks[page] if RUNE.match(c)]


def keys() -> list[str]:
    words = set(vocabulary(400))
    for line in VOCAB.read_text().splitlines():
        if line.startswith("#") or "\t" not in line:
            continue
        words.add(line.split("\t")[1].strip())
    return sorted(w for w in words if 3 <= len(w) <= 16)


def sweep(page_runes, words):
    """(prefix score, key, family, interrupt, plaintext) for every combination."""
    out = []
    for word in words:
        k = key_runes(word)
        if not k:
            continue
        for family in FAMILIES:
            for interrupt in (False, True):
                plain = decrypt(page_runes, k, family, interrupt=interrupt)
                out.append((score(plain[:PREFIX]), word, family, interrupt, plain))
    out.sort(key=lambda r: -r[0])
    return out


def readable(v) -> str:
    return "".join(ENGLISH[x] for x in v)


def main() -> None:
    words = keys()
    print(f"{len(words)} keys x {len(FAMILIES)} families x 2 interrupt settings.")
    print(f"Scored on the first {PREFIX} runes only.\n")

    print("CONTROL: page 1, whose key is known to be DIVINITY.\n")
    control = sweep(runes_of(CONTROL), words)
    ranked = control
    where = next((i for i, r in enumerate(ranked) if r[1] == "DIVINITY"), None)
    top = ranked[0]
    print(
        f"  best key found      : {top[1]} ({top[2]}, interrupt={top[3]}) {top[0]:+.3f}"
    )
    print(f"  DIVINITY's rank     : {where}")
    print(f"  its reading         : {readable(top[4])[:58]}")
    null = np.array([r[0] for r in ranked[10:]])
    print(
        f"  z above the rest    : {(top[0] - null.mean()) / null.std(ddof=1):+.2f}"
        f"   (null {null.mean():+.3f} +- {null.std(ddof=1):.3f})\n"
    )

    for page in TARGETS:
        v = runes_of(page)
        ranked = sweep(v, words)
        null = np.array([r[0] for r in ranked[10:]])
        print(f"PAGE {page}, {len(v)} runes. Top {SHOW} by prefix score.\n")
        print(f"{'key':<18}{'family':<24}{'int':>5}{'prefix':>9}{'z':>7}  reading")
        for s, word, family, interrupt, plain in ranked[:SHOW]:
            z = (s - null.mean()) / null.std(ddof=1)
            print(
                f"{word:<18}{family:<24}{str(interrupt):>5}{s:>9.3f}{z:>7.2f}  "
                f"{readable(plain)[:34]}"
            )
        print()


if __name__ == "__main__":
    main()
