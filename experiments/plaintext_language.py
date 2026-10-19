# ABOUTME: Spells prose in ten non-English languages in runes and compares its word
# ABOUTME: lengths and within-word lag-5 repeat rate with the body's blocks.
"""Is the body's plaintext English?

Every plaintext reference in this repository is English: Gutenberg prose and the
author's own solved pages. Two body facts resist an English plaintext:

  * the length marginal has a hole at 2 -- 0.1588 of blocks against 0.2420 for the
    author and >= 0.184 for 22 English registers (`block-lengths-have-a-hole-at-two.md`);
  * the blocks carry little serial length order (`separators-are-not-word-boundaries.md`).

Both are key-free, and both depend on the language. This script spells other
languages' prose with the book's own rules (`c3301.encode_english`, with umlauts as
AE/OE/UE digraphs and other accents dropped) and measures, on disjoint windows of the
body's 2,928 words:

  frac1..3  share of words of 1, 2, 3 runes
  mean      mean word length in runes
  chi2      two-sample chi2 of the length marginal (1..12+) against the body
  r1        correlation of consecutive word lengths
  d5w       within-word rate of p_j == p_(j+5)

The body's d5w is the walk's leak of the plaintext rate, diluted by any clock
perturbation, so the plaintext's own d5w must be at least the body's within error.

`--serial` compares the body's lag-1 length correlation with the author's own pages,
before and after the joining of short units that fits the marginal
(`short-units-are-written-joined.md`). Lengths are centred within chunks the size of
the author's mean page, for every corpus alike, because centring within a short page
biases the correlation by about -1/n and the bias must be the same on both sides.

Run with no arguments for the self-test, `--run` for the table.
"""

from __future__ import annotations

import collections
import random
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from block_length_shape import merged, page_lengths, register  # noqa: E402
from external_text_length_match import fetch  # noqa: E402
from fingerprint_battery import lp_words, prose_corpora  # noqa: E402

from aldegonde import c3301  # noqa: E402

WINDOW = 2928
CAP = 12

# Project Gutenberg prose, two or more books per language; scripture and verse left out
BOOKS = {
    "Latin": (218, 18837, 33849, 23306, 51812),
    "German": (2188, 2335, 2336),
    "French": (796, 799, 798),
    "Dutch": (6712, 3455, 6748),
    "Italian": (7151, 6887, 7121),
    "Spanish": (2000, 320),
    "Swedish": (9827, 10117, 13371),
    "Danish": (10686, 11139),
    "Finnish": (8494, 10481, 10863),
    "Esperanto": (11511, 17482, 8224),
}

UMLAUTS = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "æ": "ae", "ø": "oe", "å": "aa"}
WORD = re.compile(r"[^\W\d_]+")


def ascii_word(word: str) -> str:
    """Umlauts as two letters, every other accent dropped."""
    word = "".join(UMLAUTS.get(ch, ch) for ch in word.lower())
    return unicodedata.normalize("NFKD", word).encode("ascii", "ignore").decode()


def body_text(text: str) -> str:
    """The book without the Gutenberg licence: between the START and END markers."""
    start = text.find("*** START")
    end = text.find("*** END")
    if start != -1 and end != -1:
        text = text[text.find("\n", start) : end]
    # drop the first and last tenth too, which removes front matter and indexes
    # at whitespace, so that no word is cut in two
    cut = len(text) // 10
    start = text.find(" ", cut)
    end = text.rfind(" ", 0, len(text) - cut)
    return text[start:end]


def rune_words(text: str) -> list[list[int]]:
    out = []
    for token in WORD.findall(body_text(text)):
        runes = c3301.encode_english(ascii_word(token))
        if runes:
            out.append(runes)
    return out


def windows(words: list[list[int]]) -> list[list[list[int]]]:
    return [words[i : i + WINDOW] for i in range(0, len(words) - WINDOW + 1, WINDOW)]


def histogram(lengths) -> np.ndarray:
    c = collections.Counter(min(x, CAP) for x in lengths)
    return np.array([c[k] for k in range(1, CAP + 1)], float)


def measures(words) -> dict[str, float]:
    lengths = [len(w) for w in words]
    h = histogram(lengths)
    n = h.sum()
    hits = total = 0
    for w in words:
        for j in range(len(w) - 5):
            total += 1
            hits += w[j] == w[j + 5]
    return {
        "frac1": h[0] / n,
        "frac2": h[1] / n,
        "frac3": h[2] / n,
        "mean": float(np.mean(lengths)),
        "r1": float(np.corrcoef(lengths[:-1], lengths[1:])[0, 1]),
        "d5w": hits / total,
    }


def chi2_two_sample(a: np.ndarray, b: np.ndarray) -> float:
    """Two-sample chi2 between count vectors, over cells where either is non-zero."""
    na, nb = a.sum(), b.sum()
    keep = (a + b) > 0
    a, b = a[keep], b[keep]
    pooled = (a + b) / (na + nb)
    ea, eb = pooled * na, pooled * nb
    return float(((a - ea) ** 2 / ea).sum() + ((b - eb) ** 2 / eb).sum())


def self_test() -> None:
    assert ascii_word("Größe") == "groesse"
    assert ascii_word("éàç") == "eac"
    # the book's spelling: TH and ING are one rune each
    assert len(c3301.encode_english("thing")) == 2
    text = "*** START OF X ***\n" + "der die das und ist " * 20000 + "\n*** END OF X"
    words = rune_words(text)
    assert {len(w) for w in words} == {3}, "der, die, das, und and ist are 3 runes"
    assert len(windows(words)) == len(words) // WINDOW
    m = measures([[1, 2, 3, 4, 5, 1], [7, 7], [1, 2, 3]])
    assert m["d5w"] == 1.0 and m["frac2"] == 1 / 3
    assert abs(m["r1"] + 1.0) < 1e-12, "lengths 6, 2, 3 alternate perfectly"
    # centring within chunks: a chunk alternating long and short is perfectly negative
    assert abs(centred_r1([[2, 6, 2, 6, 2, 6]]) + 1.0) < 0.25
    print("self-test passed")


def row(name: str, wins, body_hist) -> None:
    ms = [measures(w) for w in wins]
    pooled = sum(histogram([len(x) for x in w]) for w in wins)
    # scale to one window so chi2 is comparable across references of different size
    scaled = pooled / len(wins)
    chi = chi2_two_sample(np.round(scaled), body_hist)
    cells = []
    for key in ("frac1", "frac2", "frac3", "mean", "r1", "d5w"):
        v = np.array([m[key] for m in ms])
        sd = v.std(ddof=1) if len(v) > 1 else float("nan")
        cells.append(f"{v.mean():.4f}({sd:.4f})")
    print(
        f"{name:<22}{len(wins):>4}"
        + "".join(c.rjust(17) for c in cells)
        + f"{chi:>9.1f}"
    )


def run() -> None:
    body = lp_words()
    body_hist = histogram([len(w) for w in body])
    b = measures(body)
    head = ("frac1", "frac2", "frac3", "mean", "r1", "d5w")
    print(
        f"{'reference':<22}{'win':>4}"
        + "".join(h.rjust(17) for h in head)
        + f"{'chi2':>9}"
    )
    print(f"{'BODY':<22}{1:>4}" + "".join(f"{b[h]:.4f}".rjust(17) for h in head))
    author = register().word_lengths()
    a = histogram(author)
    print(
        f"{'author (lengths only)':<22}{'':>4}"
        f"{a[0] / a.sum():>17.4f}{a[1] / a.sum():>17.4f}{a[2] / a.sum():>17.4f}"
        f"{np.mean(author):>17.4f}"
    )
    row("English prose", prose_corpora(WINDOW, 20), body_hist)
    summary = {}
    for language, numbers in BOOKS.items():
        everything = []
        for number in numbers:
            text = fetch(number)
            if text is None:
                print(f"{language} pg{number}: not fetched")
                continue
            words = rune_words(text)
            wins = windows(words)
            if not wins:
                continue
            row(f"{language} pg{number}", wins, body_hist)
            everything += wins
        if everything:
            summary[language] = [measures(w) for w in everything]
    print(
        f"\nchi2 has {CAP - 1} df; 5% critical value 19.7. The English prose row is "
        "the reference the repo already uses."
    )
    print("\nper language, all windows pooled: share of 2-rune words and d5w")
    for language, ms in summary.items():
        f2 = np.array([m["frac2"] for m in ms])
        d5 = np.array([m["d5w"] for m in ms])
        print(
            f"  {language:<10} frac2 {f2.mean():.4f} [{f2.min():.4f}, {f2.max():.4f}]"
            f"   d5w {d5.mean():.4f} [{d5.min():.4f}, {d5.max():.4f}]"
        )
    print(f"  {'BODY':<10} frac2 {b['frac2']:.4f}   d5w {b['d5w']:.4f}")


def centred_r1(chunks: list[list[int]]) -> float:
    """Lag-1 correlation of lengths, each chunk centred on its own mean."""
    sxy = sxx = syy = 0.0
    for chunk in chunks:
        a = np.array(chunk, float)
        a -= a.mean()
        sxy += float((a[:-1] * a[1:]).sum())
        sxx += float((a[:-1] ** 2).sum())
        syy += float((a[1:] ** 2).sum())
    return sxy / np.sqrt(sxx * syy)


def jackknife_se(chunks, statistic) -> float:
    n = len(chunks)
    values = [statistic(chunks[:i] + chunks[i + 1 :]) for i in range(n)]
    return float(np.sqrt((n - 1) / n * np.sum((values - np.mean(values)) ** 2)))


def serial(joins: int = 200, q: float = 0.40) -> None:
    rng = random.Random(5)
    author = page_lengths(register())
    size = round(np.mean([len(p) for p in author]))

    def chunks(lengths):
        return [lengths[i : i + size] for i in range(0, len(lengths) - size + 1, size)]

    body = chunks([len(w) for w in lp_words()])
    b, b_se = centred_r1(body), jackknife_se(body, centred_r1)
    a, a_se = centred_r1(author), jackknife_se(author, centred_r1)
    joined = [centred_r1([merged(p, 2, q, rng) for p in author]) for _ in range(joins)]
    j, j_sd = float(np.mean(joined)), float(np.std(joined))
    j_se = float(np.hypot(a_se, j_sd))
    prose = [[len(w) for w in p] for p in prose_corpora(WINDOW, 20)]
    pr = [centred_r1(chunks(p)) for p in prose]
    pj = [centred_r1(chunks(merged(p, 2, q, rng))) for p in prose]
    print(f"lag-1 length correlation, centred in chunks of {size} words\n")
    print(f"  body                        {b:+.4f} +- {b_se:.4f}  ({len(body)} chunks)")
    print(f"  author, 16 solved pages     {a:+.4f} +- {a_se:.4f}  (jackknife)")
    print(
        f"  author, 2-rune units joined at q = {q:.2f}"
        f"  {j:+.4f} +- {j_se:.4f}  (jackknife and join spread)"
    )
    print(f"  English prose               {np.mean(pr):+.4f} +- {np.std(pr):.4f}")
    print(f"  English prose, joined       {np.mean(pj):+.4f} +- {np.std(pj):.4f}")
    za = (b - a) / np.hypot(b_se, a_se)
    zj = (b - j) / np.hypot(b_se, j_se)
    print(f"\n  body against author: {za:+.2f} sigma; against author joined: {zj:+.2f}")


if __name__ == "__main__":
    if "--serial" in sys.argv:
        serial()
    elif "--run" in sys.argv:
        run()
    else:
        self_test()
