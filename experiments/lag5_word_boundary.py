#!/usr/bin/env python3
"""Reconcile the two lag-5 findings: paired matches vs within-word excess.

Two independent analyses characterized the same +32 excess of lag-5
coincidences in the clean unsolved corpus and reached contradictory
conclusions:

- `hypotheses/lag5-digraph-structure.md`: the excess is carried by match
  PAIRS at separations exactly 1 and 4, and "events freely cross word
  boundaries" (boundary-blind).
- `hypotheses/within-word-d5-coincidence.md`: the excess lives entirely
  INSIDE words (within-word 4.92% vs cross-word exactly at chance,
  boundary-permutation p = 0.0014).

Neither analysis ran the other's test. This script runs both instruments on
the same corpus with the same tokenization, then computes the joint
decomposition — every lag-5 match classified by (paired vs isolated) x
(within-word vs across-word) — with a word-length permutation null for each
cell. That decides whether the pairing and the word-boundary alignment are
one phenomenon or two.

Corpus: sections 0-9 of data/page0-58.txt (12,956 runes). Words tokenized
with - . & % $ as boundaries; '/' and newlines are line wraps.
"""

from bisect import bisect_right
from itertools import accumulate
from random import Random
from statistics import fmean, pstdev

from aldegonde import c3301
from aldegonde.analysis.coincidence import (
    boundary_coincidence,
    boundary_permutation_test,
    joint_coincidence,
    match_indicator,
)

LAG = 5
PAIR_SEPARATIONS = (1, 4)
N_PERMS = 10_000
SEED = 3301

R2I = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
RUNES = set(R2I)
WORD_BOUNDARIES = set(c3301.MARK_CHARS + "&%" + c3301.NUMERAL_CHARS)


def parse_clean_sections(path: str = "data/page0-58.txt") -> list[list[list[int]]]:
    """Words per $-section, clean cipher corpus only (sections 0-9)."""
    with open(path) as f:
        text = f.read()
    sec_words: list[list[list[int]]] = [[]]
    cur: list[int] = []
    for ch in text:
        if ch in RUNES:
            cur.append(R2I[ch])
        elif ch == "$":
            if cur:
                sec_words[-1].append(cur)
                cur = []
            sec_words.append([])
        elif ch in WORD_BOUNDARIES and cur:
            sec_words[-1].append(cur)
            cur = []
    if cur:
        sec_words[-1].append(cur)
    return [s for s in sec_words if s][:10]


def runes(word: list[int]) -> str:
    """Render a word of rune indices back to runes."""
    return "".join(c3301.CICADA_ALPHABET[x] for x in word)


def match_positions(stream: list[int], lag: int = LAG) -> list[int]:
    """Positions i with stream[i] == stream[i + lag]."""
    return [i for i, m in enumerate(match_indicator(stream, lag)) if m]


def split_paired(positions: list[int]) -> tuple[set[int], set[int]]:
    """Split match positions into paired (another match at +-1 or +-4) and isolated."""
    pos = set(positions)
    paired = {
        i
        for i in pos
        if any(i + d in pos or i - d in pos for d in PAIR_SEPARATIONS)
    }
    return paired, pos - paired


def main() -> None:
    sections = parse_clean_sections()
    words = [w for s in sections for w in s]
    stream = [x for w in words for x in w]
    n = len(stream)
    print(f"clean corpus: {n} runes, {len(words)} words, {len(sections)} sections")

    # ------------------------------------------------------------------
    # 1. Reproduce both published instruments on this corpus/tokenization
    # ------------------------------------------------------------------
    split = boundary_coincidence(words, LAG)
    print(f"\n[within-word instrument]  (published: 102/2073 vs 377/10878)")
    print(f"  within: {split.within_observed}/{split.within_pairs} "
          f"= {split.within_observed / split.within_pairs:.4f}")
    print(f"  across: {split.across_observed}/{split.across_pairs} "
          f"= {split.across_observed / split.across_pairs:.4f}   (1/29 = {1 / 29:.4f})")

    joint = joint_coincidence(stream, LAG, PAIR_SEPARATIONS)
    print(f"\n[paired-match instrument]  (published: d1 29, d4 28, expected ~17.7)")
    for d in PAIR_SEPARATIONS:
        print(f"  pairs at separation {d}: {joint[d].observed} "
              f"(chance {joint[d].expected:.1f})")

    # ------------------------------------------------------------------
    # 2. The joint decomposition neither analysis ran
    # ------------------------------------------------------------------
    positions = match_positions(stream)
    paired, isolated = split_paired(positions)
    ids = []
    for index, w in enumerate(words):
        ids.extend([index] * len(w))
    within = {i for i in positions if ids[i] == ids[i + LAG]}

    print(f"\n[joint decomposition]  {len(positions)} matches "
          f"(expected {(n - LAG) / 29:.1f})")
    header = f"  {'':<10} {'within':>8} {'across':>8} {'total':>8}"
    print(header)
    for label, group in (("paired", paired), ("isolated", isolated)):
        w_count = len(group & within)
        print(f"  {label:<10} {w_count:>8} {len(group) - w_count:>8} "
              f"{len(group):>8}")
    print(f"  {'total':<10} {len(within):>8} "
          f"{len(positions) - len(within):>8} {len(positions):>8}")
    assert len(within) == split.within_observed

    # Pair events: both matches of a d1/d4 pair within the same word?
    print("\n[pair events by word membership]")
    for d in PAIR_SEPARATIONS:
        events = [i for i in positions if i + d in set(positions)]
        both = [i for i in events if i in within and i + d in within]
        one = [i for i in events if (i in within) != (i + d in within)]
        neither = [i for i in events if i not in within and i + d not in within]
        print(f"  separation {d}: {len(events)} events — "
              f"both within {len(both)}, one within {len(one)}, "
              f"neither {len(neither)}")
        if d == 1:
            for i in both:
                print(f"    in-word digraph repeat at {i}: {runes(words[ids[i]])}")

    # ------------------------------------------------------------------
    # 3. Permutation nulls: shuffle word lengths per section, stream fixed
    # ------------------------------------------------------------------
    # Section-local geometry so shuffles never move matches across sections.
    sec_streams = [[x for w in s for x in w] for s in sections]
    sec_lengths = [[len(w) for w in s] for s in sections]
    starts = [0]
    for s in sec_streams:
        starts.append(starts[-1] + len(s))

    def local_matches(group: set[int]) -> list[tuple[int, int]]:
        """(section, local position) for matches not spanning a section seam."""
        out = []
        for i in sorted(group):
            sec = bisect_right(starts, i) - 1
            if i + LAG < starts[sec + 1]:
                out.append((sec, i - starts[sec]))
        return out

    def within_count(local: list[tuple[int, int]], cuts: list[list[int]]) -> int:
        """Matches with no word boundary in (k, k+LAG], given per-section cuts."""
        count = 0
        for sec, k in local:
            bounds = cuts[sec]
            if bisect_right(bounds, k + LAG) - bisect_right(bounds, k) == 0:
                count += 1
        return count

    real_cuts = [list(accumulate(lens))[:-1] for lens in sec_lengths]
    groups = {"paired": local_matches(paired), "isolated": local_matches(isolated)}
    observed = {k: within_count(v, real_cuts) for k, v in groups.items()}
    assert sum(observed.values()) == len(within)

    rng = Random(SEED)
    null: dict[str, list[int]] = {k: [] for k in groups}
    for _ in range(N_PERMS):
        cuts = []
        for lens in sec_lengths:
            shuffled = list(lens)
            rng.shuffle(shuffled)
            cuts.append(list(accumulate(shuffled))[:-1])
        for k, v in groups.items():
            null[k].append(within_count(v, cuts))

    print(f"\n[boundary permutation, {N_PERMS} perms] "
          "do boundaries know where the matches are?")
    print(f"  {'group':<10} {'obs.within':>10} {'null':>14} {'p(>=obs)':>9}")
    for k in groups:
        mean, sd = fmean(null[k]), pstdev(null[k])
        p = (sum(1 for v in null[k] if v >= observed[k]) + 1) / (N_PERMS + 1)
        print(f"  {k:<10} {observed[k]:>10} {mean:>8.1f} ± {sd:<4.1f} {p:>9.4f}")

    # The published within-word test, via the library, as a cross-check.
    result = boundary_permutation_test(sections, LAG, permutations=N_PERMS, seed=SEED)
    print(f"  {'all':<10} {result.observed:>10} "
          f"{result.null_mean:>8.1f} ± {result.null_sd:<4.1f} "
          f"{result.p_value:>9.4f}   (published: 102, 76.5 ± 7.9, p 0.0014)")

    # ------------------------------------------------------------------
    # 4. Verdict
    # ------------------------------------------------------------------
    print("\n[verdict]")
    excess = {
        k: observed[k] - fmean(null[k])
        for k in groups
    }
    aware = {
        k: excess[k] > 2 * pstdev(null[k]) > 0
        for k in groups
    }
    print(f"  within-word excess over the boundary null: "
          f"paired {excess['paired']:+.1f}, isolated {excess['isolated']:+.1f}")
    if aware["paired"]:
        print("  -> paired matches are word-boundary-aware; "
              "'events freely cross word boundaries' is falsified")
    else:
        print("  -> paired matches show no boundary preference")
    if aware["paired"] and aware["isolated"]:
        print("  -> isolated matches are boundary-aware too: one word-aware "
              "lag-5 phenomenon, of which the {1,4} pairing is a facet, "
              "not two separate effects")
    elif aware["isolated"]:
        print("  -> only isolated matches are boundary-aware; the pairing "
              "and the within-word excess are separate effects")
    elif aware["paired"]:
        print("  -> isolated matches are boundary-blind; the within-word "
              "excess and the pairing are the same phenomenon")


if __name__ == "__main__":
    main()
