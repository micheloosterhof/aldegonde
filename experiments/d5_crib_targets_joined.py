# ABOUTME: Re-runs the d5 crib targets with the book's spelling and with joined
# ABOUTME: candidates (a 2-rune word written together with the next word).
"""Do the d5 crib lists survive the book's spelling and the joining of short words?

`d5_crib_targets.py` prunes the blocks carrying XY..XY at lag 5 against single
dictionary words. Two later results change its candidate space:

  * the book's spelling (`c3301.encode_english`) differs from `english_to_runeglish`:
    ING is one rune, QU is C-W, IO is IA (`book-spelling-rules` in the notes);
  * about 40% of 2-rune words are written joined to the next word
    (`short-units-are-written-joined.md`, `plaintext-is-english.md`), so a block may be
    a two-word phrase such as OF+THINGS.

Joined candidates come from consecutive word pairs in the Gutenberg prose registers
whose first word spells to 2 runes, weighted by how often the pair occurs there.

Inside a block c_j == c_(j+5) <=> p_j == p_(j+5), with no key in it, so a candidate
must satisfy every lag-5 equality and every lag-5 inequality of its block.

Blocks come from `lp_corpus.load_clean(join_pages=True)`, so no block is cut by a
page break.

**Result (2026-10-19).** Seven of the eight XY..XY blocks gain joined candidates, 1 to
44 each against 4 to 152 single words. In two blocks the most frequent joined pair
beats the most frequent single word: 1967 (TO+RUSTICUS, 1.6x) and 2148 (AN+INFINITE,
2.7x). A single-word list leaves out candidates as likely as its best. Some pairs are
artifacts of words run together in the Gutenberg files (THE+SENSESTHE).
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import PROSE_REGISTERS  # noqa: E402
from d5_crib_targets import d5_constraints  # noqa: E402
from ea_direction_test import PROSE_CACHE, prose_words  # noqa: E402
from external_text_length_match import CACHE as BOOK_CACHE  # noqa: E402
from lp_corpus import load_clean  # noqa: E402

from aldegonde import c3301  # noqa: E402

DICT_SIZE = 200000
SHOW = 8


def blocks() -> list[list[int]]:
    stream, word_id = load_clean(join_pages=True)
    out: dict[int, list[int]] = collections.defaultdict(list)
    for rune, w in zip(stream, word_id):
        out[w].append(rune)
    return [out[k] for k in sorted(out)]


def spell(word: str) -> tuple[int, ...]:
    return tuple(c3301.encode_english(word))


def single_words() -> dict[int, list[tuple[float, str, tuple[int, ...]]]]:
    from wordfreq import top_n_list, word_frequency  # noqa: PLC0415

    out = collections.defaultdict(list)
    for word in top_n_list("en", DICT_SIZE):
        if word.isalpha():
            runes = spell(word)
            if runes:
                out[len(runes)].append((word_frequency(word, "en"), word, runes))
    return out


def joined_pairs() -> dict[int, list[tuple[float, str, tuple[int, ...]]]]:
    """Consecutive prose word pairs whose first word is 2 runes, by pair frequency."""
    counts: collections.Counter = collections.Counter()
    total = 0
    for number in PROSE_REGISTERS:
        path = PROSE_CACHE if number is None else BOOK_CACHE / f"pg{number}.txt"
        if not path.exists():
            continue
        words = [w.lower() for w in prose_words(path)]
        total += len(words)
        for a, b in zip(words, words[1:]):
            if len(spell(a)) == 2 and spell(b):
                counts[a, b] += 1
    out = collections.defaultdict(list)
    for (a, b), n in counts.items():
        runes = spell(a) + spell(b)
        out[len(runes)].append((n / total, f"{a}+{b}", runes))
    return out


def fits(block, candidates):
    equal, unequal = d5_constraints(block)
    return sorted(
        (
            (f, name)
            for f, name, runes in candidates.get(len(block), [])
            if all(runes[a] == runes[b] for a, b in equal)
            and all(runes[a] != runes[b] for a, b in unequal)
        ),
        reverse=True,
    )


def self_test() -> None:
    assert len(spell("of")) == 2 and len(spell("thing")) == 2
    # OF+NATURE spells O F N A T U R E: 8 runes, every lag-5 pair unequal
    block = list(spell("of") + spell("nature"))
    equal, unequal = d5_constraints(block)
    assert len(block) == 8 and not equal and len(unequal) == 3
    cands = {
        8: [(1.0, "of+nature", tuple(block)), (0.5, "bad", (0, 1, 2, 3, 4, 0, 6, 7))]
    }
    assert [n for _, n in fits(block, cands)] == ["of+nature"]
    print("self-test passed")


def run() -> None:
    body = blocks()
    print(f"{len(body)} blocks (page breaks joined)")
    singles = single_words()
    joined = joined_pairs()
    targets = [
        (i, b)
        for i, b in enumerate(body)
        if any(b[j] == b[j + 5] and b[j + 1] == b[j + 6] for j in range(len(b) - 6))
    ]
    print(f"{len(targets)} blocks carry XY..XY at lag 5\n")
    for index, block in targets:
        equal, _ = d5_constraints(block)
        s = fits(block, singles)
        j = fits(block, joined)
        needs = ", ".join(f"p{a}=p{b}" for a, b in equal)
        print(
            f"block {index:>5} L={len(block):<3}"
            f"{''.join(c3301.CICADA_ALPHABET[r] for r in block)}   requires {needs}"
        )
        print(
            f"    single words: {len(s):>4}  " + ", ".join(name for _, name in s[:SHOW])
        )
        print(
            f"    joined pairs: {len(j):>4}  " + ", ".join(name for _, name in j[:SHOW])
        )
        if s and j:
            # how the best joined pair compares in frequency with the best single word
            print(f"    top pair / top word frequency: {j[0][0] / s[0][0]:.2g}")


if __name__ == "__main__":
    if "--run" in sys.argv:
        run()
    else:
        self_test()
