#!/usr/bin/env python3
"""Liber Primus period-5 interruptor attack.

Follow-up to examples/lp_lag5_analysis.py: the lag-5 digraph excess in the
unsolved pages is consistent with a 5-element key schedule applied with
irregular interruptors. This script attacks that hypothesis directly and
EXCLUDES it for the shift-cipher family, and (by detection) for general
period-5 polyalphabetic substitution, under all tested key schedules.

Method
------
For shift-family ciphers the five key elements decouple per coset, so
instead of enumerating 29^5 keys each coset is solved independently by
unigram chi-square against runeglish frequencies, and the resulting full
decryption is scored with runeglish trigrams. This works whenever the
key-phase sequence is computable from ciphertext alone, which holds for:

  * plain period-5 (no interruptor)
  * "skip:R"  -- ciphertext rune R is an interruptor: emitted literally,
                 key does not advance (the rule used on solved LP pages)
  * "reset:R" -- ciphertext rune R resets the key phase to 0
  * "word"/"sent" -- key restarts at each word / sentence

Cipher families: additive (c = p + k, covers Vigenere and variant-Beaufort)
and reflective (c = k - p, covers Beaufort and atbash-composed shifts).

Calibration
-----------
Significance is measured against a doublet-preserving null: the page's
lag-1 delta stream is shuffled and the random walk rebuilt. This matters --
against a naive shuffle null every real page scores high simply because the
corpus lacks adjacent doublets, which is exactly how this attack produced
plausible-looking false positives before the null was fixed.

A positive control (the known page-57 plaintext encrypted with a random
5-shift key and an interruptor) is cracked exactly -- key and full
plaintext recovered -- at only 95 runes, with z ~ +7 against the strict
null. Real pages top out around z = +3 over 6710 attack runs: noise.

A second sweep tests mean coset IOC under every phase rule (aggregated
over all pages, against the same null). This detects ANY period-5
polyalphabetic substitution, including Quagmire-style keyed alphabets,
without needing to solve it. No rule scores above the multiple-testing
threshold.

Runtime: a few minutes for the full sweep.
"""

from __future__ import annotations

import math
import os
import random
import statistics
from collections import Counter

from aldegonde import c3301

ENG = c3301.CICADA_ENGLISH_ALPHABET
R2I = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
R2I["ᛂ"] = R2I["ᛄ"]  # the ngram tables use the variant J rune

PERIOD = 5
NULL_TRIALS = 8

PhaseRule = tuple[str, int | None]
Page = tuple[list[int], list[bool], list[bool]]  # runes, word starts, sentence starts


def data_path(*parts: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "..", *parts)


def load_ngrams(fname: str) -> dict[tuple[int, ...], int]:
    """Load a runeglish n-gram table as index tuples -> counts."""
    table: dict[tuple[int, ...], int] = {}
    path = data_path("src", "aldegonde", "data", "ngrams", "runeglish", fname)
    with open(path, encoding="utf-8") as f:
        for line in f:
            gram, count = line.split()
            table[tuple(R2I[ch] for ch in gram)] = int(count)
    return table


UNIGRAMS = load_ngrams("unigrams.txt")
UNITOTAL = sum(UNIGRAMS.values())
UNIPROB = [UNIGRAMS.get((i,), 1) / UNITOTAL for i in range(29)]

TRIGRAMS = load_ngrams("trigrams.txt")
TRITOTAL = sum(TRIGRAMS.values())
TRILOG = {k: math.log10(v / TRITOTAL) for k, v in TRIGRAMS.items()}
TRIFLOOR = math.log10(0.01 / TRITOTAL)


def trigram_score(seq: list[int]) -> float:
    """Mean trigram log10 probability of a decryption."""
    if len(seq) < 3:
        return 0.0
    total = sum(
        TRILOG.get(tuple(seq[i : i + 3]), TRIFLOOR) for i in range(len(seq) - 2)
    )
    return total / (len(seq) - 2)


def load_pages() -> list[Page]:
    """Unsolved pages 0-55 with word- and sentence-start flags."""
    with open(data_path("data", "page0-58.txt"), encoding="utf-8") as f:
        text = f.read()
    pages: list[Page] = []
    for raw in text.split("%")[:56]:
        runes: list[int] = []
        wstart: list[bool] = []
        sstart: list[bool] = []
        new_word = True
        new_sent = True
        for ch in raw.replace("/", "").replace("\n", ""):
            if ch in R2I:
                runes.append(R2I[ch])
                wstart.append(new_word)
                sstart.append(new_sent)
                new_word = new_sent = False
            elif ch in "-.,;:!?":
                new_word = True
                if ch == ".":
                    new_sent = True
        pages.append((runes, wstart, sstart))
    return pages


def phase_sequence(
    page: Page, rule: PhaseRule, period: int = PERIOD
) -> tuple[list[int], list[bool]]:
    """Key phase per position and a mask of literal (interruptor) positions."""
    runes, wstart, sstart = page
    kind, trigger = rule
    ph: list[int] = []
    literal: list[bool] = []
    k = 0
    for i, r in enumerate(runes):
        if kind == "skip" and r == trigger:
            ph.append(-1)
            literal.append(True)
            continue
        if kind == "reset" and r == trigger:
            k = 0
        if kind == "word" and wstart[i]:
            k = 0
        if kind == "sent" and sstart[i]:
            k = 0
        ph.append(k % period)
        literal.append(False)
        k += 1
    return ph, literal


def solve_cosets(
    runes: list[int],
    ph: list[int],
    literal: list[bool],
    family: str,
    period: int = PERIOD,
) -> tuple[list[int], list[int]]:
    """Chi-square best shift per coset; return decryption and shifts."""
    shifts: list[int] = []
    for c in range(period):
        coset = [r for r, p in zip(runes, ph) if p == c]
        n = len(coset)
        if n == 0:
            shifts.append(0)
            continue
        counts = Counter(coset)
        best, best_chi = 0, math.inf
        for s in range(29):
            chi = 0.0
            for sym in range(29):
                csym = (sym + s) % 29 if family == "add" else (s - sym) % 29
                expected = n * UNIPROB[sym]
                chi += (counts.get(csym, 0) - expected) ** 2 / expected
            if chi < best_chi:
                best_chi, best = chi, s
        shifts.append(best)
    decryption = [
        r if lit else ((r - shifts[p]) % 29 if family == "add" else (shifts[p] - r) % 29)
        for r, p, lit in zip(runes, ph, literal)
    ]
    return decryption, shifts


def attack(page: Page, rule: PhaseRule, family: str) -> tuple[float, list[int], list[int]]:
    """Run one attack: returns (trigram score, shifts, decryption)."""
    ph, literal = phase_sequence(page, rule)
    decryption, shifts = solve_cosets(page[0], ph, literal, family)
    return trigram_score(decryption), shifts, decryption


def delta_null_page(page: Page, rng: random.Random) -> Page:
    """Null page preserving the no-doublet random-walk structure."""
    runes, wstart, sstart = page
    deltas = [(runes[i + 1] - runes[i]) % 29 for i in range(len(runes) - 1)]
    rng.shuffle(deltas)
    out = [rng.randrange(29)]
    for d in deltas:
        out.append((out[-1] + d) % 29)
    return out, wstart, sstart


def null_zscore(
    page: Page, rule: PhaseRule, family: str, score: float, trials: int = NULL_TRIALS
) -> float:
    """Z-score of an attack score against the doublet-preserving null."""
    rng = random.Random(99)
    nulls = [attack(delta_null_page(page, rng), rule, family)[0] for _ in range(trials)]
    sd = statistics.stdev(nulls) or 1e-9
    return (score - statistics.mean(nulls)) / sd


def all_rules() -> list[PhaseRule]:
    rules: list[PhaseRule] = [("none", None), ("word", None), ("sent", None)]
    rules += [("skip", r) for r in range(29)]
    rules += [("reset", r) for r in range(29)]
    return rules


def rule_name(rule: PhaseRule) -> str:
    return rule[0] if rule[1] is None else f"{rule[0]}:{ENG[rule[1]]}"


def positive_control() -> None:
    """Encrypt the known page-57 plaintext and verify the attack cracks it."""
    print("=== positive control ===")
    with open(data_path("data", "page0-58.txt"), encoding="utf-8") as f:
        plaintext = [R2I[c] for c in f.read().split("%")[57] if c in R2I]
    rng = random.Random(7)
    key = [rng.randrange(29) for _ in range(PERIOD)]
    ciphertext: list[int] = []
    k = 0
    for p in plaintext:
        if p == 0:  # plaintext F: emitted literally, key pauses
            ciphertext.append(0)
            continue
        ciphertext.append((p + key[k % PERIOD]) % 29)
        k += 1
    flags = [False] * len(ciphertext)
    page: Page = (ciphertext, flags, flags)
    score, shifts, decryption = attack(page, ("skip", 0), "add")
    z = null_zscore(page, ("skip", 0), "add", score, trials=20)
    print(f"true key {key} -> recovered {shifts}, z={z:+.2f}")
    print("decryption:", "".join(ENG[x] for x in decryption[:60]))
    assert shifts == key, "positive control failed"


def shift_key_sweep(pages: list[Page]) -> None:
    """Attack every page under every rule and family; report top z-scores.

    Two stages: a cheap screen with NULL_TRIALS null samples (whose z
    estimates have heavy tails), then re-testing the survivors with 80
    null samples for honest significance.
    """
    print("\n=== shift-key attack sweep (doublet-preserving null) ===")
    results = []
    for pi, page in enumerate(pages):
        if len(page[0]) < 60:
            continue
        for rule in all_rules():
            for family in ("add", "ref"):
                score, shifts, decryption = attack(page, rule, family)
                z = null_zscore(page, rule, family, score)
                results.append((z, pi, page, rule, family, score, decryption))
    results.sort(key=lambda r: -r[0])
    print(f"{len(results)} attack runs; top 10 after verification (80 nulls):")
    verified = []
    for _, pi, page, rule, family, score, decryption in results[:20]:
        z = null_zscore(page, rule, family, score, trials=80)
        verified.append((z, pi, rule, family, decryption))
    verified.sort(key=lambda r: -r[0])
    for z, pi, rule, family, decryption in verified[:10]:
        text = "".join(ENG[x] for x in decryption[:50])
        print(f"z={z:+5.2f} page {pi:2d} {family} {rule_name(rule):10s} {text}")
    print(
        f"verified max={verified[0][0]:.2f} over {len(results)} runs"
        f" (a real crack scores z>+7 at 95 runes, cf. positive control)",
    )


def coset_ioc(page: Page, rule: PhaseRule) -> list[float]:
    """Normalized IOC of each coset under a phase rule."""
    ph, _ = phase_sequence(page, rule)
    out = []
    for c in range(PERIOD):
        coset = [r for r, p in zip(page[0], ph) if p == c]
        n = len(coset)
        if n < 15:
            continue
        counts = Counter(coset)
        out.append(sum(v * (v - 1) for v in counts.values()) / (n * (n - 1)) * 29)
    return out


def quagmire_detector(pages: list[Page]) -> None:
    """Mean coset IOC per rule vs null: detects ANY period-5 polyalphabetic."""
    print("\n=== period-5 polyalphabetic detector (coset IOC, all rules) ===")
    rng = random.Random(5)
    rows = []
    for rule in all_rules():
        real: list[float] = []
        null: list[float] = []
        for page in pages:
            if len(page[0]) < 60:
                continue
            real += coset_ioc(page, rule)
            for _ in range(3):
                null += coset_ioc(delta_null_page(page, rng), rule)
        se = statistics.stdev(null) / math.sqrt(len(real))
        z = (statistics.mean(real) - statistics.mean(null)) / se
        rows.append((z, rule))
    rows.sort(key=lambda r: -r[0])
    for z, rule in rows[:5]:
        print(f"{rule_name(rule):11s} z={z:+5.2f}")
    print(f"({len(rows)} rules; significance threshold for this many tests ~ z=3.2)")


def main() -> None:
    positive_control()
    pages = load_pages()
    shift_key_sweep(pages)
    quagmire_detector(pages)


if __name__ == "__main__":
    main()
