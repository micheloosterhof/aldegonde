# ABOUTME: Compares word lengths inside the seven quoted spans against the rest
# ABOUTME: of the unsolved corpus, with a contiguous-block permutation null.
"""Do the quoted segments look different from the surrounding text?

The quoted spans are the only stretch of the unsolved corpus known to be a
distinct plaintext register — direct speech (`quote-span-boundaries.md`). If
word boundaries are plaintext-faithful, speech should carry more short function
words than the surrounding text, which is the English pattern and the pattern
the solved pages show.

This matters for the boundary-authenticity question. The unsolved corpus has a
short-word deficit against the solved register (19.3% of words are 1-2 runes
against 27.9%, z ~ 4.7, `word-length-keystream-and-boundaries.md`), and
encryption cannot cause it: word lengths pass through any rune substitution
untouched. Either the plaintext really is that telegraphic, or the boundaries
are not plaintext-faithful. If the quoted speech carries a normal short-word
rate while the surrounding text does not, the deficit is localised rather than
global.

Only 86 words sit inside spans, so this is underpowered by construction. The
detectable effect size is reported alongside the result so the answer is not
mistaken for a decision either way.

The null draws seven contiguous blocks with the same word counts from random
positions, which preserves the contiguity of a span.
"""

from __future__ import annotations

import random
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
BOUNDARY = "-.%&$"
SHORT = 2          # "short word" = 1-2 runes, as in the deficit measurement
SOLVED_SHORT_RATE = 0.279
TRIALS = 20000
SEED = 3301


def words_with_quote_flag(boundary: str = BOUNDARY) -> list[tuple[int, bool]]:
    """(length, inside a quoted span) for every word of sections 0-9.

    Two conventions are in use in this repo. `lp_corpus.load_clean` breaks on
    `- . % & $` and yields the published 2,928 words; section D of
    `word-length-keystream-and-boundaries.md` argues the correct segmentation
    ends words only at `-` and `.`, since 46 of 57 `%` page breaks fall
    mid-word. The choice shifts short-word counts, so both are reported.
    """
    text = "$".join(CORPUS.read_text().split("$")[:10])
    out: list[tuple[int, bool]] = []
    length = 0
    inside = False
    started_inside = False
    for char in text:
        if RUNE.match(char):
            if length == 0:
                # a word belongs to the span it starts in; a closing quote sits
                # after the last rune but before the separator, so the state at
                # the first rune is the one that counts
                started_inside = inside
            length += 1
        elif char == '"':
            inside = not inside
        elif char in boundary and length:
            out.append((length, started_inside))
            length = 0
    if length:
        out.append((length, started_inside))
    return out


def stats(lengths: list[int]) -> tuple[float, float]:
    """Mean length and short-word fraction."""
    short = sum(1 for v in lengths if v <= SHORT) / len(lengths)
    return statistics.mean(lengths), short


def main() -> None:
    rng = random.Random(SEED)

    print("word segmentation convention check")
    for label, bset in (("- . % & $  (lp_corpus)", BOUNDARY), ("- .  (section D)", "-.")):
        w = words_with_quote_flag(bset)
        ins = [v for v, q in w if q]
        out = [v for v, q in w if not q]
        print(f"   {label:24} {len(w):5} words | inside n={len(ins):3} "
              f"mean {statistics.mean(ins):.2f} short {stats(ins)[1]:5.1%} | "
              f"outside mean {statistics.mean(out):.2f} short {stats(out)[1]:5.1%}")
    print()

    words = words_with_quote_flag()
    inside = [v for v, q in words if q]
    outside = [v for v, q in words if not q]
    print(f"clean corpus: {len(words)} words; {len(inside)} inside the seven "
          f"quoted spans, {len(outside)} outside\n")

    for name, sample in (("inside quotes", inside), ("outside quotes", outside)):
        mean, short = stats(sample)
        print(f"{name:16} n={len(sample):5}  mean length {mean:.2f}  "
              f"1-2 runes {short:.1%}")
    print(f"{'solved register':16} {'':11}{'':17}1-2 runes {SOLVED_SHORT_RATE:.1%}"
          "   (word-length-keystream-and-boundaries.md)")

    print("\nlength histogram")
    top = max(max(inside), 12)
    print(f"{'runes':>6}{'inside':>9}{'outside':>10}")
    for n in range(1, top + 1):
        i = sum(1 for v in inside if v == n)
        o = sum(1 for v in outside if v == n)
        print(f"{n:>6}{i:>9}{o / len(outside) * len(inside):>10.1f}")
    print(f"{'':>6}{'observed':>9}{'expected':>10}  (outside rate scaled to n inside)")

    # Null: seven contiguous blocks with the same word counts, placed at random.
    sizes = []
    run = 0
    for _, q in words:
        if q:
            run += 1
        elif run:
            sizes.append(run)
            run = 0
    if run:
        sizes.append(run)
    print(f"\nspan word counts: {sizes}")

    obs_mean, obs_short = stats(inside)
    lengths = [v for v, _ in words]
    null_mean, null_short = [], []
    for _ in range(TRIALS):
        picked: list[int] = []
        for size in sizes:
            start = rng.randrange(0, len(lengths) - size)
            picked.extend(lengths[start:start + size])
        m, s = stats(picked)
        null_mean.append(m)
        null_short.append(s)

    def two_sided(nulls: list[float], obs: float) -> float:
        centre = statistics.mean(nulls)
        extreme = sum(1 for v in nulls if abs(v - centre) >= abs(obs - centre))
        return (extreme + 1) / (TRIALS + 1)

    print(f"\ncontiguous-block permutation null ({TRIALS} draws)")
    print(f"   mean length      observed {obs_mean:.2f}  null "
          f"{statistics.mean(null_mean):.2f} +- {statistics.pstdev(null_mean):.2f}"
          f"  p = {two_sided(null_mean, obs_mean):.3f}")
    print(f"   1-2 rune share   observed {obs_short:.1%}  null "
          f"{statistics.mean(null_short):.1%} +- {statistics.pstdev(null_short):.1%}"
          f"  p = {two_sided(null_short, obs_short):.3f}")

    sd = statistics.pstdev(null_short)
    print(f"\npower: at n={len(inside)} the short-word share has a null sd of "
          f"{sd:.1%}, so only a")
    print(f"   shift beyond ~{2 * sd:.1%} is detectable at 2 sigma. The deficit in "
          f"question is {SOLVED_SHORT_RATE - stats(outside)[1]:.1%}")
    print(f"   ({stats(outside)[1]:.1%} outside vs {SOLVED_SHORT_RATE:.1%} solved), "
          "which is inside that band.")


if __name__ == "__main__":
    main()
