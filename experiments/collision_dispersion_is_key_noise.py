# ABOUTME: Tests whether per-block collision dispersion separates words from cuts, and
# ABOUTME: finds the statistic is dominated by key-to-key variance rather than plaintext.
"""A channel that looks rich, scores five sigma on one key, and is empty.

The within-block collision count is an appealing target. Summed over every lag there are
**811 collisions across 2,896 blocks** in the body -- an order of magnitude more events
than the 86 doublets that four earlier ticks foundered on -- and the count *per block*
carries dispersion information the lag marginals throw away. Real words repeat letters in
structured ways; arbitrary cuts of a rune stream should not.

The null has to carry the per-lag rates, because they differ enormously:

    lag    1      2      3      4      5      6      7
    rate 0.0063 0.0348 0.0371 0.0405 0.0494 0.0248 0.0410

A single pooled rate gets the variance wrong. With the per-lag rates, and one key:

    enciphered real words         var/mean 1.922   null 1.642 +- 0.071   z = +3.94
    enciphered arbitrary cuts     var/mean 1.502   null 1.593 +- 0.069   z = -1.32
    THE BODY                      var/mean 1.408   null 1.500 +- 0.063   z = -1.45

Five sigma of separation, with the corpus sitting squarely on the cuts. That would run
against `blocks-are-still-words.md`.

**It is one key.** Across six:

| plaintext structure | z |
|---|---|
| real words | -0.38 +- 3.22 |
| words joined at q = 0.35 | -0.41 +- 3.35 |
| arbitrary cuts, same lengths | -0.58 +- 1.95 |
| **the body** | **-1.40** |

The three bands overlap completely and all contain the corpus. The key-to-key spread is
about 3 sigma; the difference between words and cuts is about 0.2. The statistic measures
the key, not the plaintext.

## Two traps this walked into

- **A control that was not one.** The first version built the "cuts" by concatenating the
  words and cutting at the *original* word lengths, which reproduces the words exactly --
  words and cuts returned identical numbers to three decimals. Shuffling the length
  sequence first fixes it: 5 of 2,896 cut blocks then coincide with a word.
- **One key.** `vary-the-key-not-just-the-corpus` is the standing rule and this is a clean
  instance: the single-key run showed +3.94 against -1.32 and would have been a finding.

## What this leaves

The channel is closed, not unresolved. It is not a matter of needing more data -- 811
events are plenty -- but that the quantity varies more with the key than with the thing
being tested. Recorded so it is not retried.

    python collision_dispersion_is_key_noise.py [--keys 6]
"""

from __future__ import annotations

import collections
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import N_RUNES, order5, prose_corpora  # noqa: E402
from does_the_cipher_restart import body_blocks  # noqa: E402

BLOCKS = 2896
JOIN_RATE = 0.35
RAW = prose_corpora(3400, 1)[0]


def lag_rates(blocks):
    hits, totals = collections.Counter(), collections.Counter()
    for word in blocks:
        for i in range(len(word)):
            for j in range(i + 1, len(word)):
                totals[j - i] += 1
                hits[j - i] += word[i] == word[j]
    return {k: (hits[k] / totals[k] if totals[k] else 0.0) for k in totals}, totals


def dispersion(blocks, rates, draws=150, seed=7):
    """Variance-to-mean of the per-block collision count, against a per-lag null."""
    counts = [
        sum(1 for i in range(len(w)) for j in range(i + 1, len(w)) if w[i] == w[j])
        for w in blocks
    ]
    rng = np.random.default_rng(seed)
    sims = []
    for _ in range(draws):
        drawn = []
        for word in blocks:
            total = 0
            for i in range(len(word)):
                for j in range(i + 1, len(word)):
                    if rng.random() < rates.get(j - i, 1 / N_RUNES):
                        total += 1
            drawn.append(total)
        sims.append(np.var(drawn, ddof=1) / max(np.mean(drawn), 1e-9))
    sims = np.array(sims)
    observed = np.var(counts, ddof=1) / np.mean(counts)
    return observed, sims.mean(), sims.std(ddof=1)


def compose(p, q):
    return [p[q[i]] for i in range(len(p))]


def power(p, k):
    out = list(range(len(p)))
    for _ in range(k):
        out = compose(p, out)
    return out


def encipher(plain, seed, phi=0.90):
    rng = random.Random(seed)
    g = order5(rng)
    powers = [power(g, k) for k in range(5)]
    sigma = rng.sample(range(N_RUNES), N_RUNES)
    base = rng.sample(range(N_RUNES), N_RUNES)
    out, clock, previous = [], 0, None
    for word in plain:
        emitted = []
        for p in word:
            c = base[powers[clock % 5][p]]
            if c == previous and rng.random() < phi:
                clock += 1
                c = base[powers[clock % 5][p]]
            emitted.append(c)
            previous = c
            clock += 1
        out.append(emitted)
        base = compose(base, compose(powers[(clock - 1) % 5], sigma))
    return out


def words(_seed):
    return [list(w) for w in RAW][:BLOCKS]


def joined(seed):
    rng = random.Random(500 + seed)
    out = [list(w) for w in RAW]
    i = 0
    while i < len(out):
        if len(out[i]) <= 2 and rng.random() < JOIN_RATE and i + 1 < len(out):
            out[i] = out[i] + out.pop(i + 1)
            continue
        i += 1
    return out[:BLOCKS]


def cuts(seed):
    """The same rune stream and the same length distribution, cut off the boundaries."""
    rng = random.Random(900 + seed)
    source = joined(seed)
    stream = [r for w in source for r in w]
    lengths = [len(w) for w in source]
    rng.shuffle(lengths)
    out, k = [], 0
    for length in lengths:
        if k + length > len(stream):
            break
        out.append(stream[k : k + length])
        k += length
    return out


def main() -> None:
    keys = 6
    for i, arg in enumerate(sys.argv):
        if arg == "--keys" and i + 1 < len(sys.argv):
            keys = int(sys.argv[i + 1])

    body = [b for b, _ in body_blocks(set())]
    rates, totals = lag_rates(body)
    print("The body's within-block collision rate by lag, which the null must carry.\n")
    print(f"{'lag':>4}{'pairs':>8}{'rate':>9}")
    for k in sorted(totals):
        if totals[k] >= 150:
            print(f"{k:>4}{totals[k]:>8}{rates[k]:>9.4f}")
    events = sum(
        1
        for w in body
        for i in range(len(w))
        for j in range(i + 1, len(w))
        if w[i] == w[j]
    )
    print(f"\n{events} collisions across {len(body)} blocks.")

    print("\nOne key, which is how this nearly became a finding.\n")
    print(f"{'corpus':<30}{'var/mean':>10}{'per-lag null':>18}{'z':>8}")
    for label, builder in (
        ("enciphered real words", words),
        ("enciphered arbitrary cuts", cuts),
    ):
        corpus = encipher(builder(0), 11)
        o, m, s = dispersion(corpus, lag_rates(corpus)[0])
        print(f"{label:<30}{o:>10.3f}{f'{m:.3f} +- {s:.3f}':>18}{(o - m) / s:>+8.2f}")
    o, m, s = dispersion(body, rates)
    print(f"{'THE BODY':<30}{o:>10.3f}{f'{m:.3f} +- {s:.3f}':>18}{(o - m) / s:>+8.2f}")

    print(f"\nAcross {keys} keys, which is what the standing rule requires.\n")
    print(f"{'plaintext structure':<34}{'z':>18}")
    for label, builder in (
        ("real words", words),
        (f"words joined at q = {JOIN_RATE}", joined),
        ("arbitrary cuts, same lengths", cuts),
    ):
        zs = []
        for seed in range(keys):
            corpus = encipher(builder(seed), 11 + seed)
            o, m, s = dispersion(corpus, lag_rates(corpus)[0])
            zs.append((o - m) / s)
        zs = np.array(zs)
        print(f"{label:<34}{f'{zs.mean():+.2f} +- {zs.std(ddof=1):.2f}':>18}")
    o, m, s = dispersion(body, rates)
    print(f"{'THE BODY':<34}{(o - m) / s:>+18.2f}")

    print(
        "\nThe three bands overlap completely and all contain the corpus. The key-to-key"
        "\nspread is about 3 sigma and the words-against-cuts difference about 0.2, so the"
        "\nstatistic measures the key rather than the plaintext. The channel is closed --"
        "\nnot for want of data, since 811 events are ample, but because the quantity"
        "\nvaries more with the key than with the thing being tested."
    )


if __name__ == "__main__":
    main()
