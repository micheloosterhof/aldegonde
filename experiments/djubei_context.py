# ABOUTME: Compares the two DJU-BEI contexts: nothing matches in the runes or the
# ABOUTME: word-length clock before them, but both sit against a 13-dot section mark.
"""What do the two DJU-BEI occurrences have in common upstream?

`repeated-phrase-dju-bei.md` records that the ciphertext BEFORE the phrase
differs, so the matching key state arose from different recent history. This
script asks the question at the level that matters mechanically -- the walk is
clocked by word lengths, so a shared recent (L-1) mod 5 sequence would mean the
state agreement was inherited rather than coincidental -- and then looks at the
section marks.

Two results:

1. NOTHING is shared right before. Preceding word length 2 vs 6, (L-1)%5 1 vs 0,
   last rune, first rune all differ; the shared suffix is 0 words on all three
   channels, and the running exponent sum mod 5 disagrees at every depth tested.
   The state return is not inherited from a matching local clock.

2. BOTH are 13-dot adjacent, in complementary positions: occ1 opens a section
   body (2 words after the 13-dot closing a title), occ2 closes one (BEI is
   immediately followed by a 13-dot and the &$% break). Of the 14 repeated-word
   classes in the corpus this is the ONLY one whose occurrences are both
   boundary-adjacent, at every window 0-6.

Post-hoc caveat: the boundary definition and the window were chosen after
reading the two contexts. The 13 other repeat classes are the calibration, not
a pre-registration.

Section model from `mark-glyph-inventory.md`: [rubricated title][13-dot][body].
"""

from __future__ import annotations

import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from walk_verifier import BEI, DJU  # noqa: E402

from aldegonde import c3301  # noqa: E402
from aldegonde.c3301 import CICADA_ALPHABET as A  # noqa: E402

IDX = {r: i for i, r in enumerate(A)}
MAXK = 6


def load_words_and_marks() -> tuple[list[str], list[str]]:
    """walk_verifier.load_words' tokenizer, also keeping the non-rune block that
    closes each word (the marks the word list otherwise discards)."""
    txt = (ROOT / "data" / "page0-56.txt").read_text()
    words: list[str] = []
    blocks: list[str] = []
    cur: list[str] = []
    blk = ""
    for ch in txt:
        if ch in IDX:
            if not cur and words:
                blocks.append(blk)
                blk = ""
            cur.append(ch)
        else:
            if ch in c3301.WORD_BOUNDARY and cur:
                words.append("".join(cur))
                cur = []
            blk += ch
    if cur:
        words.append("".join(cur))
    while len(blocks) < len(words):
        blocks.append(blk)
    return words, blocks


def upstream_report(words: list[str]) -> None:
    print("What is shared in the 10 words before each occurrence?\n")
    print("  k | len      | (L-1)%5  | last rune | first rune")
    for k in range(1, 11):
        a, b = words[DJU - k], words[BEI - k]
        ea, eb = (len(a) - 1) % 5, (len(b) - 1) % 5
        print(
            f" {k:2} | {len(a):2} {len(b):2}    | {ea} {eb} {'=' if ea == eb else ' '}"
            f"      | {a[-1]} {b[-1]} {'=' if a[-1] == b[-1] else ' '}       "
            f"| {a[0]} {b[0]} {'=' if a[0] == b[0] else ' '}"
        )

    print("\nRunning sum of (L-1)%5 (the exponent the walk accumulates), mod 5:")
    for k in (1, 2, 3, 5, 10, 20):
        c1 = sum((len(words[DJU - j]) - 1) % 5 for j in range(1, k + 1)) % 5
        c2 = sum((len(words[BEI - j]) - 1) % 5 for j in range(1, k + 1)) % 5
        print(f"  last {k:2} words: {c1} vs {c2}  {'MATCH' if c1 == c2 else ''}")

    channels = {
        "(L-1)%5": lambda i: (len(words[i]) - 1) % 5,
        "length": lambda i: len(words[i]),
        "last rune": lambda i: words[i][-1],
    }
    rng = random.Random(1)
    n = len(words)
    for name, ch in channels.items():

        def run(i: int, j: int, ch=ch) -> int:
            m = 0
            while m < 20 and ch(i - 1 - m) == ch(j - 1 - m):
                m += 1
            return m

        obs = run(DJU, BEI)
        trials = 20000
        hits = sum(
            run(rng.randrange(25, n), rng.randrange(25, n)) >= obs
            for _ in range(trials)
        )
        print(f"shared suffix on {name}: {obs} words (chance P {hits / trials:.2f})")


def boundary_report(words: list[str], blocks: list[str]) -> None:
    n = len(words)
    starts = {i for i in range(n) if "⑬" in blocks[i - 1]}
    ends = {i for i in range(n) if "⑬" in blocks[i] or "$" in blocks[i]}
    ends.add(n - 1)
    print(f"\nSection-body starts {len(starts)}, ends {len(ends)}")

    pos = defaultdict(list)
    for i, x in enumerate(words):
        if len(x) >= 3:
            pos[x].append(i)
    rep = {k: v for k, v in pos.items() if len(v) > 1}
    others = {k: v for k, v in rep.items() if k not in ("ᛞᛄᚢ", "ᛒᛖᛁ")}

    print("\n  k | occ1  occ2  | baseline | other repeat classes all-adjacent")
    for k in range(MAXK + 1):

        def near(i: int, k=k) -> bool:
            return any((i - d) in starts for d in range(k + 1)) or any(
                (i + d) in ends for d in range(k + 1)
            )

        base = sum(near(i) for i in range(n)) / n
        hit = [kk for kk, v in others.items() if all(near(i) for i in v)]
        print(
            f" {k:2} | {str(near(DJU)):5} {str(near(BEI)):5} | {100 * base:5.1f}%  |"
            f" {len(hit)} of {len(others)}   (chance expects"
            f" {len(others) * base**2:.2f})"
        )

    for nm, i in (("occ1", DJU), ("occ2", BEI)):
        ds = [d for d in range(MAXK) if (i - d) in starts]
        de = [d for d in range(MAXK) if (i + d) in ends]
        print(f"  {nm}: words after a body start {ds}, words before a body end {de}")


def main() -> None:
    words, blocks = load_words_and_marks()
    assert len(words) == 2928, len(words)
    assert words[DJU] == "ᛞᛄᚢ" and words[BEI] == "ᛞᛄᚢ"
    upstream_report(words)
    boundary_report(words, blocks)


if __name__ == "__main__":
    main()
