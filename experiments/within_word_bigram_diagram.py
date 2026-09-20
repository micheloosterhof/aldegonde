# ABOUTME: Within-word bigram diagrams of the LP ciphertext at a range of skips,
# ABOUTME: pairs restricted to a single word so none cross a word boundary.
"""Print the bigram diagram of within-word rune pairs at skips 1..N.

Same grid, colouring and IOC columns as the ordinary bigram diagram, but each
pair (word[i], word[i + skip]) is taken inside one word: a skip-1 diagram is
adjacent letters, skip-2 is one apart, and so on, and the final letter of a word
is never paired with the first letter of the next. Clean corpus: sections 0-9 of
data/page0-56.txt.
"""

import sys  # noqa: I001

sys.path.insert(0, "src")

from aldegonde import c3301
from aldegonde.grams import bigram_diagram

MAX_SKIP = 6
CLEAN = 12956  # sections 0-9

BOUNDARY_CHARS = frozenset(
    c3301.MARK_CHARS + "&%$" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS
)
ALPHABET = list(range(len(c3301.CICADA_ALPHABET)))
R2I = {rune: index for index, rune in enumerate(c3301.CICADA_ALPHABET)}


def load_words() -> list[list[int]]:
    """Clean-corpus words as rune-index lists.

    Runes accumulate into the current word; a word boundary mark closes it; a
    line wrap is passed through so a word runs across it. Capped at the clean
    corpus length.
    """
    with open("data/page0-56.txt") as f:
        text = f.read()
    words: list[list[int]] = []
    current: list[int] = []
    total = 0
    for char in text:
        if total >= CLEAN:
            break
        if char in R2I:
            current.append(R2I[char])
            total += 1
        elif char in BOUNDARY_CHARS:
            if current:
                words.append(current)
                current = []
        elif char in c3301.LINE_WRAP:
            pass
    if current:
        words.append(current)
    return words


def main() -> None:
    words = load_words()
    for skip in range(1, MAX_SKIP + 1):
        print(f"\nwithin-word bigram diagram, skip={skip}")
        bigram_diagram.print_within_word_bigram_diagram(
            words, alphabet=ALPHABET, skip=skip
        )


if __name__ == "__main__":
    main()
