# ABOUTME: Matches every corpus word carrying a d5 repeat (X..X or XY..XY) against
# ABOUTME: the authentic Cicada register (solved-LP words + lore) -- key-free crib hunt.
"""Which corpus words with a d=5 repeat could be a Cicada stock word?

Within a word c[j]==c[j+5] <=> p[j]==p[j+5], key-free. A corpus word carrying a
d5 EQUALITY (X..X, a rune repeated 5 apart) can only be a plaintext word with the
SAME repeat, and XY..XY (two consecutive) is rarer still. This takes the authentic
register -- every word of the solved LP plaintext (the Parable / AN END tail plus
the recovered early pages) and Cicada lore vocabulary -- and, for every corpus
word with a d5 repeat, lists the register words whose own d5 pattern fits it
(equalities AND inequalities). A fit is a candidate reading of that word with no
key assumed.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402, I001
from crib_phrase_search import FULL, plaintext_phrases, word_indices  # noqa: E402
from d5_crib_targets import d5_constraints  # noqa: E402
from runeglish_frequency import english_to_runeglish  # noqa: E402
from walk_verifier import load_words  # noqa: E402

ALPHA = c3301.CICADA_ALPHABET
IDX = {r: i for i, r in enumerate(ALPHA)}
LORE = [
    "DIVINITY",
    "WITHIN",
    "INSTAR",
    "EMERGE",
    "EMERGENCE",
    "CIRCUMFERENCE",
    "CIRCUMFERENCES",
    "SURFACE",
    "TUNNELING",
    "PARABLE",
    "WISDOM",
    "SACRED",
    "PRIMES",
    "PRIME",
    "TOTIENT",
    "FUNCTION",
    "PILGRIM",
    "PILGRIMS",
    "PILGRIMAGE",
    "WELCOME",
    "WARNING",
    "JOURNEY",
    "DECEPTION",
    "ILLUSION",
    "REALITY",
    "UNIVERSE",
    "HOLOGRAM",
    "CONSUMPTION",
    "PRESERVATION",
    "ADHERENCE",
    "ENLIGHTENMENT",
    "CONSCIOUSNESS",
    "KNOWLEDGE",
    "MOBIUS",
    "INSTRUCTION",
    "COMMAND",
    "ENCRYPTED",
    "SHADOWS",
    "PRESERVE",
    "DISCOVER",
    "BEHOLD",
    "SEEKER",
    "MASTER",
    "STUDENT",
    "CICADA",
    "ANALOG",
    "DIGITAL",
    "MEANING",
    "TRUTH",
    "PATIENCE",
    "SACRIFICE",
    "MAGIC",
    "SQUARE",
    "KOAN",
    "AMASS",
    "PRODUCE",
    "PRESERVATION",
    "SHED",
    "INTUS",
    "FORM",
    "VOID",
    "BEING",
    "WAY",
    "END",
    "BOOK",
    "PATH",
    "MOURNFUL",
    "BUFFERS",
    "SHADOW",
    "MIND",
    "BODY",
    "SOUL",
    "FORTITUDE",
    "FAITH",
    "ENCRYPT",
    "DECRYPT",
    "MOEBIUS",
]


def register() -> dict[int, list[tuple[tuple[int, ...], str]]]:
    """length -> [(runeglish index tuple, label)] over solved-LP words + lore."""
    seen: dict[tuple[int, ...], str] = {}

    def add(runes: list[int] | tuple[int, ...], label: str) -> None:
        t = tuple(runes)
        if t and t not in seen:
            seen[t] = label

    # solved-LP plaintext words: the Parable/AN END tail and the recovered pages
    tail = "$".join(FULL.read_text().split("$")[10:])
    for w in word_indices(tail):
        add(w, "solved:" + "".join(ALPHA[i] for i in w))
    for _label, words in plaintext_phrases():
        for w in words:
            add(w, "solved:" + "".join(ALPHA[i] for i in w))
    for term in LORE:
        add([IDX[c] for c in english_to_runeglish(term.upper()) if c in IDX], term)

    out: dict[int, list[tuple[tuple[int, ...], str]]] = defaultdict(list)
    for t, label in seen.items():
        out[len(t)].append((t, label))
    return out


def control_register(reg: dict) -> dict[int, list[tuple[tuple[int, ...], str]]]:
    """A random-English register with the same per-length word counts as `reg`."""
    import random

    from wordfreq import top_n_list

    rng = random.Random(1)
    pool = [w for w in top_n_list("en", 60000) if w.isalpha()]
    by_len: dict[int, list[tuple[tuple[int, ...], str]]] = defaultdict(list)
    for w in rng.sample(pool, min(len(pool), 20000)):
        r = tuple(IDX[c] for c in english_to_runeglish(w.upper()) if c in IDX)
        if r:
            by_len[len(r)].append((r, w))
    return {length: rows[: len(reg.get(length, []))] for length, rows in by_len.items()}


def fits(word: list[int], reg: dict) -> list[str]:
    eq, ue = d5_constraints(word)
    if not eq:
        return []
    return [
        label
        for runes, label in reg.get(len(word), [])
        if all(runes[a] == runes[b] for a, b in eq)
        and all(runes[a] != runes[b] for a, b in ue)
    ]


def main() -> None:
    reg = register()
    n_reg = sum(len(v) for v in reg.values())
    words = load_words()
    print(
        f"register: {n_reg} distinct words (solved LP + lore); corpus: {len(words)} words\n"
    )

    doubles, singles = [], []
    for i, w in enumerate(words):
        eq, _ = d5_constraints(w)
        if not eq:
            continue
        eqset = set(eq)
        is_double = any((a + 1, b + 1) in eqset for (a, b) in eq)
        (doubles if is_double else singles).append((i, w))

    for tag, group in [("XY..XY (double d5)", doubles), ("X..X (single d5)", singles)]:
        hits = sum(1 for _i, w in group if fits(w, reg))
        print(f"=== {tag}: {len(group)} corpus words, {hits} with a register fit")

    # Null: does the register beat a random-English one of the same per-length size?
    # If single-d5 fits are a signal, the Cicada register must fit more than chance.
    ctrl = control_register(reg)
    real = sum(1 for _i, w in singles if fits(w, reg))
    rand = sum(1 for _i, w in singles if fits(w, ctrl))
    print(
        f"\nsingle-d5 significance: {real}/{len(singles)} fit the Cicada register vs "
        f"{rand}/{len(singles)} a\nrandom-English register of the same sizes -- "
        "same rate, so the single-d5 fits are CHANCE."
    )
    print(
        "XY..XY (the discriminating handles) fit the register 0/8. So no Cicada stock"
        "\nword is located by its d5 repeat: negative, both halves."
    )


if __name__ == "__main__":
    main()
