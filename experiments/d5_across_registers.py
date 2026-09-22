# ABOUTME: Confirms across ten registers that the body's plaintext carries English lag-5
# ABOUTME: structure, which sharpens the sentence-edge anomaly rather than easing it.
"""The body's plaintext is English on the one channel that reads plaintext directly.

Under the length-clocked walk `g^5 = id`, so two positions five apart inside a block share
both the alphabet and the base and coincide exactly when the plaintext does. That makes
d5 the only key-free window onto the plaintext itself, and
`dodge_d5_attenuation.py` already used it -- against **one** book, length-matched, at
0.0521.

Ten registers, each length-matched to the body's own block-length distribution so the d5
pairs come from words of the right sizes:

| register | d5 |
|---|---|
| pg1342 | 0.0534 |
| pg205 | 0.0584 |
| pg16643 | 0.0587 |
| pg2945 | 0.0633 |
| pg4363 | 0.0621 |
| pg3296 | 0.0582 |
| pg1497 | 0.0551 |
| pg14209 | 0.0459 |
| pg2680 | 0.0516 |
| pg131 | 0.0512 |
| **across ten** | **0.0558 +- 0.0054** |
| the LP author, 382 pairs | 0.0733 |
| **the body** (ciphertext) | **0.0494 +- 0.0047** |

The preventer attenuates the echo: a skip anywhere in the five intervening steps breaks
the identity, so the observed rate is `(1-q)^5` of the plaintext's plus chance for the
rest. The prediction barely moves over any plausible skip rate:

    q = 0.0000   attenuation 1.000   predicted 0.0558   z = -0.89
    q = 0.0315   attenuation 0.852   predicted 0.0526   z = -0.49
    q = 0.0335   attenuation 0.843   predicted 0.0525   z = -0.47
    q = 0.0400   attenuation 0.815   predicted 0.0519   z = -0.38

**The body sits within half a sigma of English prose**, and the earlier single-book
result holds with a reference ten times wider.

## Why this sharpens the anomaly

Three independent channels now say the body's plaintext is ordinary English:

- **word lengths** -- the author's own distribution with a third of the short units
  merged fits at P = 0.83, where smooth cutting laws are rejected
  (`blocks-are-still-words.md`);
- **function-word content** -- depletion, which would mean a list or invocation register,
  fits at chi2 63.9 against joining's 20.2 (`does_the_author_ever_join.py`);
- **lag-5 structure** -- this file.

So the plaintext is English prose with a normal complement of short function words, and
its sentence-final words nevertheless do not lengthen at the marks
(-0.29 +- 0.20 against a ten-register +1.19 +- 0.28). The register escape is closed from a
third direction: it is not that the body is a different kind of text.

    python d5_across_registers.py
"""

from __future__ import annotations

import collections
import math
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import IDX_ENG, to_runeglish  # noqa: E402
from does_the_cipher_restart import body_blocks  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402

LAG = 5
OVERSAMPLE = (
    6  # draw this many matched words per body block, to shrink the sampling error
)
SKIP_RATES = (
    (0.0000, "no preventer"),
    (0.0315, "gated dodge, 5 x d1"),
    (0.0335, "preventer, q - d1"),
    (0.0400, "unsuppressed walk"),
)


def words_of(path) -> list[list[int]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    trim = len(text) // 10
    out = []
    for word in re.findall(r"[A-Za-z']+", text[trim : len(text) - trim]):
        runes = [IDX_ENG[c] for c in to_runeglish(word.upper()) if c in IDX_ENG]
        if runes:
            out.append(runes)
    return out


def lag_rate(words) -> tuple[int, int]:
    hits = total = 0
    for w in words:
        for i in range(len(w) - LAG):
            total += 1
            hits += w[i] == w[i + LAG]
    return hits, total


def length_matched(words, target, rng):
    """Resample so the length distribution matches the body's blocks.

    d5 pairs come only from words of six runes or more, so an unmatched sample measures
    the wrong words -- which is what `dodge_d5_attenuation.py` found when it compared raw
    prose.
    """
    by_length = collections.defaultdict(list)
    for w in words:
        by_length[len(w)].append(w)
    out = []
    for length, count in target.items():
        pool = by_length.get(length)
        if pool:
            out += [rng.choice(pool) for _ in range(count * OVERSAMPLE)]
    return out


def main() -> None:
    rng = random.Random(3301)
    body = [b for b, _ in body_blocks(set())]
    target = collections.Counter(len(b) for b in body)

    print("Plaintext lag-5 coincidence, length-matched to the body's blocks.\n")
    print(f"{'register':<12}{'pairs':>9}{'d5':>9}")
    rates = []
    for number in REGISTERS:
        path = fetch(number)
        if path is None:
            continue
        hits, total = lag_rate(length_matched(words_of(path), target, rng))
        if total < 500:
            continue
        rates.append(hits / total)
        print(f"pg{number:<10}{total:>9,}{hits / total:>9.4f}")
    rates = np.array(rates)
    plain, plain_se = float(rates.mean()), float(rates.std(ddof=1))
    print(f"{'across ten':<12}{'':>9}{f'{plain:.4f} +- {plain_se:.4f}':>9}")

    hits, total = lag_rate(corpus(keyed=True))
    print(f"{'the author':<12}{total:>9,}{hits / total:>9.4f}")
    hits, total = lag_rate(body)
    observed = hits / total
    observed_se = math.sqrt(observed * (1 - observed) / total)
    print(f"{'the body':<12}{total:>9,}{observed:>9.4f}   (ciphertext, attenuated)")

    print("\nThe preventer attenuates the echo: a skip in any of the five intervening")
    print(
        "steps breaks the identity, so the observed rate is (1-q)^5 of the plaintext's.\n"
    )
    print(f"{'skip rate q':>12}{'attenuation':>13}{'predicted':>12}{'z':>8}   model")
    for q, label in SKIP_RATES:
        attenuation = (1 - q) ** LAG
        predicted = attenuation * plain + (1 - attenuation) / 29
        se = math.hypot(observed_se, attenuation * plain_se)
        print(
            f"{q:>12.4f}{attenuation:>13.3f}{predicted:>12.4f}"
            f"{(observed - predicted) / se:>+8.2f}   {label}"
        )

    print(
        "\nThe body sits within half a sigma of English prose at every plausible skip"
        "\nrate, so the single-book result holds against a reference ten times wider."
        "\n\nThat sharpens the sentence-edge anomaly rather than easing it. Word lengths,"
        "\nfunction-word content and lag-5 structure all say ordinary English prose, and"
        "\nits sentence-final words still do not lengthen at the marks."
    )


if __name__ == "__main__":
    main()
