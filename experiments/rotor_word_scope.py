# ABOUTME: An autonomous machine cannot see word boundaries, so its distance-d
# ABOUTME: statistics must be boundary-blind. The LP's d5 echo is not.
"""The period tests (rotor_period_closure.py) leave one escape: a machine
with period longer than the corpus, e.g. a 3-rotor odometer at 29^3 =
24389. It never reuses an alphabet, so no lag test can see it.

This closes that escape on a different property. An autonomous machine's
alphabet is a function of ABSOLUTE POSITION only. It has no access to the
word separators, so whatever it does at distance 5 it does uniformly --
the within-word and cross-word distance-5 rates must agree, and the
within-word rate must not depend on where the boundaries happen to fall.

Test: hold the rune stream byte-for-byte and shuffle only the word-length
sequence. That is exactly the prediction of a boundary-blind machine. If
the real boundaries know where the distance-5 coincidences are, no
autonomous machine of any period produced this text.

Reproduces the figure in within-word-d5-coincidence.md independently
(102 observed vs ~76 null) as a self-check on the harness.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

N = 29
D = 5


def split_counts(stream: list[int], lengths: list[int], d: int) -> tuple[int, int, int, int]:
    """(within hits, within pairs, cross hits, cross pairs) at distance d."""
    word_of = []
    for w, L in enumerate(lengths):
        word_of.extend([w] * L)
    wh = wp = ch = cp = 0
    for i in range(len(stream) - d):
        same = word_of[i] == word_of[i + d]
        hit = stream[i] == stream[i + d]
        if same:
            wp += 1
            wh += hit
        else:
            cp += 1
            ch += hit
    return wh, wp, ch, cp


def main() -> None:
    stream, word_id = load_clean()
    lengths: list[int] = []
    for w in word_id:
        if w >= len(lengths):
            lengths.append(0)
        lengths[w] += 1
    assert sum(lengths) == len(stream)

    wh, wp, ch, cp = split_counts(stream, lengths, D)
    print(f"observed d={D}:")
    print(f"  within-word {wh:>4}/{wp:<6} = {wh / wp:.4f}")
    print(f"  cross-word  {ch:>4}/{cp:<6} = {ch / cp:.4f}")
    print(f"  chance 1/29 = {1 / N:.4f}")

    # Self-check against the documented figures.
    assert (wh, wp) == (102, 2073), (wh, wp)
    assert (ch, cp) == (377, 10878), (ch, cp)
    print("  self-check: matches within-word-d5-coincidence.md (102/2073, 377/10878)  OK")

    # The boundary-blind prediction: shuffle word lengths, keep runes fixed.
    rng = random.Random(3301)
    trials = 5000
    null = []
    for _ in range(trials):
        perm = lengths[:]
        rng.shuffle(perm)
        null.append(split_counts(stream, perm, D)[0])
    mean = sum(null) / trials
    sd = (sum((x - mean) ** 2 for x in null) / trials) ** 0.5
    ge = sum(1 for x in null if x >= wh)
    print(f"\nboundary-blind null (word lengths shuffled, runes fixed, {trials} draws):")
    print(f"  within-word hits {mean:.1f} +/- {sd:.1f}   observed {wh}")
    print(f"  z = {(wh - mean) / sd:+.2f}   P(null >= observed) = {(ge + 1) / (trials + 1):.4f}")

    print(
        "\n  An autonomous machine (rotor of any period, any wiring) is boundary-blind\n"
        "  by construction, so this null IS its prediction."
    )

    # Controls: the same test at neighbouring distances, to show it is d5 and
    # not a general artefact of the harness.
    print("\ncontrol distances (same harness):")
    for d in (1, 2, 3, 4, 5, 6, 7):
        h, p, _, _ = split_counts(stream, lengths, d)
        nl = []
        for _ in range(1500):
            perm = lengths[:]
            rng.shuffle(perm)
            nl.append(split_counts(stream, perm, d)[0])
        m = sum(nl) / len(nl)
        s = (sum((x - m) ** 2 for x in nl) / len(nl)) ** 0.5
        flag = "  <== the echo" if d == D else ""
        print(f"  d={d}: {h:>4}/{p:<6} obs, null {m:6.1f} +/- {s:4.1f}, z={(h - m) / s:+5.2f}{flag}")


if __name__ == "__main__":
    main()
