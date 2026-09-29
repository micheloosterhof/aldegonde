# ABOUTME: Searches for a per-page block transposition that would restore the word-length
# ABOUTME: order the body is missing, testing the reordering reading against a plant.
"""If the blocks were reordered, undoing the reordering must put the order back.

`separators-are-not-word-boundaries.md` measures that the body's word-length sequence
carries a tenth of the serial structure language has, under every tokenization, and that
no merge rule reproduces both the histogram and the order. Two readings survive. One is
that the plaintext is a list, with no sentence order to carry. The other is that the
blocks were REORDERED -- which preserves the length multiset exactly and destroys its
order exactly.

The reordering reading makes a demand the list reading does not: a reader has to be able
to undo it, so the permutation is a rule, not a shuffle. The classical rules are route
transpositions, and they are few enough to enumerate.

So: for each candidate rule, un-permute the length sequence within each page and measure
the transition structure again. A correct inverse restores it to the language level. The
plant below shows the search finds a rule when one is there.

Scope. This searches per-PAGE transpositions of whole blocks. A permutation spanning
pages, or one that moves runes rather than blocks, is not covered.

    python block_transposition_search.py [--control]
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from word_length_sequence import excess_per_pair, prose_sequences  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"


def page_lengths() -> list[list[int]]:
    """Block lengths per master chunk, unsolved pages only (chunk 15 onward)."""
    out = []
    for chunk in MASTER.read_text().split("%")[15:]:
        if not RUNE.search(chunk):
            continue
        seq, cur = [], 0
        for ch in chunk:
            if RUNE.match(ch):
                cur += 1
            elif ch in "/\n":
                continue
            elif cur and ch in c3301.WORD_BOUNDARY:
                seq.append(cur)
                cur = 0
        if cur:
            seq.append(cur)
        if len(seq) > 8:
            out.append(seq)
    return out


def columnar(n: int, cols: int) -> list[int]:
    """Read-by-column order of n items written in rows of `cols`."""
    return [
        r * cols + c
        for c in range(cols)
        for r in range((n + cols - 1) // cols)
        if r * cols + c < n
    ]


def rail(n: int, rails: int) -> list[int]:
    """Rail-fence order."""
    rows: list[list[int]] = [[] for _ in range(rails)]
    r, step = 0, 1
    for i in range(n):
        rows[r].append(i)
        if rails > 1:
            if r == 0:
                step = 1
            elif r == rails - 1:
                step = -1
            r += step
    return [i for row in rows for i in row]


def rules(n: int) -> dict[str, list[int]]:
    """Candidate permutations of n blocks, as the order they were READ OUT in."""
    out: dict[str, list[int]] = {
        "identity": list(range(n)),
        "reverse": list(range(n))[::-1],
    }
    for c in range(2, 13):
        out[f"columnar {c}"] = columnar(n, c)
    for k in range(2, 6):
        out[f"rail {k}"] = rail(n, k)
    return out


def unpermute(seq: list[int], order: list[int]) -> list[int]:
    """Undo a read-out order: element written at position order[i] was read i-th."""
    out = [0] * len(seq)
    for i, src in enumerate(order):
        out[src] = seq[i]
    return out


def score(pages: list[list[int]], name: str, rng: random.Random) -> tuple[float, float]:
    restored = [unpermute(p, rules(len(p))[name]) for p in pages]
    e, se, _o, _m, _n = excess_per_pair(restored, rng, draws=60)
    return e, se


def main() -> None:
    rng = random.Random(3301)
    names = list(rules(40))

    if "--control" in sys.argv:
        prose = prose_sequences(40000)[0][1]
        pages, i = [], 0
        while i + 45 < len(prose):
            pages.append(prose[i : i + 45])
            i += 45
        pages = pages[: len(page_lengths())]
        planted = [[p[j] for j in rules(len(p))["columnar 7"]] for p in pages]
        base = excess_per_pair(pages, rng, draws=40)[0]
        print(f"prose cut into {len(pages)} pages: excess/pair {base:.4f}")
        scram = excess_per_pair(planted, rng, draws=40)[0]
        print(f"after a columnar-7 transposition:  {scram:.4f}")
        rows = sorted(((score(planted, n, rng)[0], n) for n in names), reverse=True)
        print("\nbest rules recovered by the search:")
        for e, n in rows[:4]:
            print(f"  {e:>8.4f}  {n}")
        return

    pages = page_lengths()
    words = sum(len(p) for p in pages)
    print(f"{len(pages)} unsolved pages, {words:,} blocks\n")
    rows = sorted(((score(pages, n, rng), n) for n in names), reverse=True)
    print(f"{'rule':<16}{'excess/pair':>16}")
    for (e, se), n in rows[:8]:
        print(f"{n:<16}{e:>10.4f} +-{se:.4f}")
    print(
        "\nlanguage reference: 0.0397 +- 0.0101 (the LP's own plaintext),"
        "\n0.0484 +- 0.0160 (prose). No rule comes near it."
    )


if __name__ == "__main__":
    main()
