# ABOUTME: Simulates word-keyed ciphers whose base is set by a compact state (public
# ABOUTME: clock x secret clock) and compares their key-free predictions with the LP.
"""Which compact-state models fit the LP's four recurrence statistics?

If DJU-BEI is a deliberate repeat, the cipher state recurs, so the number of
word-level bases N is small (`hypotheses/dju-bei-gate-validity.md`). A state the
solver can compute from public data is excluded (`word_state_sweep.py`), so part
of the state must be secret: driven by plaintext content or by key material.

Each model here sets the base of word w from a state (public part, secret part).
The base of each state is an independent random permutation and the letter step
inside a word is an order-5 permutation g. Doublet suppression is left out: the
re-draw rule of `stream-cipher-no-repeat.md` would break exact word repeats, so the
DJU-BEI repeat requires a deterministic mechanism (a tuned g), and a tuned g changes
none of the four statistics below.

English prose is enciphered under the model and measured with the same functions as
the corpus:

  returns     word-aligned repeats of two consecutive words, 6 runes or more
  identical   pairs of identical cipher words of 3 runes or more
  long        pairs of identical cipher words of 4 runes or more
  clock       coincidence in (A-w mod 29, phase) buckets, relative to 1/29

**Result (2026-09-19).** LP: 1 return, 17 identical, 0 long. `--fit`, 260 prose
corpora over 10 registers, state counts N:

  N        P(word counts fit)   P(return)   P(return | word counts fit)
  generic walk      0.742         ~1.4e-6            ~1.4e-6
  850               0.008          0.365              0.000
  1200              0.015          0.335              0.000
  2000              0.123          0.242              0.031
  4205              0.342          0.096              0.011
  20000             0.619          0.031              0.006

Two conclusions. N below about 1,200 is refuted by the LP's own word counts: such a
state space leaks 27 to 73 identical cipher words where the LP has 17. Among the
state counts that do fit those counts, the return occurs in 0.6% to 3% of corpora,
against 1.4e-6 under a generic walk, so the LP's three counts favour a compact state
of a few thousand by about 1e4. Neither model makes the return probable.

A state built only from public data is refuted again here, and by a wider margin
than in `word_state_sweep.py`: the public clock alone reads 2.196 on the clock
statistic where the LP reads 1.007.

Run with no arguments for the self-test of the measuring functions, `--run` for the
model table, `--fit` for the state-count comparison.
"""

from __future__ import annotations

import functools
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import TYPE_CHECKING

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish  # noqa: E402
from doublet_position_profile import IDX_ENG  # noqa: E402
from ea_direction_test import PROSE_CACHE, prose_words  # noqa: E402
from external_text_length_match import CACHE as BOOK_CACHE  # noqa: E402
from lp_corpus import load_clean  # noqa: E402

from aldegonde import c3301  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Sequence

N_RUNES = 29
GP_VALUE = [c3301.r2v(r) for r in c3301.CICADA_ALPHABET]
CHANCE = 1.0 / N_RUNES
PHRASE_RUNES = 6  # DJU-BEI is 3 + 3
# prose registers: a novel, essays, philosophy, autobiography. None is scripture or
# verse. `None` is the repo's stand-in register, Pride and Prejudice.
PROSE_REGISTERS = (None, 205, 16643, 2945, 4363, 3296, 1497, 14209, 2680, 131)
MIN_WORD = 3  # shorter words repeat by chance too often to mean anything


def recurrence_counts(words: Sequence[Sequence[int]]) -> dict[str, int]:
    """Word-repeat statistics of a cipher corpus.

    returns    pairs of positions carrying the same two consecutive words,
               PHRASE_RUNES runes or more (the DJU-BEI event)
    identical  pairs of equal words of MIN_WORD runes or more
    long       pairs of equal words of MIN_WORD + 1 runes or more
    """
    phrases = Counter(
        (tuple(a), tuple(b))
        for a, b in zip(words, words[1:])
        if len(a) + len(b) >= PHRASE_RUNES
    )
    counts = Counter(tuple(w) for w in words if len(w) >= MIN_WORD)
    pairs = lambda c: sum(n * (n - 1) // 2 for n in c.values())  # noqa: E731
    return {
        "returns": pairs(phrases),
        "identical": pairs(counts),
        "long": pairs(Counter({w: n for w, n in counts.items() if len(w) > MIN_WORD})),
    }


def clock_reading(words: Sequence[Sequence[int]]) -> float:
    """Coincidence in (A - w mod 29, within-word phase) buckets, over 1/29.

    A - w is the number of letter steps before the word, the walk's own increment
    and the one public clock cell that leans in the corpus
    (`word_state_local_sweep.py`). A model whose state includes this clock reads
    1 + (1/S)(plaintext rate/chance - 1) with S the number of secret states; a
    model that does not reads about 1.
    """
    buckets: dict[tuple[int, int], Counter] = defaultdict(Counter)
    steps = 0
    for w, word in enumerate(words):
        for j, rune in enumerate(word):
            buckets[((steps - w) % N_RUNES, j % 5)][rune] += 1
        steps += len(word)
    hits = total = 0
    for cell in buckets.values():
        size = sum(cell.values())
        hits += sum(n * (n - 1) // 2 for n in cell.values())
        total += size * (size - 1) // 2
    return (hits / total) / CHANCE if total else float("nan")


@functools.cache
def _prose_books() -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Each prose register as a list of runeglish words, longest first.

    One novel does not supply enough windows of 2,928 CONSECUTIVE words, and a
    window running past the end of a text would be short and show far fewer repeats
    than the corpus it stands for. Scripture and verse are left out: their formulaic
    repetition is several times that of the LP's own solved pages, and every
    statistic here scales with the plaintext's repeat rate. The first and last tenth
    of each file is dropped, which removes the Project Gutenberg boilerplate.
    """
    books = []
    for number in PROSE_REGISTERS:
        path = PROSE_CACHE if number is None else BOOK_CACHE / f"pg{number}.txt"
        if not path.exists():
            continue
        words = []
        for word in prose_words(path):
            runes = tuple(IDX_ENG[t] for t in to_runeglish(word))
            if runes:
                words.append(runes)
        trim = len(words) // 10
        words = words[trim : len(words) - trim]
        if len(words) > 3000:
            books.append(tuple(words))
    return tuple(sorted(books, key=len, reverse=True))


def prose_corpora(n_words: int, count: int) -> list[list[list[int]]]:
    """`count` disjoint windows of `n_words` consecutive prose words."""
    out = []
    for book in _prose_books():
        for start in range(0, len(book) - n_words + 1, n_words):
            out.append([list(w) for w in book[start : start + n_words]])
            if len(out) == count:
                return out
    msg = f"only {len(out)} corpora of {n_words} words available, need {count}"
    raise AssertionError(msg)


def order5(rng: random.Random) -> list[int]:
    g = list(range(N_RUNES))
    points = rng.sample(range(N_RUNES), 25)
    for c in range(5):
        cycle = points[5 * c : 5 * c + 5]
        for t in range(5):
            g[cycle[t]] = cycle[(t + 1) % 5]
    return g


def encipher(plain, states: Sequence[int], rng: random.Random) -> list[list[int]]:
    """c[j] = base_{state(w)}( g^(j mod 5)( p[j] ) ), one random base per state."""
    g = order5(rng)
    powers = [list(range(N_RUNES))]
    for _ in range(4):
        powers.append([g[x] for x in powers[-1]])
    bases = {s: rng.sample(range(N_RUNES), N_RUNES) for s in set(states)}
    return [
        [bases[s][powers[j % 5][p]] for j, p in enumerate(word)]
        for word, s in zip(plain, states)
    ]


def state_sequences(plain, rng: random.Random) -> dict[str, list[int]]:
    """Word-state sequences of each model, as integers.

    public   the clock (A - w) mod 29, computable from the ciphertext alone
    secret   a coordinate the solver cannot compute: either the previous word's
             gematria sum mod 29 (plaintext-driven) or a keyed draw per word
    """
    lengths = [len(w) for w in plain]
    steps = [0]
    for length in lengths:
        steps.append(steps[-1] + length)
    public = [(steps[w] - w) % N_RUNES for w in range(len(plain))]
    gematria = [0] + [sum(GP_VALUE[r] for r in word) % N_RUNES for word in plain[:-1]]
    keyed = {}
    keyed_seq = [
        keyed.setdefault(w % 8191, rng.randrange(N_RUNES)) for w in range(len(plain))
    ]
    out = {
        "generic walk (no recurrence)": list(range(len(plain))),
        "public clock only (29)": public,
        "previous-word gematria only (29)": gematria,
        "public x gematria (841)": [a * N_RUNES + b for a, b in zip(public, gematria)],
        "public x keyed (841)": [a * N_RUNES + b for a, b in zip(public, keyed_seq)],
    }
    for n_states in (500, 2000, 4205, 20000):
        out[f"unstructured, {n_states} states"] = [
            rng.randrange(n_states) for _ in plain
        ]
    for n_states in (300, 500, 850, 1200, 2000, 4205, 20000):
        out[f"automaton, {n_states} states"] = automaton(plain, n_states)
    return out


def automaton(plain, n_states: int) -> list[int]:
    """A deterministic plaintext-driven state: s' = (3s + gematria + length) mod n.

    The transition rule matters more than the state count. If the state advances
    deterministically from the plaintext, two occurrences of one phrase in the same
    state stay in step across it, so a repeated word carries the next word with it.
    If instead the states are independent per word, a two-word repeat needs two
    coincidences and is about N times rarer.
    """
    states, s = [], 0
    for word in plain:
        states.append(s)
        s = (3 * s + sum(GP_VALUE[r] for r in word) + len(word)) % n_states
    return states


def self_test() -> None:
    # words as tuples of rune indices
    words = [
        (1, 2, 3),
        (4, 5, 6),
        (7, 8),
        (1, 2, 3),
        (4, 5, 6),
        (9, 9, 1, 2),
        (1, 2, 3),
    ]
    got = recurrence_counts(words)
    # (1,2,3) occurs three times -> 3 pairs; (4,5,6) twice -> 1 pair
    assert got["identical"] == 4, got
    assert got["long"] == 0, got
    # the two-word phrase (1,2,3)(4,5,6) occurs twice -> one return
    assert got["returns"] == 1, got

    long_words = [(1, 2, 3, 4), (5, 6), (1, 2, 3, 4), (5, 6), (5, 6)]
    got = recurrence_counts(long_words)
    assert got["long"] == 1 and got["identical"] == 1, got
    # (1,2,3,4)(5,6) occurs twice -> one return; (5,6)(5,6) is only 4 runes
    assert got["returns"] == 1, got

    # every rune equal inside each clock bucket -> reading of exactly 29
    same = [(0,)] * 40
    assert abs(clock_reading(same) - N_RUNES) < 1e-9
    print("self-test passed")


def lp_words() -> list[list[int]]:
    stream, wid = load_clean()
    words: list[list[int]] = [[] for _ in range(wid[-1] + 1)]
    for rune, w in zip(stream, wid):
        words[w].append(rune)
    return words


def run(draws: int = 40) -> None:
    """Each model's four statistics over `draws` prose corpora, against the LP."""
    corpus = lp_words()
    observed = recurrence_counts(corpus)
    print(f"LP: returns {observed['returns']}, identical {observed['identical']}, ")
    print(f"    long {observed['long']}, clock {clock_reading(corpus):.4f}\n")
    print(f"{'model':<34}{'returns':>10}{'identical':>13}{'long':>11}{'clock':>15}")
    rng = random.Random(3301)
    plains = prose_corpora(len(corpus), draws)
    print(f"{'plaintext (no cipher)':<34}", end="")
    stats = [recurrence_counts(p) for p in plains]
    for key in ("returns", "identical", "long"):
        values = [t[key] for t in stats]
        print(
            f"{mean(values):>10.1f}" if key == "returns" else f"{mean(values):>13.1f}",
            end="",
        )
    print(f"{mean([clock_reading(p) for p in plains]):>15.4f}")
    for name, _ in state_sequences(plains[0], random.Random(0)).items():
        rows = []
        for plain in plains:
            states = state_sequences(plain, rng)[name]
            cipher = encipher(plain, states, rng)
            row = recurrence_counts(cipher)
            row["clock"] = clock_reading(cipher)
            rows.append(row)
        cells = []
        for key, width in (
            ("returns", 10),
            ("identical", 13),
            ("long", 11),
            ("clock", 15),
        ):
            values = [r[key] for r in rows]
            digits = 4 if key == "clock" else 1
            cells.append(
                f"{mean(values):.{digits}f}±{stdev(values):.{digits}f}".rjust(width)
            )
        print(f"{name:<34}" + "".join(cells), flush=True)


def fit(draws: int = 260) -> None:
    """Does a state space that fits the word repeats also produce the phrase return?

    The three counts are correlated: a repetitive corpus raises all of them, so the
    plain conjunction of three tails understates every model. The word-repeat counts
    are what pin the number of states, so the test is conditional. Among corpora
    whose identical and long counts land at or below the LP's, how often does a
    two-word return occur?
    """
    corpus = lp_words()
    observed = recurrence_counts(corpus)
    print(
        f"LP: returns {observed['returns']}, identical {observed['identical']}, "
        f"long {observed['long']}"
    )
    print(f"{draws} prose corpora per model, {len(_prose_books())} registers\n")
    print(
        f"{'model':<30}{'identical':>12}{'P(word counts fit)':>20}"
        f"{'P(return)':>12}{'P(return | fit)':>18}"
    )
    rng = random.Random(3301)
    plains = prose_corpora(len(corpus), draws)
    names = ["generic walk (no recurrence)"]
    names += [
        f"automaton, {n} states" for n in (300, 500, 850, 1200, 2000, 4205, 20000)
    ]
    for name in names:
        rows = []
        for plain in plains:
            states = state_sequences(plain, rng)[name]
            rows.append(recurrence_counts(encipher(plain, states, rng)))
        fits = [
            r
            for r in rows
            if r["identical"] <= observed["identical"] and r["long"] <= observed["long"]
        ]
        share = len(fits) / len(rows)
        returned = (
            mean([r["returns"] >= observed["returns"] for r in fits])
            if fits
            else float("nan")
        )
        every = mean([r["returns"] >= observed["returns"] for r in rows])
        print(
            f"{name:<30}{mean([r['identical'] for r in rows]):>12.1f}"
            f"{share:>20.3f}{every:>12.3f}{returned:>18.3f}",
            flush=True,
        )
    print(
        "\nThe generic walk's simulated return rate is an upper bound: its 2,928 states"
        "\nare all distinct, so a return needs two DIFFERENT bases to agree on six"
        "\npoints, which has probability 3e-9 per repeated phrase, about 1.4e-6 in all."
    )


if __name__ == "__main__":
    if "--run" in sys.argv:
        run()
    elif "--fit" in sys.argv:
        fit()
    else:
        self_test()
