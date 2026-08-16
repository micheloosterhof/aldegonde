# ABOUTME: Matches every corpus word carrying a d5 repeat (X..X or XY..XY) against
# ABOUTME: the Cicada register (data/register_vocab.txt) -- key-free crib hunt.
"""Which corpus words with a d=5 repeat could be a Cicada stock word?

Within a word c[j]==c[j+5] <=> p[j]==p[j+5], key-free. A corpus word carrying a
d5 EQUALITY (X..X, a rune repeated 5 apart) can only be a plaintext word with the
SAME repeat, and XY..XY (two consecutive) is rarer still. This loads the Cicada
register (data/register_vocab.txt, built by build_register_vocab.py from the
solved LP + the 2012-2014 solved messages + lore) and, for every corpus word with
a d5 repeat, lists the register words whose own d5 pattern fits it (equalities AND
inequalities). A null against a random-English register of the same size shows
whether the fits are a signal or chance.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402, I001
from build_register_vocab import load_register  # noqa: E402
from d5_crib_targets import d5_constraints  # noqa: E402
from runeglish_frequency import english_to_runeglish  # noqa: E402
from walk_verifier import load_words  # noqa: E402

ALPHA = c3301.CICADA_ALPHABET
IDX = {r: i for i, r in enumerate(ALPHA)}


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
    reg = load_register()
    n_reg = sum(len(v) for v in reg.values())
    words = load_words()
    print(f"register: {n_reg} words (data/register_vocab.txt); corpus: {len(words)} words\n")

    doubles, singles = [], []
    for i, w in enumerate(words):
        eq, _ = d5_constraints(w)
        if not eq:
            continue
        eqset = set(eq)
        is_double = any((a + 1, b + 1) in eqset for (a, b) in eq)
        (doubles if is_double else singles).append((i, w))

    for tag, group in [("XY..XY (double d5)", doubles), ("X..X (single d5)", singles)]:
        shown = 0
        print(f"=== {tag}: {len(group)} corpus words")
        for i, w in group:
            f = fits(w, reg)
            if f:
                shown += 1
                need = ",".join(f"p{a}=p{b}" for a, b in d5_constraints(w)[0])
                cipher = "".join(ALPHA[r] for r in w)
                print(f"  word {i:>4} L={len(w):<2} {cipher} ({need}) -> {f[:8]}")
        print(f"  ({shown}/{len(group)} with a register fit)")

    ctrl = control_register(reg)
    real = sum(1 for _i, w in singles if fits(w, reg))
    rand = sum(1 for _i, w in singles if fits(w, ctrl))
    print(
        f"\nsingle-d5 significance: {real}/{len(singles)} fit the Cicada register vs "
        f"{rand}/{len(singles)} a\nrandom-English register of the same sizes."
    )


if __name__ == "__main__":
    main()
