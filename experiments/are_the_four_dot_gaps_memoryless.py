# ABOUTME: Tests whether the four-dot gap law is exponential (a memoryless placement) or
# ABOUTME: English-sentence-shaped, which is positive evidence rather than a missing signature.
"""Is the four-dot placed by a process with no memory?

Everything established about the four-dot so far is an absence: no lengthening before it,
no line-break coupling, no match to any English punctuation class, no key switch. Absences
are consistent with many things. The gap law is a chance at positive evidence, because the
two readings predict different *shapes*, not different means.

- **A memoryless placement** -- a mark dropped at a constant rate per block, for whatever
  reason -- gives geometric gaps, coefficient of variation 1, and a mode at the shortest
  gap. Short gaps are common.
- **Sentence boundaries** do not. English sentences have a mode away from zero: one- and
  two-word sentences are rare, so very short gaps are rare.

`mark_forensics.py` records the four-dot gap cv at **1.09** in runes, which is
exponential. `marks-are-not-clause-punctuation.md` records **0.79** in words and reads it
as consistent with English -- but that file's spacing argument is **withdrawn**, because
its control pooled the author's plaintext pages with still-enciphered ones. So the
question is open and the two figures have never been reconciled.

## Method

The gaps are counted in **blocks**, and every reference is joined at q = 0.40 first, so
the units match: a body span of 21 blocks is more than 21 plaintext words.

Three arms, each rescaled to the observed mean so the test is about shape alone:

- geometric, the memoryless arm;
- ten English registers' sentences, joined;
- the LP author's own spans, joined.

Scored by binned multinomial log-likelihood, with a positive control that draws n = 137
from each arm and checks the test names the right one.

## Result: not memoryless, not English sentences, and cv is the wrong summary

Gaps counted in blocks: 137 of them, mean 21.40, median 14, **cv 1.03**.

| arm | cv | 1-3 | 4-7 | 8-14 | 15-24 | 25-39 | 40+ |
|---|---|---|---|---|---|---|---|
| **the body** | **1.03** | **9** | 27 | 33 | 28 | 23 | 17 |
| memoryless (geometric) | 0.98 | 18.4 | 20.7 | 27.8 | 26.8 | 22.1 | 21.2 |
| English sentences, joined | 0.82 | 3.7 | 18.5 | 36.4 | 36.8 | 24.7 | 16.9 |
| the LP author's spans | 0.73 | 8.7 | 19.1 | 30.6 | 32.1 | 33.5 | 13.0 |

**The cv of 1.03 does not mean the process is memoryless.** It is inflated by the long
tail, and the short end says the opposite: the body has **9 gaps of three blocks or less
against the 18.4 a constant-rate placement predicts**, about 2.2 sigma low. A mark dropped
at a fixed rate per block would produce short gaps twice as often as this.

Binned log-likelihood of the body's gaps:

| arm | log-likelihood | ratio |
|---|---|---|
| the LP author's spans | -240.52 | 1.000 |
| memoryless (geometric) | -241.08 | 0.571 |
| English sentences, joined | -242.11 | 0.203 |

**Nothing is decisive.** 1.75 to 1 over memoryless and 4.9 to 1 over English sentences is
not a verdict, and the body sits between the arms: it has the author's short-gap deficit
(9 against his 8.7, where English predicts 3.7) and a heavier long tail than either.

The test has power. Drawing 137 gaps from each arm, it names the right one 92-98% of the
time with median likelihood ratios of 50 to 6,000. So the indecision is the body's, not
the instrument's.

## What this settles

The three cv figures on record -- 1.09 in runes (`mark_forensics.py`), 0.79 in words
(`marks-are-not-clause-punctuation.md`, whose spacing argument is withdrawn) and 1.03 in
blocks here -- are not in conflict. They are different units and different filters, and
**none of them should be read as a shape.** The bin table is the statistic; the cv is not.

The positive content is small and real: **the four-dot is not dropped at a constant rate.**
Whatever places it avoids placing two close together, which a memoryless process would not.

    python are_the_four_dot_gaps_memoryless.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from are_the_two_marks_one_system import body_stream, gaps_between  # noqa: E402
from final_lengthening_across_registers import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import author_spans  # noqa: E402

BINS = ((1, 3), (4, 7), (8, 14), (15, 24), (25, 39), (40, 10**6))
DRAWS = 400
FLOOR = 1e-4


def rescaled(sample, target_mean, rng, n=200000):
    """Draw from an empirical shape, rescaled to the target mean."""
    a = np.array(sample, float)
    scale = target_mean / a.mean()
    return np.maximum(1, np.round(rng.choice(a, size=n) * scale))


def geometric(target_mean, rng, n=200000):
    p = 1.0 / target_mean
    return np.maximum(1, rng.geometric(p, size=n))


def bin_probs(sample) -> np.ndarray:
    a = np.asarray(sample, float)
    p = np.array([((a >= lo) & (a <= hi)).mean() for lo, hi in BINS])
    return np.maximum(p, FLOOR) / np.maximum(p, FLOOR).sum()


def counts(sample) -> np.ndarray:
    a = np.asarray(sample, float)
    return np.array([int(((a >= lo) & (a <= hi)).sum()) for lo, hi in BINS])


def loglik(observed_counts, probs) -> float:
    return float((observed_counts * np.log(probs)).sum())


def main() -> None:
    rng = np.random.default_rng(3301)
    stream = body_stream()
    gaps = np.array(gaps_between(stream, "④"), float)
    mean = gaps.mean()
    print(
        f"{len(gaps)} four-dot gaps in blocks: mean {mean:.2f}, median "
        f"{np.median(gaps):.0f}, cv {gaps.std(ddof=1) / mean:.2f}\n"
    )

    py_rng = random.Random(3301)
    registers = [
        register_spans(p, py_rng)
        for p in (fetch(n) for n in REGISTERS)
        if p is not None
    ]
    english = [len(s) for r in registers for s in r]
    author = [len(s) for s in author_spans()]
    arms = {
        "memoryless (geometric)": geometric(mean, rng),
        "English sentences, joined": rescaled(english, mean, rng),
        "the LP author's spans": rescaled(author, mean, rng),
    }
    print(f"{'arm':<28}{'cv':>7}" + "".join(f"{f'{lo}-{hi}' if hi < 1000 else f'{lo}+':>9}" for lo, hi in BINS))
    print(f"{'the body':<28}{gaps.std(ddof=1) / mean:>7.2f}" + "".join(f"{c:>9}" for c in counts(gaps)))
    for label, sample in arms.items():
        p = bin_probs(sample)
        cv = np.std(sample, ddof=1) / np.mean(sample)
        print(
            f"{label:<28}{cv:>7.2f}"
            + "".join(f"{x * len(gaps):>9.1f}" for x in p)
        )

    obs = counts(gaps)
    lls = {label: loglik(obs, bin_probs(s)) for label, s in arms.items()}
    print("\nBinned log-likelihood of the body's gaps under each arm.\n")
    print(f"{'arm':<28}{'log-likelihood':>16}{'ratio vs best':>16}")
    best = max(lls.values())
    for label, ll in sorted(lls.items(), key=lambda kv: -kv[1]):
        print(f"{label:<28}{ll:>16.2f}{math.exp(ll - best):>16.3f}")

    print("\nControl: draw 137 gaps from each arm and see which the test names.\n")
    print(f"{'drawn from':<28}{'named correctly':>18}{'median LR':>12}")
    for truth, sample in arms.items():
        right, ratios = 0, []
        probs = {label: bin_probs(s) for label, s in arms.items()}
        for _ in range(DRAWS):
            draw = rng.choice(sample, size=len(gaps))
            c = counts(draw)
            scores = {label: loglik(c, p) for label, p in probs.items()}
            pick = max(scores, key=scores.get)
            right += pick == truth
            ordered = sorted(scores.values(), reverse=True)
            ratios.append(math.exp(ordered[0] - ordered[1]))
        print(f"{truth:<28}{right / DRAWS:>18.2f}{np.median(ratios):>12.1f}")


if __name__ == "__main__":
    main()
