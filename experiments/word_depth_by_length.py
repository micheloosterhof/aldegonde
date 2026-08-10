# ABOUTME: Extends the 2-rune depth test to every short word length, using
# ABOUTME: wordfreq to measure how often a register repeats a word of each length.
"""Do ciphertext words of the same length agree at all positions together?

`two-rune-depth-no-base-reuse.md` showed the two positions of a 2-rune word
agree independently, which excludes shift-like schedules. The same argument
runs at any word length, and longer words sharpen it:

    C = ( base_w(p0), base_w(g(p1)), base_w(g^2(p2)), ... )

Two words agree at a position when their bases agree at the matching point.
Under any conjugated shift the base difference is fixed-point-free unless the
two shifts are equal, so two words with the same plaintext agree at EVERY
position or none. Under a rich walk the positions agree independently.

Longer words make the full-agreement cell rarer by chance -- (1/29)^L instead
of (1/29)^2 -- so a schedule's collisions stand out against a smaller
background. Working against that, longer words repeat less often in a register,
which is what supplies the collisions in the first place. This script measures
both sides instead of assuming either.

The register repeat rate comes from wordfreq: for each rune length, the
frequency-weighted probability that two tokens of that length are the same
word. That replaces the Cauchy-Schwarz lower bound used for 2-rune words with
a direct measurement.

The null shuffles each position independently across words, preserving every
per-position marginal exactly and destroying only the link between positions.
"""

from __future__ import annotations

import random
import re
import statistics
from collections import Counter
from pathlib import Path

from aldegonde import c3301
from experiments.d5_partial_leak import to_runeglish

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
BOUNDARY = c3301.MARK_CHARS + "%&$" + c3301.NUMERAL_CHARS
N_RUNES = 29
SHIFTS = 29           # states of the schedule being excluded
LENGTHS = (2, 3, 4, 5, 6, 7, 8)
TRIALS = 4000
LEXICON = 60000
SEED = 3301


def lp_words() -> dict[int, list[tuple[int, ...]]]:
    text = "$".join(CORPUS.read_text().split("$")[:10])
    index: dict[str, int] = {}
    out: dict[int, list[tuple[int, ...]]] = {}
    cur: list[int] = []
    for char in text:
        if RUNE.match(char):
            cur.append(index.setdefault(char, len(index)))
        elif char in BOUNDARY and cur:
            out.setdefault(len(cur), []).append(tuple(cur))
            cur = []
    if cur:
        out.setdefault(len(cur), []).append(tuple(cur))
    return out


def register_repeat_rates() -> dict[int, float]:
    """P(two tokens of the same rune length are the same word), by length."""
    from wordfreq import top_n_list, word_frequency

    weight: dict[int, Counter[str]] = {}
    for w in top_n_list("en", LEXICON):
        if not w.isalpha():
            continue
        try:
            runes = to_runeglish(w.upper())
        except (KeyError, ValueError):
            continue
        n = len(runes)
        if n in LENGTHS:
            weight.setdefault(n, Counter())["".join(runes)] += word_frequency(w, "en")
    rates = {}
    for n, counts in weight.items():
        total = sum(counts.values())
        rates[n] = sum((v / total) ** 2 for v in counts.values()) if total else 0.0
    return rates


def poisson_log10_tail(observed: int, mean: float) -> float:
    """log10 P(X <= observed) for X ~ Poisson(mean), computed in log space.

    The Gaussian z of the shuffle null is meaningless once the expected count
    is a handful, so the schedule prediction is tested as a Poisson tail.
    """
    from math import exp, lgamma, log

    if mean <= 0:
        return 0.0
    terms = [-mean + i * log(mean) - lgamma(i + 1) for i in range(observed + 1)]
    peak = max(terms)
    return (peak + log(sum(exp(t - peak) for t in terms))) / log(10) if terms else 0.0


def full_agree(words: list[tuple[int, ...]]) -> int:
    """Pairs agreeing at every position."""
    return sum(v * (v - 1) // 2 for v in Counter(words).values())


def agreement_histogram(words: list[tuple[int, ...]]) -> list[int]:
    """How many pairs agree at 0, 1, ... L positions."""
    length = len(words[0])
    hist = [0] * (length + 1)
    for i, a in enumerate(words):
        for b in words[i + 1:]:
            hist[sum(x == y for x, y in zip(a, b))] += 1
    return hist


def main() -> None:
    rng = random.Random(SEED)
    by_len = lp_words()
    rates = register_repeat_rates()

    print(f"{'len':>4}{'words':>7}{'pairs':>10}{'full: obs':>11}{'null':>9}"
          f"{'sd':>7}{'z':>7}{'repeat rate':>13}{'shift pred':>12}{'log10 P':>10}")
    for length in LENGTHS:
        words = by_len.get(length, [])
        n = len(words)
        if n < 30:
            continue
        pairs = n * (n - 1) // 2
        obs = full_agree(words)

        cols = [[w[k] for w in words] for k in range(length)]
        null = []
        for _ in range(TRIALS):
            for col in cols:
                rng.shuffle(col)
            null.append(full_agree(list(zip(*cols))))
        mu, sd = statistics.mean(null), statistics.pstdev(null)
        # once chance collisions vanish the shuffle sd is 0 and z is undefined;
        # the Poisson tail against the schedule prediction still carries meaning
        zs = f"{(obs - mu) / sd:+7.2f}" if sd else f"{'--':>7}"

        s = rates.get(length, 0.0)
        pred = mu + pairs * s / SHIFTS
        log_p = poisson_log10_tail(obs, pred)
        print(f"{length:>4}{n:>7}{pairs:>10}{obs:>11}{mu:>9.1f}{sd:>7.1f}{zs}"
              f"{s:>13.4f}{pred:>12.1f}{log_p:>10.1f}")

    print("\nlog10 P = Poisson tail P(observed or fewer | shift prediction).")
    print("full = pairs agreeing at EVERY position; null shuffles each position")
    print("independently across words, so it keeps every marginal and breaks only")
    print(f"the link between positions. shift pred = null + pairs x repeat rate / {SHIFTS}.")

    print("\nagreement histograms (how many pairs agree at k of L positions)")
    for length in LENGTHS:
        words = by_len.get(length, [])
        if len(words) < 30:
            continue
        hist = agreement_histogram(words)
        total = sum(hist)
        cells = "  ".join(f"{k}:{v}" for k, v in enumerate(hist))
        print(f"   L={length}  {cells}   (of {total} pairs)")
    print("\nA schedule shows up ONLY in the top cell: partial agreements stay at")
    print("chance because they need the plaintext difference to equal the shift.")


if __name__ == "__main__":
    main()
