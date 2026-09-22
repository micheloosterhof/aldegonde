# ABOUTME: Bounds the author's own short-word joining rate directly from solved plaintext
# ABOUTME: and tests depletion as an alternative to joining for the body's 2-rune deficit.
"""The author never joins two words. The body joins one short unit in three.

`short-units-are-written-joined.md` rests on two things this file measures directly for
the first time.

**"The front matter does not do it"** was an inference from its 2-rune fraction sitting
at the median of English registers. That is indirect: a text could join and still land
there. The solved pages can be read instead. Their ciphers preserve position, so the
plaintext splices back into each page's own separator layout, and every separated unit
can be checked against a dictionary and against the author's own vocabulary.

A join is counted only when a unit is **not** an English word and **does** split into two
words the author writes separately elsewhere, each used at least twice. That is strict on
purpose: a loose test flags AND as AN+D and WITHIN as WITH+IN.

    units on the 16 solved pages                          723
    units of two runes or less                            204   (28.2%)
    strict join candidates                                  0
    the same detector, on his text joined at q = 0.40      45

Zero against forty-five. The detector is not blind -- it finds 45 of the ~82 joins that
q = 0.40 would create, so it is about half sensitive, and seeing none puts the author's
rate at **q < 0.015** by the rule of three. The body's fitted rate is **27x** that.

His most common short units are the reason the question mattered: THE (43), TO (23),
IS (22), A (19), WE (18), OF (9). He writes every one of them separately.

**Reading 3 gets its first real test.** That file lists as its surviving alternative
"the deficit is not joining at all but some other process that happens to leave the same
marginal", and notes that nothing else measured does. Depletion is the obvious candidate
-- the body's plaintext simply carrying fewer function words -- and it is now measured.
Both models take one free parameter and start from the author's own 723 words:

| model | fitted | chi2 over 13 length cells |
|---|---|---|
| **joining**: a unit of <= 2 runes merges with the next | q = 0.35 | **20.2** |
| **depletion**: a unit of <= 2 runes is simply absent | d = 0.40 | **63.9** |

Depletion is rejected. It has to renormalise the whole distribution upward, so it
over-predicts lengths 3 and 4 and under-predicts everything past 7, where joining puts
the merged mass. The deficit at two really is merging.

So the tension sharpens rather than resolving: the body's lengths are the author's own
words with a third of the short ones merged, and the author demonstrably does not merge.

    python does_the_author_ever_join.py
"""

from __future__ import annotations

import collections
import json
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import (  # noqa: E402
    MASTER,
    PLAIN_PAGES,
    TRIPLES,
    word_lengths,
)
from what_the_marks_are import blocks_with  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET
DICT = Path("/usr/share/dict/web2")
MAX_LENGTH = 12
JOIN_RATE = 0.40  # the body's fitted rate, for the sensitivity check


def solved_units() -> list[tuple[str, int]]:
    """(letters, runes) for every separator-delimited unit of the solved pages.

    The ciphers on these pages preserve position, so the recorded plaintext can be laid
    back into the ciphertext's own separator layout one rune at a time.
    """
    pages = MASTER.read_text().split("%")
    triples = {t["page"]: t for t in json.loads(TRIPLES.read_text())}
    out: list[tuple[str, int]] = []
    for n in sorted(set(PLAIN_PAGES) | set(triples)):
        source = pages[n]
        letters = (
            [ENGLISH[i] for i in triples[n]["plaintext_runes"]]
            if n in triples
            else [
                ENGLISH[c3301.CICADA_ALPHABET.index(c)] for c in source if RUNE.match(c)
            ]
        )
        current: list[str] = []
        taken = runes = 0
        for ch in source:
            if RUNE.match(ch):
                if taken < len(letters):
                    current.append(letters[taken])
                    taken += 1
                runes += 1
            elif ch in "/\n":
                continue
            elif ch in c3301.WORD_BOUNDARY:
                if current:
                    out.append(("".join(current), runes))
                    current, runes = [], 0
        if current:
            out.append(("".join(current), runes))
    return out


def english_words() -> set[str]:
    return {w.strip().upper() for w in DICT.read_text().splitlines()}


def spellings(unit: str) -> set[str]:
    """The transcription writes V as U, K as C, drops I before NG, and Q as C."""
    out = {unit, unit.replace("U", "V"), unit.replace("C", "K")}
    out.add(unit.replace("U", "V").replace("C", "K"))
    for w in list(out):
        if "NG" in w:
            out.add(w.replace("NG", "ING"))
        out.update({w.replace("C", "QU"), w + "S", w + "E"})
    return out


def make_join_detector(vocabulary, words):
    """A unit counts as joined only if it is no word itself but is two words he uses."""

    def known(unit: str) -> bool:
        return bool(spellings(unit) & words)

    def detect(unit: str):
        if known(unit):
            return None
        for i in range(1, len(unit)):
            head, tail = unit[:i], unit[i:]
            if (
                vocabulary.get(head, 0) >= 2
                and vocabulary.get(tail, 0) >= 2
                and known(head)
                and known(tail)
            ):
                return head, tail
        return None

    return detect


def join(lengths, q, rng):
    out = list(lengths)
    i = 0
    while i < len(out):
        if out[i] <= 2 and rng.random() < q and i + 1 < len(out):
            out[i] += out.pop(i + 1)
            continue
        i += 1
    return out


def deplete(lengths, d, rng):
    return [n for n in lengths if not (n <= 2 and rng.random() < d)]


def histogram(values) -> np.ndarray:
    counts = np.zeros(MAX_LENGTH + 1)
    for v in values:
        counts[min(int(v), MAX_LENGTH)] += 1
    return counts / counts.sum()


def fit(model, grid, author, body_hist, n_body):
    """Best parameter by chi-square, carrying the reference's own sampling error."""
    best = None
    for p in grid:
        rng = random.Random(11)
        draws = [histogram(model(author, p, rng)) for _ in range(120)]
        mean, sd = np.mean(draws, axis=0), np.std(draws, axis=0, ddof=1)
        se = np.sqrt(sd**2 + body_hist * (1 - body_hist) / n_body)
        chi = float(np.sum(((body_hist - mean) / np.maximum(se, 1e-6)) ** 2))
        if best is None or chi < best[1]:
            best = (p, chi, mean)
    return best


def main() -> None:
    units = solved_units()
    vocabulary = collections.Counter(w for w, _ in units)
    detect = make_join_detector(vocabulary, english_words())
    found = [(w, detect(w)) for w, _ in units if detect(w)]
    short = sum(1 for _, n in units if n <= 2)

    print("Does the author ever write two words as one unit?\n")
    print(f"  units on the 16 solved pages          {len(units):>5}")
    print(
        f"  units of two runes or less            {short:>5}   ({short / len(units):.1%})"
    )
    print(f"  strict join candidates                {len(found):>5}")
    for w, parts in found[:10]:
        print(f"      {w} -> {parts}")

    rng = random.Random(3301)
    flagged = []
    for _ in range(200):
        out, i = list(units), 0
        while i < len(out):
            word, runes = out[i]
            if runes <= 2 and rng.random() < JOIN_RATE and i + 1 < len(out):
                nxt, more = out[i + 1]
                out[i] = (word + nxt, runes + more)
                out.pop(i + 1)
                continue
            i += 1
        flagged.append(sum(1 for w, _ in out if detect(w)))
    sensitivity = float(np.mean(flagged))
    print(
        f"\n  the same detector, on his text joined at q = {JOIN_RATE}"
        f"   {sensitivity:>5.0f}"
    )
    print(f"\n  95% upper bound on the author's q (rule of three): {3 / short:.3f}")
    print(f"  the body's fitted rate is {0.35 / (3 / short):.0f}x that bound")
    print(
        f"\n  his most common short units: "
        f"{[w for w, n in collections.Counter(w for w, k in units if k <= 2).most_common(6)]}"
    )

    author = word_lengths()
    body = [n for n, _, _ in blocks_with(set("④⑬③⑩"))]
    body_hist = histogram(body)
    grid = [round(x, 2) for x in np.arange(0.10, 0.75, 0.05)]
    q, chi_join, mean_join = fit(join, grid, author, body_hist, len(body))
    d, chi_deplete, mean_deplete = fit(deplete, grid, author, body_hist, len(body))

    print("\n\nIs the deficit at two a merge, or simply fewer short words?\n")
    print(f"{'model':<44}{'fitted':>8}{'chi2':>9}")
    print(f"{'joining: a <=2 unit merges with the next':<44}{q:>8.2f}{chi_join:>9.1f}")
    print(f"{'depletion: a <=2 unit is simply absent':<44}{d:>8.2f}{chi_deplete:>9.1f}")
    print(
        f"\n{'length':>7}{'the body':>10}{'the author':>12}{'joined':>9}{'depleted':>10}"
    )
    author_hist = histogram(author)
    for n in range(1, 11):
        print(
            f"{n:>7}{body_hist[n]:>10.4f}{author_hist[n]:>12.4f}"
            f"{mean_join[n]:>9.4f}{mean_deplete[n]:>10.4f}"
        )

    print(
        "\nDepletion has to renormalise the whole distribution upward, so it over-predicts"
        "\nlengths 3 and 4 and under-predicts past 7, where joining puts the merged mass."
        "\nThe deficit really is a merge -- and the author demonstrably does not merge."
    )


if __name__ == "__main__":
    main()
