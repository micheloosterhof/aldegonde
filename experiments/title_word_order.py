# ABOUTME: Reads the rubricated title spans' block-length shapes and asks whether their word
# ABOUTME: order looks like English titles or like a shuffle, via where the short words sit.
"""Do the titles stand in English order?

`the-words-are-transposed-within-sentences.md` leaves open whether the words inside a
span are permuted. The rubricated titles are the one place where the plaintext order is
partly known without a key: the author's own titles put an article or preposition
first (A WARNING, A KOAN, THE LOSS OF DIVINITY, AN INSTRUCTION, AN END -- in runes THE,
OF, AN are two runes, A is one), and a one- or two-rune block in a title span is almost
certainly such a word. Under a per-span shuffle it lands in a uniformly random slot.

For every body title span that holds at least two words and at least one block of one or
two runes: is the first such block in the first slot? Priced against a shuffle (exact
Poisson-binomial over the spans' own sizes) and against the author's titles.

The DIVINITY WITHIN crib was matched by its ordered shape (8, 5), so it cannot test the
order; AN END and PARABLE lie outside the body. Those three are listed, not counted.

    python experiments/title_word_order.py
"""

from __future__ import annotations

import json
import re
from itertools import product
from math import comb
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
TITLES = ROOT / "experiments" / "rubricated_titles.json"
SHORT = 2
OUTSIDE_BODY = {71, 72}  # AN END and the plaintext Parable
# the author's own titles, in runes: A=1, THE=2 (TH is one rune), OF=2, AN=2
AUTHOR_TITLES = {
    "A WARNING": (1, 6),
    "SOME WISDOM": (4, 5),
    "A KOAN": (1, 4),
    "THE LOSS OF DIVINITY": (2, 4, 2, 8),
    "AN INSTRUCTION": (2, 10),
    "AN END": (2, 3),
    "PARABLE": (7,),
    "DIVINITY WITHIN": (8, 5),
}


ENG = c3301.CICADA_ENGLISH_ALPHABET


def splits(word: str) -> set[int]:
    """Every rune count a transliterated word can have under the digraph alphabet."""
    if not word:
        return {0}
    out = set()
    for token in ENG:
        if word.startswith(token):
            out |= {1 + n for n in splits(word[len(token) :])}
    return out


MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
RUNE = re.compile(r"[ᚠ-᛿]")


def master_shape(t: dict, chunks: list[str]) -> tuple[int, ...] | None:
    """The title's block lengths read off the master chunk, if its word indexing agrees."""
    words = "".join(c if RUNE.match(c) else " " for c in chunks[t["chunk"]]).split()
    a, b = t["word_range"]
    lengths = tuple(len(w) for w in words[a : b + 1])
    return (
        lengths if sum(lengths) == t["runes"] and len(lengths) == t["words"] else None
    )


def shapes() -> list[dict]:
    """Each title's block-length shape: from the master where its indexing agrees,
    otherwise from the transliteration and the rune total."""
    chunks = MASTER.read_text().split("%")
    out = []
    for t in json.loads(TITLES.read_text()):
        from_master = master_shape(t, chunks)
        if from_master is not None:
            out.append({**t, "shape": from_master})
            continue
        options = [sorted(splits(w)) for w in t["text"].split()]
        fits = [combo for combo in product(*options) if sum(combo) == t["runes"]]
        assert fits, t
        shape = fits[0]
        if len(fits) > 1:
            # ambiguous digraph splits that still sum right; keep the first, note it
            t = {**t, "ambiguous": len(fits)}
        out.append({**t, "shape": tuple(shape)})
    return out


def short_first(shape: tuple[int, ...]) -> bool | None:
    """True/False if the span has >= 2 words and a short one; None if the test does not apply."""
    if len(shape) < 2 or not any(n <= SHORT for n in shape):
        return None
    return shape[0] <= SHORT


def poisson_binomial(ps: list[float]) -> list[float]:
    dist = [1.0]
    for p in ps:
        dist = [
            (dist[k] if k < len(dist) else 0) * (1 - p) + (dist[k - 1] if k else 0) * p
            for k in range(len(dist) + 1)
        ]
    return dist


def main() -> None:
    titles = shapes()
    print(
        f"{'page':>4}{'chunk':>6}  shape                               short word first?"
    )
    tested: list[tuple[str, tuple[int, ...]]] = []
    for t in titles:
        verdict = short_first(t["shape"])
        note = (
            "outside the body"
            if t["chunk"] in OUTSIDE_BODY
            else ("crib, matched by shape" if t["chunk"] == 15 else "")
        )
        shown = "-" if verdict is None else ("yes" if verdict else "no")
        if t.get("ambiguous"):
            note += f" ({t['ambiguous']} digraph splits fit; first kept)"
        print(f"{t['page']:>4}{t['chunk']:>6}  {str(t['shape']):<36}{shown:<6}{note}")
        if verdict is not None and t["chunk"] not in OUTSIDE_BODY and t["chunk"] != 15:
            tested.append((f"page {t['page']}", t["shape"]))

    observed = sum(short_first(s) for _, s in tested)
    ps = [sum(n <= SHORT for n in s) / len(s) for _, s in tested]
    dist = poisson_binomial(ps)
    expected = sum(ps)
    p_ge = sum(dist[observed:])
    print(f"\nbody titles tested: {len(tested)}; short word first in {observed}")
    print(
        f"shuffle: expected {expected:.2f}, P(>= {observed}) = {p_ge:.3f}, P(exactly) = {dist[observed]:.3f}"
    )

    author = [
        (name, s) for name, s in AUTHOR_TITLES.items() if short_first(s) is not None
    ]
    a_yes = sum(short_first(s) for _, s in author)
    print(
        f"author's titles with a short word: {len(author)}, short first in {a_yes} ({', '.join(n for n, _ in author)})"
    )
    # likelihood of the body count under an in-order rate r, for a few r
    n = len(tested)
    print(
        "in-order model at rate r (author's titles read 1.0 on 5; English headlines lower):"
    )
    for r in (0.95, 0.85, 0.7, 0.5):
        like = comb(n, observed) * r**observed * (1 - r) ** (n - observed)
        print(
            f"  r = {r:.2f}: P(exactly {observed} of {n}) = {like:.3f}, against shuffle {dist[observed]:.3f} -> ratio {like / dist[observed]:.2f}"
        )

    print("\nspans where the short word is not first:")
    for name, s in tested:
        if not short_first(s):
            print(f"  {name}: {s}")


if __name__ == "__main__":
    main()
