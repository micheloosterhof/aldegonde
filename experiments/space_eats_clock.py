# ABOUTME: Tests whether the word space consumes clock steps, by looking for the
# ABOUTME: period-5 echo across word boundaries at a distance corrected for the space.
"""Does the space count as an enciphered letter?

Michel's proposal (September 2026): the separator is enciphered like any other letter
and simply not transmitted, so the clock advances an extra `k` steps at every word
boundary. Two runes on opposite sides of a boundary are then further apart on the clock
than they look in the transmitted text:

    clock distance = (transmitted runes between) + k x (boundaries between)

Within words the period-5 echo is plain: distance 5 reads 0.0492 against chance 0.0345,
z = +3.67, because two positions five apart share an alphabet. If the space eats `k`
steps, the same echo should appear across a boundary wherever that total is a multiple
of five.

**Scanning k is one question, not five.** For pairs spanning a single boundary the clock
distance is `gap + k`, so changing `k` only relabels which residue class of the gap
should carry the echo. The test is therefore: pool every cross-word pair by `gap mod 5`
and ask whether any one class is elevated. A class at residue `r` means `k = -r mod 5`.
Pooling this way uses every pair instead of the handful at gap exactly 5, which is where
the power comes from.

**The power is here, unlike at distance 6.** Each residue class holds about 12,000
pairs, against the 1,267 that made the within-word distance-6 test useless. An echo the
size of the within-word one would read z near +8.

**What a positive would mean.** The echo needs a shared ALPHABET and a shared BASE. The
per-word step changes the base at every boundary in every model here, which is what the
flat IoC and the 17 identical words demand, and that alone would kill the cross-word
echo whatever the clock does. So a positive result would say the per-word step is much
weaker than assumed; a negative one leaves the space question open, because the base
change hides the answer.

Run with no arguments.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import M, lp_words  # noqa: E402

CHANCE = 1.0 / M
MAX_RUNE_GAP = 30


def stream_of(words):
    runes, word_of = [], []
    for i, w in enumerate(words):
        runes.extend(w)
        word_of.extend([i] * len(w))
    return runes, word_of


def z_of(hits: int, pairs: int) -> float:
    if not pairs:
        return float("nan")
    return (hits - pairs * CHANCE) / math.sqrt(pairs * CHANCE * (1 - CHANCE))


def two_rate_z(h1: int, n1: int, h2: int, n2: int) -> float:
    """z for rate1 - rate2, the residue class against all the others pooled."""
    if not n1 or not n2:
        return float("nan")
    p = (h1 + h2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return (h1 / n1 - h2 / n2) / se if se else float("nan")


def collect(words):
    """Coincidences by (boundaries crossed, rune gap) up to MAX_RUNE_GAP."""
    runes, word_of = stream_of(words)
    table: dict[tuple[int, int], list[int]] = {}
    for i in range(len(runes)):
        top = min(MAX_RUNE_GAP, len(runes) - i - 1)
        for gap in range(1, top + 1):
            j = i + gap
            key = (word_of[j] - word_of[i], gap)
            cell = table.setdefault(key, [0, 0])
            cell[1] += 1
            cell[0] += runes[i] == runes[j]
    return table


def main() -> None:
    words = lp_words()
    table = collect(words)
    runes, _ = stream_of(words)
    print(f"{len(words)} words, {len(runes)} runes, chance {CHANCE:.5f}")
    print(f"rune gaps up to {MAX_RUNE_GAP}\n")

    within = {g: v for (b, g), v in table.items() if b == 0}
    h5, n5 = within[5]
    print("control -- the echo inside words, which no clock convention can remove:")
    print(f"   gap 5: {h5}/{n5}  {h5 / n5:.4f}  z {z_of(h5, n5):+.2f}")

    # one boundary only: the clock distance is gap + k, so the residue class of the gap
    # is what a non-zero k would pick out. The seam (gap 1) is excluded: the doublet
    # preventer suppresses it by design and it would swamp its own class.
    single = {g: v for (b, g), v in table.items() if b == 1 and g > 1}
    classes = {r: [0, 0] for r in range(5)}
    for gap, (hits, pairs) in single.items():
        cell = classes[gap % 5]
        cell[0] += hits
        cell[1] += pairs

    total_h = sum(c[0] for c in classes.values())
    total_n = sum(c[1] for c in classes.values())
    print(
        f"\ncross-word pairs spanning ONE boundary, seam excluded: "
        f"{total_h}/{total_n} = {total_h / total_n:.4f}\n"
    )
    print(
        f"{'gap mod 5':>10}{'implies skip':>14}{'hits/pairs':>16}"
        f"{'rate':>9}{'z vs chance':>13}{'z vs others':>13}"
    )
    best = None
    for r in range(5):
        hits, pairs = classes[r]
        others_h, others_n = total_h - hits, total_n - pairs
        z_rest = two_rate_z(hits, pairs, others_h, others_n)
        print(
            f"{r:>10}{(-r) % 5:>14}{f'{hits}/{pairs}':>16}"
            f"{hits / pairs:>9.4f}{z_of(hits, pairs):>13.2f}{z_rest:>13.2f}"
        )
        if best is None or z_rest > best[0]:
            best = (z_rest, r)

    excess = h5 / n5 - CHANCE
    per_class = total_n // 5
    detectable = excess * per_class / math.sqrt(per_class * CHANCE * (1 - CHANCE))
    print(
        f"\nthe within-word echo is {excess:+.4f} over chance; at {per_class:,} pairs "
        f"a class\nwould read z {detectable:+.2f}. The largest here is {best[0]:+.2f} "
        f"at residue {best[1]},\nwhere chance over five classes gives about "
        f"{math.sqrt(2 * math.log(5)):.2f}."
    )
    print(
        "\nthe sharper test -- every surviving doublet sitting at one clock phase --"
        "\nis blocked by the preventer's own drift:"
    )
    assert n5 > 1000, "the within-word control needs its pairs"
    assert per_class > 5000, "each residue class should be well populated"
    drift_note(len(runes))


def drift_note(n_runes: int) -> None:
    """The sharper test, and why the doublet preventer blocks it.

    A one-zero schedule lets the preventer fail at exactly one clock phase, so EVERY
    surviving doublet -- the 63 inside words and the 23 at the seam -- should sit at a
    single phase. The phase of a position is the cumulative rune count plus k per word
    boundary, so that concentration would pin k without knowing the alphabet, the
    schedule or the base.

    It cannot be run. The preventer advances the clock whenever it fires, and it fires
    on far more positions than it fails on, so the clock drifts away from the position
    count at the skip rate. Once the accumulated drift passes five the phase is
    scrambled.
    """
    for label, q in (("q = 5 x d1w", 0.031), ("q measured on models", 0.045)):
        runes_to_scramble = 5 / q
        print(
            f"   {label:<22} drift reaches 5 steps after {runes_to_scramble:.0f} runes "
            f"({runes_to_scramble / 4.4:.0f} words) of {n_runes:,}"
        )


if __name__ == "__main__":
    main()
