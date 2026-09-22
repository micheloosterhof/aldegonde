# ABOUTME: Measures monograph, digraph and trigraph kappa restricted to pairs inside one
# ABOUTME: block, where the base cancels, and prices what each cell can carry.
"""The lag-5 digraph anomaly is inside the words, where the base cancels.

`lag5-digraph-structure.md` records 29 repeated digraphs at distance 5 against 15.4
expected, measured on the body's 12,956 runes with no regard for word boundaries, and
concludes plain digraph kappa is not globally significant -- a max over lags 2..150
reaches +3.47 in 38% of null runs.

The base changes at every block edge, so a digraph straddling one is written under two
alphabets and its coincidence falls to chance. **Lag 5 is not a scan maximum here.** It is
the one lag the model singles out in advance: g has order 5, so `c_i = c_(i+5)` inside a
block holds exactly when `p_i = p_(i+5)`, and every other lag reads a g-twisted relation
instead. That makes this a pre-specified cell, not a look-elsewhere one.

## The g-model passes a check it was not built for

Inside a block the body shows an excess at lag 5 and nowhere else:

    lag           1      2      3      4      5      6      7
    body    -15.24  +0.13  +0.97  +1.83  +3.69  -1.87  +0.95
    English -10.88 +10.95 +82.15 +64.25 +57.07 +60.89 +33.59

English repeats letters within a word at every distance. The body repeats them at distance
five only. That is what a period-5 walk predicts and nothing else does.

## The digraph result

    n  lag   inside hits   pairs   expected       z
    1    5           104   2,105      72.59   +3.69
    2    5             9   1,290       1.53   +6.03
    3    5             1     731       0.03   +5.60

## Where the whole-stream hits sit

The sharpest form needs no rate estimate: of the hits already counted on the raw stream,
how many are inside a block? Inside positions are a known fraction of all positions, so it
is a binomial test on the hits themselves.

    n = 1, lag 5    104 of 479 inside, chance puts 77.9    P = 0.0011
    n = 2, lag 5      9 of  29 inside, chance puts  2.9    P = 0.0015
    n = 3, lag 5      1 of   1 inside, chance puts  0.1    P = 0.0565

**The digraph anomaly is a within-word effect.** The trigraph row is a single hit and is
reported for completeness only -- one hit against an expectation of 0.03 is a one-arm
tail, not evidence.

## The null that matters

A digraph coincidence needs two monograph coincidences, and the monograph rate inside a
block at lag 5 is already 0.0494 against chance 0.0345. So the expectation to beat is the
observed monograph rate squared, not 1/29^2:

    the body    9 hits against 3.15 expected   ratio 2.86   z = +3.30
    English   724 hits against 431.84          ratio 1.68   z = +14.06

Both are super-multiplicative, which is what language does: a repeated digraph is more
likely than two independent repeated letters. The body's ratio is higher than English's
and rests on nine hits, so the two are not distinguishable.

## What it rests on

Nine hits in **eight distinct blocks** -- one block carries a repeated trigraph and so
contributes two overlapping digraph hits. Dropping any single event leaves 8 against 3.15,
z = +2.73. The effect is not one word.

    ᛝᛈᚩᚪᚣᛝᛈ  ᚹᛡᛠᚱᚫᚹᛡ  ᚣᛈᛟᚦᛋᚣᛈ  ᚾᚪᛠᚩᚪᚾᚪ
    ᚪᛝᛈᚦᛈᚪᛝ  ᛈᛋᚦᛁᚳᛈᛋ  ᛋᛞᛝᚷᛚᛋᛞᛝ  ᛖᛋᛇᚦᚦᛖᛋ

Under the model each is a plaintext word with a repeated digraph five apart, which is a
heavy constraint on an English word of that length.

## Power, stated before the numbers are read

    cell                                eligible pairs   expected at chance
    monograph, lag 5, inside a block             2,105                72.59
    digraph,   lag 5, inside a block             1,290                 1.53
    trigraph,  lag 5, inside a block               731                 0.03

The trigraph cell expects one hit per thirty runs of the whole book. It cannot be turned
into a rate and is not read as one here.

    python ngram_kappa_inside_a_word.py
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import BODY, MARKS, MASTER, RUNE, SEPARATORS  # noqa: E402
from d5_partial_leak import to_runeglish  # noqa: E402
from doublet_position_profile import IDX_ENG  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402

MOD = 29
JOIN_RATE = 0.40
SHORT = 2
LAGS = (1, 2, 3, 4, 5, 6, 7, 10)


def body_words() -> list[str]:
    """The body's blocks as rune strings, carrying across line wraps."""
    text = MASTER.read_text().split("%")
    out, cur = [], []
    for ci in BODY:
        for line in re.split(r"[/\n]", text[ci]):
            if not RUNE.search(line):
                continue
            for ch in line:
                if RUNE.match(ch):
                    cur.append(ch)
                elif (ch in MARKS or ch in SEPARATORS) and cur:
                    out.append("".join(cur))
                    cur = []
    if cur:
        out.append("".join(cur))
    return out


def english_words(rng, registers=3) -> list[tuple[int, ...]]:
    """English words as runeglish index tuples, joined the way the body is."""
    words: list[tuple[int, ...]] = []
    for number in REGISTERS[:registers]:
        path = fetch(number)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        trim = len(text) // 10
        for raw in re.findall(r"[A-Za-z']+", text[trim : len(text) - trim]):
            runes = tuple(IDX_ENG[t] for t in to_runeglish(raw.upper()) if t in IDX_ENG)
            if runes:
                words.append(runes)
    joined: list[tuple[int, ...]] = []
    for w in words:
        if joined and len(w) <= SHORT and rng.random() < JOIN_RATE:
            joined[-1] = joined[-1] + w
        else:
            joined.append(w)
    return joined


def inside(words, n: int, lag: int) -> tuple[int, int]:
    """(hits, eligible pairs) for n-gram coincidence at `lag`, both grams in one word."""
    hits = pairs = 0
    for w in words:
        for i in range(len(w) - lag - n + 1):
            pairs += 1
            hits += all(w[i + j] == w[i + lag + j] for j in range(n))
    return hits, pairs


def whole_stream(stream, n: int, lag: int) -> tuple[int, int]:
    pairs = len(stream) - lag - n + 1
    hits = sum(
        all(stream[i + j] == stream[i + lag + j] for j in range(n))
        for i in range(pairs)
    )
    return hits, pairs


def table(label, words, stream) -> None:
    print(f"\n{label}\n")
    print(
        f"{'n':>2}{'lag':>5}{'inside hits':>13}{'pairs':>8}{'expected':>10}{'z':>7}"
        f"{'  |':>3}{'whole hits':>12}{'pairs':>10}{'expected':>10}{'z':>7}"
    )
    for n in (1, 2, 3):
        for lag in LAGS:
            hi, pi = inside(words, n, lag)
            hw, pw = whole_stream(stream, n, lag)
            ei, ew = pi / MOD**n, pw / MOD**n
            zi = (hi - ei) / max(np.sqrt(ei), 1e-9)
            zw = (hw - ew) / max(np.sqrt(ew), 1e-9)
            print(
                f"{n:>2}{lag:>5}{hi:>13,}{pi:>8,}{ei:>10.2f}{zi:>+7.2f}{'  |':>3}"
                f"{hw:>12,}{pw:>10,}{ew:>10.2f}{zw:>+7.2f}"
            )


def localise(words, stream, n: int, lag: int) -> None:
    """Of the whole-stream hits at this cell, how many are inside one block?"""
    hi, pi = inside(words, n, lag)
    hw, pw = whole_stream(stream, n, lag)
    share = pi / pw
    p = stats.binom.sf(hi - 1, hw, share)
    print(
        f"\nn = {n}, lag = {lag}: {hw} hits on the whole stream, {hi} of them inside a"
        f"\n  block. Inside positions are {share:.1%} of all positions, so chance puts"
        f"\n  {hw * share:.1f} there.  P(inside >= {hi}) = {p:.4f}"
    )


def beyond_the_monographs(label, words) -> None:
    """Is the digraph excess more than two elevated monographs multiplied together?

    A digraph coincidence needs two monograph coincidences, and the monograph rate at
    lag 5 is already above chance inside a block. The null that matters is not 1/29^2 but
    the observed monograph rate squared.
    """
    mono_hits, mono_pairs = inside(words, 1, 5)
    di_hits, di_pairs = inside(words, 2, 5)
    rate = mono_hits / mono_pairs
    expected = di_pairs * rate * rate
    z = (di_hits - expected) / np.sqrt(expected)
    print(
        f"\n{label}"
        f"\n  monograph rate inside a block at lag 5: {rate:.4f}"
        f" ({mono_hits:,} of {mono_pairs:,}), chance {1 / MOD:.4f}"
        f"\n  digraph hits {di_hits:,}, expected {expected:.2f} if the two monograph"
        f"\n  coincidences were independent -- ratio {di_hits / expected:.2f}, z = {z:+.2f}"
        f"\n  (against plain chance the expectation is {di_pairs / MOD**2:.2f})"
    )


def main() -> None:
    rng = random.Random(3301)
    words = body_words()
    stream = "".join(words)
    print(f"the body: {len(words):,} blocks, {len(stream):,} runes")
    print(
        "  blocks carry across page breaks as well as line wraps, so this is 32 fewer"
        "\n  than body_parse reports -- see tokenizer-boundaries-need-auditing."
    )

    table("The body.", words, stream)

    print("\nWhere the whole-stream hits sit.")
    localise(words, stream, 1, 5)
    localise(words, stream, 2, 5)
    localise(words, stream, 3, 5)

    beyond_the_monographs("The body, digraphs against elevated monographs.", words)

    english = english_words(rng)
    flat = [x for w in english for x in w]
    print(f"\nEnglish reference: {len(english):,} joined words, {len(flat):,} letters")
    table("English, runeglish, joined at q = 0.40.", english, flat)
    beyond_the_monographs("English, the same comparison.", english)


if __name__ == "__main__":
    main()
