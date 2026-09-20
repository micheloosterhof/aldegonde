# ABOUTME: Tests the runes at a fixed position within each word for periodicity in the
# ABOUTME: word index, the cleanest probe of the per-word base schedule.
"""Is the per-word base periodic in the word index?

Michel's question (September 2026): take the first rune of every word and measure its
index of coincidence, then split by even and odd words, then by words 1, 2, 3 in
threes, and so on.

It is the right place to look. Under the length-clocked walk the first rune of a word
is `c = base_w(p_0)` with the letter step at phase zero, so word-initial runes are
enciphered by the base ALONE. Any periodicity in the base schedule shows there
undiluted, where the full stream mixes it with five letter-step phases. If the base
repeated with period k, the words in one residue class mod k would share an alphabet
and their initial runes would read as a monoalphabet, nIoC about 1.7 rather than 1.0.

The null is a shuffle of the word ORDER, keeping the same multiset of runes, so the
comparison is against "these runes in no particular order" rather than against a
uniform alphabet.

**Result (2026-09-20): no pattern, at any modulus from 2 to 80.**

    1st rune   plain nIoC 0.9985   even/odd z -0.71   threes +0.08   fives +1.94
    2nd rune              0.9975              -0.08           -0.91         +0.86
    3rd rune              0.9962              -0.70           -0.65         -1.56

The largest |z| across all 79 moduli is 2.48, 2.72 and 2.36 for the three positions,
where chance over that many tests gives about 2.96. Every value is inside the noise.

One near-miss is worth recording because it looked like something. Multiples of 5
leaned positive for the first rune (mean z +0.65) and the second (+0.92), which is
tempting given period 5 is the corpus's known structure. It does not survive: for the
THIRD rune the same set leans NEGATIVE (-0.70). A real period-5 base schedule would
push every within-word position the same way, so a lean that flips sign with position
is noise.

**Reviewed with a stronger test (same day).** Bucketing 2,928 word-initial runes is
weak. Comparing words `k` apart at every matched within-word position gives ~9,300
pairs per gap, a third of the standard error, and settles it:

  * gap 5 reads 0.0353 against chance 0.0345, z = +0.45. A strict period-5 base would
    read the plaintext rate, about 0.060; the observation bounds base-sharing at gap 5
    below **16%**, against the 100% a period requires.
  * multiples of 5 average z -0.143, slightly BELOW chance, against +0.005 elsewhere.
  * gap 15 is the one cell that surfaced in both tests (z = +2.61 bucketed, +2.70 here)
    and is positive in both halves of the corpus. It is still not a period: gaps 30, 45
    and 60 read z = +0.05, +1.03 and -3.07. A real period returns at its multiples.

So the fives are nothing, and the moral stands -- a pattern noticed in a scan has to be
re-tested on a channel that was not used to notice it, and preferably with a test that
has the power to see it.

Run with no arguments.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import lp_words  # noqa: E402

M = 29
MODULI = list(range(2, 81))
DRAWS = 200


def nioc(runes: np.ndarray) -> float:
    if len(runes) < 2:
        return float("nan")
    counts = np.bincount(runes, minlength=M)
    return float((counts * (counts - 1)).sum() / (len(runes) * (len(runes) - 1)) * M)


def bucketed(stream: np.ndarray, k: int) -> float:
    """Mean nIoC inside residue classes of the word index mod k."""
    return float(np.nanmean([nioc(stream[i::k]) for i in range(k)]))


def gap_coincidence(words, gap: int) -> tuple[float, float, int]:
    """Coincidence of words `gap` apart at matched within-word positions.

    Far more powerful than bucketing the word-initial stream: it pools every position,
    giving about 9,300 pairs per gap against 2,928 word-initial runes, so the standard
    error is roughly a third. If words `gap` apart shared a base their runes at a
    common position would coincide at the plaintext rate, about 0.060, not at 1/29.
    """
    hits = total = 0
    for w in range(len(words) - gap):
        a, b = words[w], words[w + gap]
        for j in range(min(len(a), len(b))):
            total += 1
            hits += a[j] == b[j]
    rate = hits / total
    z = (rate - 1.0 / M) / np.sqrt(rate * (1 - rate) / total)
    return rate, z, total


def gap_scan() -> None:
    """The direct test, and whether any flagged gap behaves like a real period."""
    words = lp_words()
    rows = [(k, *gap_coincidence(words, k)) for k in range(1, 61)]
    z = np.array([r[2] for r in rows])
    print(f"\ndirect word-gap test, ~{rows[0][3]:,} matched-position pairs per gap")
    print(f"chance {1 / M:.4f}; a shared base would read about 0.060\n")
    print(f"{'gap':>5}{'rate':>9}{'z':>7}      {'gap':>5}{'rate':>9}{'z':>7}")
    for k, rate, zz, _ in rows[:8]:
        other = rows[k + 7]
        print(
            f"{k:>5}{rate:>9.4f}{zz:>7.2f}      "
            f"{other[0]:>5}{other[1]:>9.4f}{other[2]:>7.2f}"
        )
    peak = int(np.abs(z).argmax())
    print(
        f"\nlargest |z| over 60 gaps: {np.abs(z).max():.2f} at gap {rows[peak][0]} "
        f"(chance expects ~{np.sqrt(2 * np.log(60)):.2f})"
    )
    by5 = np.array([r[0] % 5 == 0 for r in rows])
    print(
        f"mean z at multiples of 5: {z[by5].mean():+.3f}   elsewhere {z[~by5].mean():+.3f}"
    )
    print("\na real period lights up its multiples too:")
    for p in (5, 15):
        cells = "   ".join(
            f"gap {p * m}: z {rows[p * m - 1][2]:+.2f}"
            for m in (1, 2, 3)
            if p * m <= 60
        )
        print(f"   period {p:>2} -> {cells}")


def main() -> None:
    words = lp_words()
    rng = np.random.default_rng(3301)
    print(f"{len(words)} words; nIoC 1.00 is flat, about 1.7 is one alphabet\n")
    for position, label in (
        (0, "1st rune of each word"),
        (1, "2nd rune"),
        (2, "3rd rune"),
    ):
        stream = np.array([w[position] for w in words if len(w) > position])
        observed = np.array([bucketed(stream, k) for k in MODULI])
        null = np.array(
            [
                [bucketed(rng.permutation(stream), k) for k in MODULI]
                for _ in range(DRAWS)
            ]
        )
        z = (observed - null.mean(axis=0)) / null.std(axis=0)
        by5 = np.array([k % 5 == 0 for k in MODULI])
        peak = int(np.abs(z).argmax())
        print(f"{label}: plain nIoC {nioc(stream):.4f}, {len(stream)} runes")
        print(
            f"   even/odd (k=2) z {z[0]:+.2f}    threes (k=3) z {z[1]:+.2f}"
            f"    fives (k=5) z {z[3]:+.2f}"
        )
        print(
            f"   largest |z| over {len(MODULI)} moduli: {np.abs(z).max():.2f} at k={MODULI[peak]}"
        )
        print(
            f"   mean z at multiples of 5: {z[by5].mean():+.3f}   elsewhere {z[~by5].mean():+.3f}"
        )
    print(
        f"\nexpected largest |z| over {len(MODULI)} moduli by chance: "
        f"{np.sqrt(2 * np.log(len(MODULI))):.2f}"
    )
    gap_scan()


if __name__ == "__main__":
    main()
