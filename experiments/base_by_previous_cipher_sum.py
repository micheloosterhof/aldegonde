# ABOUTME: Tests a word-level ciphertext autokey indexed by Gematria sums: does the alphabet
# ABOUTME: set of a block depend on the sum of the previous ciphertext block, or on a running sum?
"""Is the per-block alphabet set a function of the previous ciphertext block's sum?

A ciphertext autokey at the word level is public: the solver can compute the state. If
the state is the Gematria Primus sum of the previous ciphertext block (mod 29, mod 5, or
any modulus), every block whose predecessor has the same sum gets the same alphabet set,
and runes at the same within-block phase in such blocks share one substitution. Their
coincidence rate is then the plaintext's (about 1.6-1.8 x chance) instead of chance.
`the-base-is-not-a-ciphertext-autokey.md` covers any function of the whole previous
block on 742 pairs; a sum has only 29 values, so this grouping has hundreds of thousands
of pairs and reads the question at full power. The running-sum states cover the composed
public form base_w = base_0 . T^(cumulative index).

A planted control -- prose re-cut to the body's block lengths, enciphered with 29 bases
indexed by the previous ciphertext block's sum mod 29 -- shows what a hit looks like.

    python experiments/base_by_previous_cipher_sum.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from aldegonde import analysis, c3301

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import order5_fixing  # noqa: E402
from frame_count_baseline import prose_books  # noqa: E402
from within_word_d5 import M, parse_clean_sections  # noqa: E402

SEED = 20261027
GP = [c3301.r2v(r) for r in c3301.CICADA_ALPHABET]
H1 = 1.6  # same-alphabet coincidence of prose runes at matched phase, conservative


def block_sum(block: list[int], values: list[int]) -> int:
    return sum(values[r] for r in block)


def state_functions() -> dict[str, callable]:
    """Each maps (previous block, cumulative GP sum before this block) to a state."""
    fs = {}
    for n in (29, 5, 28, 30, 2):
        fs[f"previous block GP sum mod {n}"] = lambda prev, _cum, n=n: (
            block_sum(prev, GP) % n
        )
    fs["previous block GP sum, raw"] = lambda prev, _cum: block_sum(prev, GP)
    for n in (29, 5):
        fs[f"previous block index sum mod {n}"] = lambda prev, _cum, n=n: (
            block_sum(prev, list(range(M))) % n
        )
    for n in (5, 29, 58, 87, 145, 290):
        fs[f"running GP sum mod {n}"] = lambda _prev, cum, n=n: cum % n
    return fs


def labels_for(words: list[list[int]], state) -> list:
    """One label per rune: (state of its block, phase); the first block is unlabelled."""
    labels = []
    cum = 0
    for w, block in enumerate(words):
        if w == 0:
            labels += [("first", i) for i in range(len(block))]
        else:
            s = state(words[w - 1], cum)
            labels += [(s, j % 5) for j in range(len(block))]
        cum += block_sum(block, GP)
    return labels


def report(title: str, words: list[list[int]]) -> None:
    stream = [r for w in words for r in w]
    print(f"\n{title}: {len(words)} blocks, {len(stream)} runes")
    print(
        f"{'state':<34}{'pairs':>10}{'matched':>9}{'x chance':>10}{'z vs chance':>13}{'z vs H1':>9}"
    )
    for name, state in state_functions().items():
        r = analysis.bucket_coincidence(stream, labels_for(words, state))
        pairs, matched = r.pairs, r.observed
        chance = pairs / M
        sd = (pairs * (1 / M) * (1 - 1 / M)) ** 0.5
        z0 = (matched - chance) / sd
        z1 = (matched - H1 * chance) / sd
        print(
            f"{name:<34}{pairs:>10}{matched:>9}{matched / chance:>10.3f}{z0:>+13.1f}{z1:>+9.1f}"
        )


def planted(lengths: list[int], rng: random.Random) -> list[list[int]]:
    """Prose at the body's lengths, bases indexed by the previous ciphertext block's sum mod 29."""
    need = sum(lengths)
    runes = [r for book in prose_books() for w in book for r in w][:need]
    plain = analysis.recut_words(runes, lengths)
    bases = [rng.sample(range(M), M) for _ in range(M)]
    g = order5_fixing(rng.sample(range(M), 4), rng)
    powers = [list(range(M))]
    for _ in range(4):
        powers.append([g[x] for x in powers[-1]])
    out = []
    state = 0
    for block in plain:
        cipher = [bases[state][powers[j % 5][p]] for j, p in enumerate(block)]
        out.append(cipher)
        state = block_sum(cipher, GP) % M
    return out


def main() -> None:
    sections = parse_clean_sections(str(ROOT / "data/page0-56.txt"))
    words = [w for s in sections for w in s]
    report("the body", words)
    rng = random.Random(SEED)
    report(
        "planted: 29 bases indexed by the previous ciphertext block's GP sum mod 29",
        planted([len(w) for w in words], rng),
    )


if __name__ == "__main__":
    main()
