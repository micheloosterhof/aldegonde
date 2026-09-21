# ABOUTME: Asks whether the LP's distance-6 deficit is a real relation or too few pairs,
# ABOUTME: and whether it extends to the rest of the 1-mod-5 family at 11 and 16.
"""Is the distance-6 deficit an effect, or is it 31 coincidences?

`quagmire-odometer.md` records `d6w` as the one cell the model cannot reach: the corpus
reads 0.0245 and the model sits at 0.0350, flagged at p = 0.000. That p comes from
`fingerprint_battery`, which compares the LP's value against the spread of the MODEL
over prose draws and treats the LP itself as exact. The LP's within-word distance-6 rate
rests on 31 coincidences in 1,267 pairs, so it is not exact at all.

Three questions, in order.

**Is the deficit significant on its own terms?** Against chance 1/29 the expected count
is 43.7 with a standard deviation of 6.5, so 31 is about -1.9. That is the whole of the
evidence for a distance-6 relation.

**Does the battery's verdict survive the LP's error bar?** The right comparison adds the
two uncertainties. The battery adds only one.

**Does it extend along the 1-mod-5 family?** Under a period-5 schedule the distances
congruent to 1 mod 5 -- 1, 6, 11, 16 -- all carry the same shift relation, so a designed
diagonal at distance 1 acts at 6 and 11 too. That is a sharper prediction than any
single distance, and pooling the family is the only way to get the pair count up. If the
family shows nothing once distance 1 is set aside, the distance-6 dip is noise and the
doublet rule is the only thing acting.

The within-word and cross-word splits are reported separately throughout. The per-word
step changes the alphabet at every boundary, so a cross-word rate should sit at chance
whatever the schedule does; a deficit appearing in BOTH would mean something other than
the schedule is responsible.

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
MAX_D = 21


def split_pairs(words, distance: int):
    """(within-word, cross-word) coincidence counts at `distance` in the rune stream."""
    stream, owner = [], []
    for i, w in enumerate(words):
        stream.extend(w)
        owner.extend([i] * len(w))
    win = wtot = xin = xtot = 0
    for j in range(len(stream) - distance):
        same = owner[j] == owner[j + distance]
        hit = stream[j] == stream[j + distance]
        if same:
            wtot += 1
            win += hit
        else:
            xtot += 1
            xin += hit
    return (win, wtot), (xin, xtot)


def z_of(hits: int, pairs: int) -> float:
    if not pairs:
        return float("nan")
    return (hits - pairs * CHANCE) / math.sqrt(pairs * CHANCE * (1 - CHANCE))


def detectable(pairs: int, target: float = 0.0245) -> float:
    """The z a deficit of `target` would produce at this pair count.

    Answers "is there enough data": if a real relation the size of the observed one
    would only reach z = 1, the distance cannot settle anything either way.
    """
    if not pairs:
        return float("nan")
    return (target - CHANCE) * pairs / math.sqrt(pairs * CHANCE * (1 - CHANCE))


def main() -> None:
    words = lp_words()
    print(f"{len(words)} words, chance {CHANCE:.5f}\n")
    print(
        f"{'d':>3}{'within hits':>12}{'pairs':>8}{'rate':>9}{'z':>7}"
        f"{'  |':>4}{'cross hits':>11}{'pairs':>8}{'rate':>9}{'z':>7}{'   z if real':>13}"
    )
    rows = []
    for d in range(1, MAX_D):
        (win, wtot), (xin, xtot) = split_pairs(words, d)
        rows.append((d, win, wtot, xin, xtot))
        print(
            f"{d:>3}{win:>12}{wtot:>8}{win / wtot if wtot else float('nan'):>9.4f}"
            f"{z_of(win, wtot):>7.2f}{'  |':>4}"
            f"{xin:>11}{xtot:>8}{xin / xtot if xtot else float('nan'):>9.4f}"
            f"{z_of(xin, xtot):>7.2f}{detectable(wtot):>13.2f}"
        )

    # the 1-mod-5 family: the same shift relation at every one of these distances
    print("\nthe 1 mod 5 family, which a period-5 schedule ties together:")
    fam = [r for r in rows if r[0] % 5 == 1]
    for d, win, wtot, _xin, _xtot in fam:
        print(
            f"   d{d:<3} {win:>4}/{wtot:<6} z {z_of(win, wtot):>6.2f}"
            f"   a real deficit would read z {detectable(wtot):>5.2f}"
        )
    pooled_h = sum(r[1] for r in fam if r[0] > 1)
    pooled_p = sum(r[2] for r in fam if r[0] > 1)
    print(
        f"\n   pooled without d1: {pooled_h}/{pooled_p} = "
        f"{pooled_h / pooled_p:.4f}, z {z_of(pooled_h, pooled_p):+.2f}"
    )

    # the other residues, as the control: they carry a different shift
    others_h = sum(r[1] for r in rows if r[0] % 5 != 1 and r[0] > 1)
    others_p = sum(r[2] for r in rows if r[0] % 5 != 1 and r[0] > 1)
    print(
        f"   every other distance 2..20: {others_h}/{others_p} = "
        f"{others_h / others_p:.4f}, z {z_of(others_h, others_p):+.2f}"
    )

    # does the battery's d6w verdict survive the LP's own sampling error?
    d6 = next(r for r in rows if r[0] == 6)
    lp_rate = d6[1] / d6[2]
    lp_se = math.sqrt(lp_rate * (1 - lp_rate) / d6[2])
    model, model_sd = 0.0350, 0.0047  # quagmire_odometer.py --fit-d6, 40 draws
    combined = math.hypot(lp_se, model_sd)
    print("\nthe battery's d6w miss, re-tested with both uncertainties:")
    print(f"   LP    {lp_rate:.4f} +- {lp_se:.4f}  ({d6[1]} coincidences)")
    print(f"   model {model:.4f} +- {model_sd:.4f}")
    print(
        f"   difference {model - lp_rate:.4f}, combined SE {combined:.4f}, "
        f"z {(model - lp_rate) / combined:+.2f}"
    )
    print(
        "   the battery uses the model spread alone, which is where p = 0.000 came from."
    )

    assert d6[2] < 2000, (
        "d6 within words should be the thin cell this argument is about"
    )
    stability(words, rows)


def stability(words, rows) -> None:
    """The largest cross-word departure apart from d1, and why splitting cannot judge it.

    Twenty distances were scanned and the largest |z| chance gives over twenty tries is
    about 2.45, so d11's -2.90 sits at the multiple-testing floor.

    Splitting the corpus does NOT settle it. z scales as the square root of the pair
    count, so a pooled -2.90 puts each half at -2.90/sqrt(2) = -2.05 whether the cause
    is a real relation or one fluctuation spread across the whole corpus. Agreement
    between the halves is arithmetic, not evidence. Only disagreement would be
    informative, so the split is printed as a negative control on the method rather
    than as support.
    """
    print("\nthe one flagged cross-word cell, checked for stability:")
    worst = max((r for r in rows if r[0] > 1), key=lambda r: abs(z_of(r[3], r[4])))
    d = worst[0]
    print(
        f"   cross-word d{d}: {worst[3]}/{worst[4]} z {z_of(worst[3], worst[4]):+.2f}"
        f"   (chance over {MAX_D - 1} distances gives max |z| about "
        f"{math.sqrt(2 * math.log(MAX_D - 1)):.2f})"
    )
    half = len(words) // 2
    for label, part in (("first half", words[:half]), ("second half", words[half:])):
        _w, (xh, xp) = split_pairs(part, d)
        print(f"      {label:<12} {xh:>4}/{xp:<6} z {z_of(xh, xp):+.2f}")
    print(
        f"      both land near {z_of(worst[3], worst[4]) / math.sqrt(2):+.2f}, which is "
        f"the pooled z over sqrt(2):\n      the split is uninformative either way."
    )
    # and the within-word family, which is where a schedule relation would have to show
    print(
        "\n   within words the 1-mod-5 family past d1 has no power: d11 holds 35 pairs"
        "\n   and d16 none, so d6's 31 coincidences are the whole of the evidence."
    )


if __name__ == "__main__":
    main()
