#!/usr/bin/env python3
# ABOUTME: Test whether the mono-kappa coincidence deficit at distance 11 in the
# ABOUTME: clean Liber Primus corpus is real and whether it is a period-5 echo (11 = 2*5+1).
"""Is the lag-11 coincidence deficit real, and is it tied to the lag-5 structure?

A low-doublet-null kappa scan of the clean corpus (sections 0-9 of
data/page0-58.txt, 12,956 runes) shows one strong outlier: at skip 11 the text
has 386 single-rune coincidences against ~447 expected (z ~= -2.9, IoC 0.865).
Every other skip in 1..20 sits within +-1.6 sigma. The conjecture on the table
is that 11 = 2*5 + 1, i.e. the deficit is a harmonic/echo of the known lag-5
coincidence excess.

A plain "the text repeats every 5" model predicts an EXCESS at 10, 15, 20 too;
those are flat (z ~= -0.3, -0.5, -0.1), so any link to lag 5 must be subtler
than periodicity. This script runs five instruments and lets the numbers decide:

  A. Wide analytic kappa scan (1..80) with a multiplicity budget and the
     ranked extremes, to see whether 11 is uniquely deep or one of many.
  B. mod-5 phase decomposition of the z-scores: if the deficit is a period-5
     phenomenon, the residue classes should separate (multiples of 5 high,
     some class low). This is the direct test of the 2*5+1 conjecture.
  C. Per-section and leave-one-section-out z at lag 11, to see whether one
     section drives it.
  D. Monte-Carlo low-doublet-null p-value at lag 11, then Sidak-corrected for
     the number of lags scanned -- the honest significance.
  E. Within-word vs across-word split at lag 11 with a word-length permutation
     null (the instrument that cracked lag 5), to see where the deficit lives.

Corpus and tokenization match experiments/lag5_word_boundary.py.
"""

from __future__ import annotations

from math import erfc, sqrt

from aldegonde import c3301
from aldegonde.analysis.coincidence import (
    boundary_coincidence,
    boundary_permutation_test,
)
from aldegonde.stats.kappa import doublets
from aldegonde.stats.nulls import doublet_shuffle
from aldegonde.stats.resample import monte_carlo_map

ALPHA = len(c3301.CICADA_ALPHABET)
R2I = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
RUNES = set(R2I)
WORD_BOUNDARIES = set(c3301.MARK_CHARS + "&%" + c3301.NUMERAL_CHARS)
FOCUS_LAG = 11
MAX_LAG = 80
SEED = 3301


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


def coincidence_prob(stream: list[int]) -> float:
    """Chance match probability = sum of squared symbol frequencies (mono IoC)."""
    n = len(stream)
    counts = [0] * ALPHA
    for x in stream:
        counts[x] += 1
    return sum((c / n) ** 2 for c in counts)


def kappa_z(stream: list[int], skip: int, prob: float) -> tuple[int, float, float, float]:
    """Return (count, expected, z, normalized_ioc) for one skip, frequency-based null.

    Expected and its standard deviation come from a Bernoulli(prob) model over
    the N-skip position pairs, prob being the frequency-matched chance rate.
    This is the closed form the Monte-Carlo low-doublet null reproduces.
    """
    pairs = len(stream) - skip
    count = sum(1 for i in range(pairs) if stream[i] == stream[i + skip])
    mu = pairs * prob
    sd = sqrt(pairs * prob * (1.0 - prob))
    z = (count - mu) / sd if sd else 0.0
    ioc = count / mu if mu else 0.0
    return count, mu, z, ioc


def two_sided_p(z: float) -> float:
    """Two-sided normal tail probability for a z-score."""
    return erfc(abs(z) / sqrt(2.0))


def test_a_wide_scan(stream: list[int], prob: float) -> dict[int, float]:
    """Analytic kappa scan 1..MAX_LAG, multiplicity budget, ranked extremes."""
    print(f"=== A. Wide kappa scan, lags 1..{MAX_LAG} (analytic freq-null) ===")
    rows = {}
    for skip in range(1, MAX_LAG + 1):
        count, mu, z, ioc = kappa_z(stream, skip, prob)
        rows[skip] = z
        mark = "  <<<" if skip == FOCUS_LAG else ""
        if abs(z) >= 2.0 or skip <= 20 or skip == FOCUS_LAG:
            print(
                f"  skip={skip:<3d} count={count:<4d} exp={mu:6.1f} "
                f"z={z:+5.2f} ioc={ioc:.3f}{mark}"
            )
    m = MAX_LAG - 1  # skip=1 is the doublet slot, excluded from the comb budget
    for thr in (2.0, 2.5, 3.0):
        obs = sum(1 for s, z in rows.items() if s != 1 and abs(z) >= thr)
        exp = m * two_sided_p(thr)
        print(f"  |z| >= {thr}: observed {obs}, expected {exp:.2f} over {m} lags")
    ordered = sorted((z, s) for s, z in rows.items() if s != 1)
    low = ", ".join(f"{s}:{z:+.2f}" for z, s in ordered[:5])
    high = ", ".join(f"{s}:{z:+.2f}" for z, s in ordered[-5:][::-1])
    print(f"  most depleted:  {low}")
    print(f"  most enriched:  {high}")
    print()
    return rows


def test_b_mod5(rows: dict[int, float]) -> None:
    """mod-5 phase decomposition -- the direct test of the 2*5+1 conjecture."""
    print("=== B. mod-5 phase decomposition of z-scores ===")
    print("  If the deficit is a period-5 effect, residue classes separate.")
    residues: dict[int, list[float]] = {r: [] for r in range(5)}
    for skip, z in rows.items():
        if skip == 1:
            continue
        residues[skip % 5].append(z)
    for r in range(5):
        zs = residues[r]
        mean = sum(zs) / len(zs)
        # z of the class mean (independent-lag approximation)
        pooled = mean * sqrt(len(zs))
        note = ""
        if r == 0:
            note = "  (5,10,15,20,... -- would-be harmonics)"
        elif r == 1:
            note = "  (6,11,16,21,... -- the 5k+1 family, contains 11)"
        print(
            f"  skip%5=={r}: n={len(zs):2d} mean_z={mean:+.3f} "
            f"pooled_z={pooled:+.2f}{note}"
        )
    print("  members of the 5k+1 family:")
    fam = sorted(s for s in rows if s % 5 == 1 and s != 1)
    print("   " + ", ".join(f"{s}:{rows[s]:+.2f}" for s in fam))
    print()


def test_c_sections(sections: list[list[list[int]]], prob: float) -> None:
    """Per-section and leave-one-out z at the focus lag."""
    print(f"=== C. Section stability at lag {FOCUS_LAG} ===")
    streams = [[r for w in s for r in w] for s in sections]
    full = [r for st in streams for r in st]
    _, _, z_full, ioc_full = kappa_z(full, FOCUS_LAG, prob)
    print(f"  full corpus: z={z_full:+.2f} ioc={ioc_full:.3f}")
    for i, st in enumerate(streams):
        if len(st) <= FOCUS_LAG + 5:
            continue
        p = coincidence_prob(st)
        c, mu, z, ioc = kappa_z(st, FOCUS_LAG, p)
        loo = [r for j, s in enumerate(streams) if j != i for r in s]
        _, _, z_loo, ioc_loo = kappa_z(loo, FOCUS_LAG, coincidence_prob(loo))
        print(
            f"  section {i}: n={len(st):5d} z={z:+5.2f} ioc={ioc:.3f}"
            f"   | drop it -> z={z_loo:+5.2f} ioc={ioc_loo:.3f}"
        )
    print()


def test_d_montecarlo(stream: list[int]) -> None:
    """Monte-Carlo low-doublet-null p-value at the focus lag, Sidak-corrected."""
    print(f"=== D. Monte-Carlo significance at lag {FOCUS_LAG} ===")
    dbl, pairs1 = doublets(stream, skip=1, length=1)
    rate = len(dbl) / pairs1
    null = doublet_shuffle(rate)
    skips = list(range(2, MAX_LAG + 1))

    def statistic(sample):
        return {s: float(sum(1 for i in range(len(sample) - s)
                             if sample[i] == sample[i + s])) for s in skips}

    results = monte_carlo_map(statistic, null, stream, keys=skips,
                              trials=5000, seed=SEED)
    comp = results[FOCUS_LAG]
    p_mc = comp.p_lower
    z = comp.z
    p_analytic = two_sided_p(z)
    m = len(skips)
    sidak = 1.0 - (1.0 - p_analytic) ** m
    print(f"  observed count : {int(comp.observed)}")
    print(f"  null mean/sd   : {comp.null_mean:.2f} / {comp.null_sd:.2f}")
    print(f"  z              : {z:+.2f}")
    print(f"  one-sided MC p : {p_mc:.4f} (5000 trials, matched doublet rate)")
    print(f"  two-sided p    : {p_analytic:.4f}")
    print(f"  Sidak over {m} lags: {sidak:.3f}")
    print()


def test_e_word_boundary(sections: list[list[list[int]]]) -> None:
    """Within-word vs across-word split at the focus lag (the lag-5 instrument)."""
    print(f"=== E. Within/across-word split at lag {FOCUS_LAG} ===")
    all_words = [w for s in sections for w in s]
    bc = boundary_coincidence(all_words, FOCUS_LAG)
    within = bc.within_observed / bc.within_pairs if bc.within_pairs else 0.0
    across = bc.across_observed / bc.across_pairs if bc.across_pairs else 0.0
    print(f"  within-word: {bc.within_observed}/{bc.within_pairs} = {within:.4f}")
    print(f"  across-word: {bc.across_observed}/{bc.across_pairs} = {across:.4f}")
    perm = boundary_permutation_test(sections, FOCUS_LAG,
                                     permutations=5000, seed=SEED)
    print(
        f"  within-word matches vs length-shuffle null: obs={perm.observed} "
        f"null={perm.null_mean:.1f}+-{perm.null_sd:.1f} p(>=obs)={perm.p_value:.4f}"
    )
    print("  (p near 1.0 => within-word DEFICIT; near 0.0 => within-word excess)")
    print()


def main() -> None:
    sections = parse_clean_sections()
    stream = [r for s in sections for w in s for r in w]
    prob = coincidence_prob(stream)
    print(f"corpus: {len(stream)} runes, {len(sections)} sections, "
          f"chance match rate {prob:.5f} (uniform 1/29 = {1/ALPHA:.5f})\n")
    rows = test_a_wide_scan(stream, prob)
    test_b_mod5(rows)
    test_c_sections(sections, prob)
    test_d_montecarlo(stream)
    test_e_word_boundary(sections)


if __name__ == "__main__":
    main()
