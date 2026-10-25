# ABOUTME: A zoo of distinct encryption algorithms run on the author's plaintext and
# ABOUTME: scored on the body's fingerprint cells, so constructions can be compared by numbers.
"""Which encryption algorithms produce ciphertext with the body's properties?

Every algorithm here enciphers the same plaintext (the author's register, words cycled
with their order shuffled, 2,928 words) and is scored on the cells the body is measured
on, with the body itself as the first row:

  nIoC        flat unigrams (body 1.000)
  d1w / seam  doublet rate inside words and across the separator (0.0063 / 0.0079)
  trip        triplets (0)
  d2..d6      within-word coincidence at lags 2..6, as multiples of chance; the body
              reads about 1.0 except d5 ~1.4
  d5x         lag-5 coincidence across one separator (~1.0, the echo is inside words)
  kmax        largest |z| of kappa at skips 2..40 (no periodicity)
  ident       identical ciphertext words of three runes or more
  ret         adjacent identical word pairs (the DJU-BEI event; body 1)

The algorithms are built from three parts the ledger forces on any solution, with
alternatives for each, plus controls that drop a part so its signature can be seen:

  letter clock   order-5 permutation g | 5-shift schedule | 5 independent rows |
                 rotor stepping per letter | Trithemius progression (control)
  word chain     product walk | two dials with carry | plaintext-sum accumulator |
                 no change (control)
  preventer      dodge (advance the clock again) | hold (step back) | null rune | none
  scribe         no rule in the cipher; doubled runes written once by the copyist (rate 0.8)

The letter clock runs through the separators for every machine but the walk, whose
chain carries the phase in g^(L-1); a clock that restarts at every word puts every
seam on one phase and the preventer then fails at all seams or none
(`pure-quagmire-word-restart.md`).

    python experiments/cipher_zoo_fingerprint.py [--draws 6]
"""

from __future__ import annotations

import argparse
import collections
import math
import random
import sys
from pathlib import Path
from typing import TYPE_CHECKING

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_tokenized  # noqa: E402
from lp_plaintext_register import corpus as register  # noqa: E402

from aldegonde.maths import permutation as pm  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

M = 29
NULL = 12  # EO, which the author's plaintext never uses; the null symbol where one is needed
Words = list[list[int]]


# ---------------------------------------------------------------- fingerprint
def fingerprint(words: Words) -> dict[str, float]:
    stream = [r for w in words for r in w]
    n = len(stream)
    counts = collections.Counter(stream)
    out: dict[str, float] = {}
    out["nIoC"] = M * sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))
    out["d1w"] = sum(w[i] == w[i + 1] for w in words for i in range(len(w) - 1)) / sum(
        len(w) - 1 for w in words
    )
    out["seam"] = sum(a[-1] == b[0] for a, b in zip(words, words[1:], strict=False)) / (
        len(words) - 1
    )
    out["trip"] = sum(stream[i] == stream[i + 1] == stream[i + 2] for i in range(n - 2))
    for lag in range(2, 7):
        hits = sum(w[i] == w[i + lag] for w in words for i in range(len(w) - lag))
        pairs = sum(max(0, len(w) - lag) for w in words)
        out[f"d{lag}"] = M * hits / pairs
    boundary: list[int] = []
    for w in words:
        boundary += [0] * (len(w) - 1) + [1]
    hits = pairs = 0
    for i in range(n - 5):
        if sum(boundary[i : i + 5]) == 1:
            pairs += 1
            hits += stream[i] == stream[i + 5]
    out["d5x"] = M * hits / pairs
    kmax = 0.0
    for skip in range(2, 41):
        pairs = n - skip
        hits = sum(stream[i] == stream[i + skip] for i in range(pairs))
        kmax = max(kmax, abs((hits - pairs / M) / math.sqrt(pairs / M * (1 - 1 / M))))
    out["kmax"] = kmax
    seen = collections.Counter(tuple(w) for w in words if len(w) >= 3)
    out["ident"] = sum(v * (v - 1) // 2 for v in seen.values())
    pairs_adj = collections.Counter(
        (tuple(a), tuple(b))
        for a, b in zip(words, words[1:], strict=False)
        if len(a) >= 3
    )
    out["ret"] = sum(v * (v - 1) // 2 for v in pairs_adj.values())
    return out


HEADER = (
    f"{'algorithm':<50}{'nIoC':>6}{'d1w':>7}{'seam':>7}{'trip':>5}"
    + "".join(f"{f'd{lag}':>5}" for lag in range(2, 7))
    + f"{'d5x':>5}{'kmax':>6}{'ident':>6}{'ret':>4}"
)


def row(name: str, fp: dict[str, float]) -> str:
    return (
        f"{name:<50}{fp['nIoC']:>6.3f}{fp['d1w']:>7.4f}{fp['seam']:>7.4f}{fp['trip']:>5.0f}"
        + "".join(f"{fp[f'd{lag}']:>5.2f}" for lag in range(2, 7))
        + f"{fp['d5x']:>5.2f}{fp['kmax']:>6.1f}{fp['ident']:>6.0f}{fp['ret']:>4.0f}"
    )


# ---------------------------------------------------------------- plaintext
def plaintext(rng: random.Random, n_words: int) -> Words:
    reg = register()
    words: Words = []
    while len(words) < n_words:
        block = [list(w) for w in reg]
        rng.shuffle(block)
        words += block
    return words[:n_words]


def bigram_table(words: Words) -> list[list[int]]:
    t = [[0] * M for _ in range(M)]
    for w in words:
        for a, b in zip(w, w[1:], strict=False):
            t[a][b] += 1
    return t


def rare_diagonal_order5(
    rng: random.Random, table: list[list[int]], tries: int = 3000
) -> list[int]:
    """The order-5 permutation (five 5-cycles, four fixed) with the least mass on {(g(b), b)}."""
    best: list[int] = []
    best_mass = float("inf")
    for _ in range(tries):
        g = pm.random_with_cycle_type(M, [5, 5, 5, 5, 5], rng)
        mass = sum(table[g[b]][b] for b in range(M))
        if mass < best_mass:
            best, best_mass = g, mass
    return best


def shift(k: int) -> list[int]:
    return [(i + k) % M for i in range(M)]


def compose(*perms: Sequence[int]) -> list[int]:
    """Apply left to right: compose(a, b)[x] = b[a[x]]."""
    out = list(range(M))
    for p in perms:
        out = [p[x] for x in out]
    return out


def scribe(words: Words, rate: float, rng: random.Random) -> Words:
    """Runic orthography applied to the ciphertext: a doubled rune is written once, with
    probability `rate`, across separators as well; a word emptied by it disappears."""
    out: Words = []
    prev = -1
    for w in words:
        cw: list[int] = []
        for r in w:
            if r == prev and rng.random() < rate:
                continue
            cw.append(r)
            prev = r
        if cw:
            out.append(cw)
    return out


# ---------------------------------------------------------------- the generic machine
class Machine:
    """alphabet(word state, letter clock) -> permutation.

    The word state advances once per word through `word_step`; the letter clock once per
    letter, restarting at each word unless `continuous`. A preventer of 'dodge' advances
    the clock again when the output would repeat the previous rune; 'hold' steps it back
    once instead; 'null' emits the null rune under the current alphabet and enciphers the
    letter at the next step; 'none' lets the repeat stand.
    """

    def __init__(
        self,
        alphabet: Callable[[int, int], Sequence[int]],
        *,
        preventer: str,
        continuous: bool = False,
    ) -> None:
        self.alphabet = alphabet
        self.preventer = preventer
        self.continuous = continuous

    def encipher(
        self, words: Words, *, word_step: Callable[[int, int, int], int]
    ) -> Words:
        out: Words = []
        prev = -1
        wstate = 0
        clock = 0
        for w_index, w in enumerate(words):
            if w_index:
                wstate = word_step(w_index, wstate, len(words[w_index - 1]))
            if not self.continuous:
                clock = 0
            cw: list[int] = []
            for p in w:
                c = self.alphabet(wstate, clock)[p]
                if c == prev and self.preventer == "dodge":
                    clock += 1
                    c = self.alphabet(wstate, clock)[p]
                elif c == prev and self.preventer == "hold":
                    clock -= 1
                    c = self.alphabet(wstate, clock)[p]
                elif c == prev and self.preventer == "null":
                    cw.append(self.alphabet(wstate, clock)[NULL])
                    prev = cw[-1]
                    clock += 1
                    c = self.alphabet(wstate, clock)[p]
                cw.append(c)
                prev = c
                clock += 1
            out.append(cw)
        return out


# ---------------------------------------------------------------- algorithms
def zoo(rng: random.Random, words: Words) -> list[tuple[str, Words]]:
    g = rare_diagonal_order5(rng, bigram_table(words))
    g_pow = [list(range(M))]
    for _ in range(4):
        g_pow.append(compose(g_pow[-1], g))
    key = rng.sample(range(M), M)  # one mixed alphabet
    rows = [rng.sample(range(M), M) for _ in range(5)]  # five independent mixed rows
    rotors = [rng.sample(range(M), M) for _ in range(3)]
    sigma = rng.sample(range(M), M)
    # increments summing to 0 mod 29, so the shift has period 5; the zero makes a dodge fail one time in five
    deltas = [0, 7, 11, 19, 21]
    cum = [0]
    for d in deltas[:-1]:
        cum.append(cum[-1] + d)
    sums = [0]
    for w in words:
        sums.append(sums[-1] + sum(w))
    results: list[tuple[str, Words]] = []

    # --- the walk: base_w ∘ g^clock, the base chained by g^(L-1) ∘ σ
    bases: dict[int, list[int]] = {}

    def walk_alphabet(w: int, clock: int) -> list[int]:
        return compose(g_pow[clock % 5], bases[w])

    def walk_step(w: int, _prev: int, prev_len: int) -> int:
        bases[w] = compose(g_pow[(prev_len - 1) % 5], sigma, bases[w - 1])
        return w

    for prev_name in ("none", "dodge", "hold", "null"):
        bases.clear()
        bases[0] = rng.sample(range(M), M)
        ct = Machine(walk_alphabet, preventer=prev_name).encipher(
            words, word_step=walk_step
        )
        results.append((f"walk: rare order-5 g, σ chain, {prev_name}", ct))

    # --- the walk with an untuned g (median diagonal), dodge: does the preventer alone suffice?
    g_median = pm.random_with_cycle_type(M, [5, 5, 5, 5, 5], rng)
    gm_pow = [list(range(M))]
    for _ in range(4):
        gm_pow.append(compose(gm_pow[-1], g_median))

    def walk_median_alphabet(w: int, clock: int) -> list[int]:
        return compose(gm_pow[clock % 5], bases[w])

    def walk_median_step(w: int, _prev: int, prev_len: int) -> int:
        bases[w] = compose(gm_pow[(prev_len - 1) % 5], sigma, bases[w - 1])
        return w

    bases.clear()
    bases[0] = rng.sample(range(M), M)
    ct = Machine(walk_median_alphabet, preventer="dodge").encipher(
        words, word_step=walk_median_step
    )
    results.append(("walk: untuned g, σ chain, dodge", ct))

    # --- Quagmire with a period-5 increment schedule and two dials with carry
    def quag_alphabet(state: int, clock: int) -> list[int]:
        d1, d2 = state % M, state // M
        return compose(shift(cum[clock % 5] + d1), key, shift(d2))

    def odometer(_w: int, prev: int, _len: int) -> int:
        return (prev + 1) % (M * M)

    # --- Quagmire whose 5-letter keyword has a doubled letter: equal consecutive shifts, so a dodge fails there
    keyword = [4, 4, 17, 9, 25]

    def keyword_alphabet(state: int, clock: int) -> list[int]:
        d1, d2 = state % M, state // M
        return compose(shift(keyword[clock % 5] + d1), key, shift(d2))

    ct = Machine(keyword_alphabet, preventer="dodge", continuous=True).encipher(
        words, word_step=odometer
    )
    results.append(
        ("quagmire: 5-letter keyword with a doubled letter, two dials, dodge", ct)
    )

    # --- Quagmire whose keyword has five distinct letters: the dodge never fails
    keyword2 = [4, 11, 17, 9, 25]

    def keyword2_alphabet(state: int, clock: int) -> list[int]:
        d1, d2 = state % M, state // M
        return compose(shift(keyword2[clock % 5] + d1), key, shift(d2))

    ct = Machine(keyword2_alphabet, preventer="dodge", continuous=True).encipher(
        words, word_step=odometer
    )
    results.append(
        ("quagmire: 5-letter keyword, distinct letters, two dials, dodge", ct)
    )

    for prev_name in ("none", "dodge", "hold", "null"):
        ct = Machine(quag_alphabet, preventer=prev_name, continuous=True).encipher(
            words, word_step=odometer
        )
        results.append(
            (f"quagmire: 5-shift schedule with a zero, two dials, {prev_name}", ct)
        )

    # --- five independent rows by clock phase, two dials
    def rows_alphabet(state: int, clock: int) -> list[int]:
        d1, d2 = state % M, state // M
        return compose(shift(d1), rows[clock % 5], shift(d2))

    for prev_name in ("dodge", "hold", "null"):
        ct = Machine(rows_alphabet, preventer=prev_name, continuous=True).encipher(
            words, word_step=odometer
        )
        results.append((f"five mixed rows by phase, two dials, {prev_name}", ct))

    # --- plaintext-sum accumulator driving dial 1, the word count dial 2
    def accumulator(w: int, _prev: int, _len: int) -> int:
        return (sums[w] % M) + M * (w % M)

    ct = Machine(quag_alphabet, preventer="dodge", continuous=True).encipher(
        words, word_step=accumulator
    )
    results.append(("quagmire, dial 1 = plaintext sum so far, dodge", ct))

    # --- three rotors stepping per letter: no word structure
    def rotor_alphabet(_state: int, clock: int) -> list[int]:
        a, b, c = clock % M, (clock // M) % M, (clock // (M * M)) % M
        return compose(
            shift(a), rotors[0], shift(b - a), rotors[1], shift(c - b), rotors[2]
        )

    ct = Machine(rotor_alphabet, preventer="dodge", continuous=True).encipher(
        words, word_step=lambda *_: 0
    )
    results.append(("three rotors stepping per letter, dodge", ct))

    # --- Trithemius progression inside the clock (no period 5): the echo control
    def trith_alphabet(state: int, clock: int) -> list[int]:
        d1, d2 = state % M, state // M
        return compose(shift((3 * clock) % M + d1), key, shift(d2))

    ct = Machine(trith_alphabet, preventer="dodge", continuous=True).encipher(
        words, word_step=odometer
    )
    results.append(("quagmire, progressive shift +3 per letter, dodge", ct))

    # --- no rule in the cipher at all; the scribe writes a doubled rune once, 80% of the time
    bases.clear()
    bases[0] = rng.sample(range(M), M)
    ct = Machine(walk_median_alphabet, preventer="none").encipher(
        words, word_step=walk_median_step
    )
    results.append(
        (
            "walk, untuned g, no rule; scribe writes doubles once at 0.8",
            scribe(ct, 0.8, rng),
        )
    )
    ct = Machine(keyword2_alphabet, preventer="none", continuous=True).encipher(
        words, word_step=odometer
    )
    results.append(
        (
            "quagmire, distinct-letter keyword, no rule; scribe at 0.8",
            scribe(ct, 0.8, rng),
        )
    )

    # --- the simplest carrier: the 5-rune keyword restarts at every word; two dials; no rule; the copyist
    keyword3 = rng.sample(range(M), 5)

    def restart_alphabet(state: int, clock: int) -> list[int]:
        d1, d2 = state % M, state // M
        return compose(shift(keyword3[clock % 5] + d1), key, shift(d2))

    ct = Machine(restart_alphabet, preventer="none").encipher(words, word_step=odometer)
    results.append(("quagmire, keyword restarting per word, two dials, no rule", ct))
    results.append(("same, scribe writes doubles once at 0.8", scribe(ct, 0.8, rng)))

    # --- one alphabet per word, no letter clock: the monoalphabet-per-word control
    def mono_alphabet(state: int, _clock: int) -> list[int]:
        d1, d2 = state % M, state // M
        return compose(shift(d1), key, shift(d2))

    ct = Machine(mono_alphabet, preventer="dodge").encipher(words, word_step=odometer)
    results.append(("per-word alphabet only, no letter clock, dodge", ct))
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=6)
    args = ap.parse_args()
    body = load_tokenized().words()
    print(HEADER)
    print(row("Liber Primus body", fingerprint(body)))
    rng = random.Random(3301)
    plain = plaintext(rng, len(body))
    print(row("plaintext (register, order shuffled)", fingerprint(plain)))
    acc: dict[str, list[dict[str, float]]] = collections.defaultdict(list)
    for _ in range(args.draws):
        for name, ct in zoo(rng, plain):
            acc[name].append(fingerprint(ct))
    print()
    for name, fps in acc.items():
        mean = {k: sum(fp[k] for fp in fps) / len(fps) for k in fps[0]}
        print(row(name, mean))
    print(
        f"\n{args.draws} key draws per algorithm, averaged. The cycled plaintext repeats every word"
    )
    print("four times, so ident reads the pool of alphabets rather than the body's 17.")


if __name__ == "__main__":
    main()
