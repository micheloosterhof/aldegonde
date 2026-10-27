# ABOUTME: Tests whether each word's base alphabet is a keyword alphabet built from the previous
# ABOUTME: plaintext word, using the DIVINITY WITHIN title as a known adjacent pair in the visible order.
"""Is the base a keyword alphabet keyed by the previous plaintext word?

Under the walk, c_k = base_w(g^k(p_k)) inside a word. If base_w is a keyword alphabet built
from the previous plaintext word, the DIVINITY WITHIN title decides it without knowing g:

- WITHIN's base is f(DIVINITY), and its first rune has no g, so f(DIVINITY) must send W to
  WITHIN's first ciphertext rune;
- DIVINITY's base is f(P) for the unknown word P before it, scanned over a dictionary;
  its runes 0 and 5 are g-free (g^5 = 1), and runes 1, 3 and 4 (I, I, N) sit at the same
  positions with the same plaintext in WITHIN, so the g-values read off the two words must
  agree.

Six 1/29 checks per (P, construction). A candidate survives at 0 mismatches, or at 1 if
the doublet preventer fired once inside the crib. Constructions: the four keyword rules of
`keyword_exhaustion.alphabets`, the keyed alphabet on the ciphertext or the plaintext
side, and with the clock restarting at each word or running on across the title (then
the g-free and shared positions change, and the script derives them). A free rotation
of the keyed alphabet per word is a separate, weaker variant. The false-survivor rate is
measured on random ciphertext, and a planted key must be recovered before the real crib
is read.

    python experiments/previous_word_keyed_alphabet_crib.py [--top 3000]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from keyword_exhaustion import alphabets  # noqa: E402
from lp_corpus import load_words  # noqa: E402
from quagmire_ungated_sweep import priority_vocabulary  # noqa: E402

from aldegonde import c3301  # noqa: E402
from aldegonde.maths import permutation  # noqa: E402

M = 29
SEED = 20261028
CRIB = ["DIVINITY", "WITHIN"]
PLAIN = [c3301.encode_english(w) for w in CRIB]
NULL_DRAWS = 300


def keyword(word: str) -> list[int]:
    """The word's runes as the book spells them, de-duplicated, order kept."""
    out: list[int] = []
    for r in c3301.encode_english(word):
        if r not in out:
            out.append(r)
    return out


def constructions(word: str):
    """(label, A, B): the plaintext-side rune is A[(B[c] - r) % 29] for a rotation r."""
    std = np.arange(M)
    for rule, K in alphabets(keyword(word)):
        K = np.array(K)
        pos = np.empty(M, dtype=int)
        pos[K] = std
        yield f"{rule}, cipher side", std, pos  # c = K[idx(x) + r]
        yield f"{rule}, plain side", K, std  # c = std[pos_K(x) + r]


def positions(clock: str) -> list[tuple[int, int, int]]:
    """(word, rune index in word, clock phase k mod 5) for the 13 crib runes."""
    out, k = [], 0
    for w, p in enumerate(PLAIN):
        if clock == "restart":
            k = 0
        for i in range(len(p)):
            out.append((w, i, k % 5))
            k += 1
    return out


def checks(
    pos: list[tuple[int, int, int]],
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """(rune, plaintext) pairs that are g-free, and rune pairs that must carry the same g-value."""
    groups: dict[tuple[int, int], list[int]] = {}
    for n, (w, i, k) in enumerate(pos):
        groups.setdefault((k, PLAIN[w][i]), []).append(n)
    free = [(members[0], p) for (k, p), members in groups.items() if k == 0]
    free += [
        (m, p) for (k, p), members in groups.items() if k == 0 for m in members[1:]
    ]
    same = []
    for (k, _), members in groups.items():
        if k:
            assert len(members) <= 2, members
            if len(members) == 2:
                same.append((members[0], members[1]))
    return free, same


class Candidates:
    """The keyed alphabets of every candidate previous word, one array pair per construction."""

    def __init__(self, words: list[str]) -> None:
        self.words = words
        cons = [list(constructions(w)) for w in words]
        self.labels = [label for label, _, _ in cons[0]]
        self.a = [np.array([c[j][1] for c in cons]) for j in range(len(self.labels))]
        self.b = [np.array([c[j][2] for c in cons]) for j in range(len(self.labels))]


def scan(
    cipher: list[list[int]], cands: Candidates, clock: str, *, rotate: bool
) -> np.ndarray:
    """Fewest mismatches over rotations, shape (candidates, constructions)."""
    pos = positions(clock)
    free, same = checks(pos)
    c = np.array([cipher[w][i] for w, i, _ in pos])
    word = np.array([w for w, _, _ in pos])
    r = np.arange(M) if rotate else np.arange(1)
    second = list(constructions(CRIB[0]))
    out = np.empty((len(cands.words), len(cands.labels)), dtype=int)
    idx = np.arange(len(cands.words))[:, None, None]
    for j, (_, a1, b1) in enumerate(second):
        a0, b0 = cands.a[j], cands.b[j]
        v0 = b0[:, c]  # (cands, 13)
        x0 = a0[idx, (v0[:, None, :] - r[None, :, None]) % M]  # (cands, r0, 13)
        x1 = a1[(b1[c][None, :] - r[:, None]) % M]  # (r1, 13)
        x = np.where(
            word[None, None, None, :] == 0, x0[:, :, None, :], x1[None, None, :, :]
        )  # (cands, r0, r1, 13)
        bad = np.zeros(x.shape[:3], dtype=int)
        for n, p in free:
            bad += x[..., n] != p
        for m0, m1 in same:
            bad += x[..., m0] != x[..., m1]
        out[:, j] = bad.min(axis=(1, 2))
    return out


def survivors(cipher, cands: Candidates, clock, allow, *, rotate=False):
    bad = scan(cipher, cands, clock, rotate=rotate)
    return [
        (cands.words[i], cands.labels[j]) for i, j in zip(*np.nonzero(bad <= allow))
    ]


def encipher(
    prev: str, g: list[int], rule_index: int, clock: str, rng
) -> list[list[int]]:
    """A planted crib: base from the previous word, g inside words, the chosen construction."""
    pos = positions(clock)
    bases = [
        list(constructions(prev))[rule_index],
        list(constructions(CRIB[0]))[rule_index],
    ]
    out = [[0] * len(p) for p in PLAIN]
    for w, i, k in pos:
        _, a, b = bases[w]
        x = PLAIN[w][i]
        for _ in range(k):
            x = g[x]
        # invert x = a[(b[c]) % M]: find c with a[b[c]] == x
        c = int(np.where(a[b] == x)[0][0])
        out[w][i] = c
    return out


def self_test(cands: Candidates, rng) -> None:
    words = cands.words
    g = permutation.random_with_cycle_type(M, [5, 5, 5, 5, 5, 1, 1, 1, 1], rng)
    for clock in ("restart", "continuous"):
        for rule_index in (0, 5):
            prev = rng.choice(words)
            planted = encipher(prev, g, rule_index, clock, rng)
            found = survivors(planted, cands, clock, 0)
            assert (prev, list(constructions(prev))[rule_index][0]) in found, (
                clock,
                rule_index,
                prev,
                found,
            )
            # one preventer fire: a changed rune is found at one mismatch
            hit = [list(w) for w in planted]
            hit[0][0] = (hit[0][0] + 1) % M  # rune 0 is g-free under either clock
            assert (prev, list(constructions(prev))[rule_index][0]) not in survivors(
                hit, cands, clock, 0
            )
            assert (prev, list(constructions(prev))[rule_index][0]) in survivors(
                hit, cands, clock, 1
            )
    print(
        "self-test passed: planted keys recovered, a fired rune found at one mismatch"
    )


def main() -> None:
    top = 3000
    for i, a in enumerate(sys.argv):
        if a == "--top" and i + 1 < len(sys.argv):
            top = int(sys.argv[i + 1])
    rng = random.Random(SEED)
    from wordfreq import top_n_list  # noqa: PLC0415

    words = sorted(
        {w.upper() for w in top_n_list("en", top) if w.isalpha()}
        | {w.upper() for w in priority_vocabulary()}
    )
    words = [w for w in words if keyword(w)]
    body = load_words()
    cipher = [body[0], body[1]]
    assert [len(w) for w in cipher] == [len(p) for p in PLAIN]
    print(
        f"crib {' '.join(CRIB)} at body words 0-1; {len(words)} candidate previous words"
    )

    cands = Candidates(words)
    self_test(Candidates(words[:200]), rng)

    nrng = np.random.default_rng(SEED)
    for rotate in (False, True):
        for clock in ("restart", "continuous"):
            label = f"{'free rotation per word' if rotate else 'no rotation'}, clock {clock}"
            print(f"\n{label}")
            draws = NULL_DRAWS if not rotate else 100
            null = np.array(
                [
                    scan(
                        [list(nrng.integers(0, M, len(p))) for p in PLAIN],
                        cands,
                        clock,
                        rotate=rotate,
                    )
                    for _ in range(draws)
                ]
            )
            real = scan(cipher, cands, clock, rotate=rotate)
            for allow in (0, 1):
                hits = (null <= allow).sum(axis=(1, 2))
                found = [
                    (cands.words[i], cands.labels[j])
                    for i, j in zip(*np.nonzero(real <= allow))
                ]
                print(
                    f"  mismatches <= {allow}: body {len(found)} survivors;"
                    f" random ciphertext {hits.mean():.2f} +- {hits.std():.2f} ({draws} draws)"
                )
                for w, lab in found[:20]:
                    print(f"    {w:<14} {lab}")
    print(
        "\nA survivor is a previous word and construction reproducing the crib's g-free and"
        "\nshared runes; the random-ciphertext row is the false-survivor rate to read it against."
    )


if __name__ == "__main__":
    main()
