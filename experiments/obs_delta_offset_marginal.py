# ABOUTME: Observation: the d=1 difference-class marginal (c_j - c_{j-1} mod 29)
# ABOUTME: is flat off zero -- closes deterministic skip rules spread over offsets.
"""Per-offset marginal of adjacent ciphertext differences.

The doublet deficit removes ~360 adjacent-equal pairs relative to chance. Any
DETERMINISTIC avoidance rule ("on would-be doublet, emit prev + s" for one or a
few offsets s) must park that mass in specific difference classes. The bigram
battery's per-cell chi-square (full_bigram_battery.py) catches a single-offset
rule but loses power once the mass spreads over several offsets, because each
class is 29 cells and the per-class excess dilutes. The difference-class
marginal pools each class and keeps ~sqrt(29)x the per-cell power.

Test: histogram of (c_j - c_{j-1}) mod 29 over all adjacent pairs, class 0
(doublets) set aside as known. The 28 nonzero classes should be multinomial
uniform under uniform-redraw avoidance and under the walk's tuned diagonal
(both spread displaced mass evenly to first order). Bands: analytic
multinomial z per class, chi-square over 28 classes, and a rune-shuffle null
(unigram-exact) for the family-blind max |z|.

Self-test: the same statistics on simulated avoidance streams with the fix
parked on |S| = 1, 2, 4, 8 offsets, plus a uniform-redraw control, so the
power at each spread is measured, not assumed.

The chi-square gets a second, within-section shuffle null: unigram drift
across sections inflates the difference-class chi2 under a global shuffle
(adjacent pairs sample the local profile), so only an excess over the
stratified null counts as adjacency structure.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from pathlib import Path

from lp_corpus import IDX, RUNE, N, load_clean

from aldegonde import c3301


def load_sections() -> list[list[int]]:
    """The clean stream split per $-section (concatenation == load_clean)."""
    text = (
        Path(__file__).resolve().parent.parent / "data" / "page0-56.txt"
    ).read_text()
    secs = [s for s in text.split("$") if RUNE.search(s)][:10]
    return [[IDX[ch] for ch in s if RUNE.match(ch)] for s in secs]


SHUFFLES = 3000
DOUBLET_SURROGATES = 1000
SIM_SEED = 5


def nonzero_class_stats(stream: list[int]) -> tuple[list[int], float, float]:
    """Return (per-class counts k=1..28, chi2 over the 28 classes, max |z|)."""
    counts = Counter((stream[i + 1] - stream[i]) % N for i in range(len(stream) - 1))
    off = [counts.get(k, 0) for k in range(1, N)]
    m = sum(off)
    exp = m / (N - 1)
    sd = math.sqrt(m * (1 / (N - 1)) * (1 - 1 / (N - 1)))
    chi2 = sum((o - exp) ** 2 / exp for o in off)
    maxz = max(abs(o - exp) / sd for o in off)
    return off, chi2, maxz


def simulate_avoidance(
    unigram: list[float], n: int, offsets: list[int] | None, rng: random.Random
) -> list[int]:
    """i.i.d. stream from the corpus unigram profile with 81% doublet avoidance:
    a would-be doublet is replaced by prev + s (s from offsets) or, when
    offsets is None, by a uniform redraw among the 28 other runes."""
    runes = list(range(N))
    stream = [rng.choices(runes, weights=unigram)[0]]
    for _ in range(n - 1):
        c = rng.choices(runes, weights=unigram)[0]
        if c == stream[-1] and rng.random() < 0.81:
            if offsets is None:
                c = (stream[-1] + rng.randint(1, N - 1)) % N
            else:
                c = (stream[-1] + rng.choice(offsets)) % N
        stream.append(c)
    return stream


def main() -> None:
    stream, _ = load_clean()
    npairs = len(stream) - 1
    doublets = sum(1 for i in range(npairs) if stream[i] == stream[i + 1])
    off, chi2, maxz = nonzero_class_stats(stream)
    m = sum(off)
    exp = m / (N - 1)
    sd = math.sqrt(m * (1 / (N - 1)) * (1 - 1 / (N - 1)))
    displaced = npairs / N - doublets

    print(
        f"pairs {npairs}, doublets {doublets}, "
        f"displaced mass vs chance ~{displaced:.0f} events"
    )
    print(f"nonzero pairs {m}, per-class expectation {exp:.1f} +- {sd:.1f}")
    print("class:  " + " ".join(f"{k:4d}" for k in range(1, N)))
    print("count:  " + " ".join(f"{o:4d}" for o in off))
    print("z:      " + " ".join(f"{(o - exp) / sd:+4.1f}" for o in off))
    print(f"chi2 (27 df) {chi2:.1f}, max |z| {maxz:.2f}")

    # rune-shuffle null: exact unigram profile, no adjacency structure
    rng = random.Random(SIM_SEED)
    null_chi2, null_maxz = [], []
    work = list(stream)
    for _ in range(SHUFFLES):
        rng.shuffle(work)
        _, c2, mz = nonzero_class_stats(work)
        null_chi2.append(c2)
        null_maxz.append(mz)
    mu_c, sd_c = (
        sum(null_chi2) / SHUFFLES,
        math.sqrt(
            sum((c - sum(null_chi2) / SHUFFLES) ** 2 for c in null_chi2) / SHUFFLES
        ),
    )
    p_chi2 = sum(c >= chi2 for c in null_chi2) / SHUFFLES
    p_maxz = sum(z >= maxz for z in null_maxz) / SHUFFLES
    print(
        f"global shuffle null ({SHUFFLES}): chi2 {mu_c:.1f} +- {sd_c:.1f} "
        f"-> p = {p_chi2:.3f}; family-blind max|z| p = {p_maxz:.3f}"
    )

    # within-section shuffle null: preserves per-section unigram profiles,
    # so section-level drift no longer reads as adjacency structure
    sections = load_sections()
    assert [r for s in sections for r in s] == stream
    strat_chi2, strat_maxz = [], []
    for _ in range(SHUFFLES):
        for s in sections:
            rng.shuffle(s)
        _, c2, mz = nonzero_class_stats([r for s in sections for r in s])
        strat_chi2.append(c2)
        strat_maxz.append(mz)
    mu_s = sum(strat_chi2) / SHUFFLES
    sd_s = math.sqrt(sum((c - mu_s) ** 2 for c in strat_chi2) / SHUFFLES)
    ps_chi2 = sum(c >= chi2 for c in strat_chi2) / SHUFFLES
    ps_maxz = sum(z >= maxz for z in strat_maxz) / SHUFFLES
    print(
        f"within-section null ({SHUFFLES}): chi2 {mu_s:.1f} +- {sd_s:.1f} "
        f"-> p = {ps_chi2:.3f}; family-blind max|z| p = {ps_maxz:.3f}"
    )

    # doublet-preserving null: the canonical corpus null (frequency-exact,
    # observed doublet rate), as used by full_bigram_battery.py
    model = c3301.low_doublet_null()
    db_chi2, db_maxz = [], []
    for _ in range(DOUBLET_SURROGATES):
        _, c2, mz = nonzero_class_stats(list(model(stream, rng)))
        db_chi2.append(c2)
        db_maxz.append(mz)
    mu_d = sum(db_chi2) / DOUBLET_SURROGATES
    sd_d = math.sqrt(sum((c - mu_d) ** 2 for c in db_chi2) / DOUBLET_SURROGATES)
    pd_chi2 = sum(c >= chi2 for c in db_chi2) / DOUBLET_SURROGATES
    pd_maxz = sum(z >= maxz for z in db_maxz) / DOUBLET_SURROGATES
    print(
        f"doublet-preserving null ({DOUBLET_SURROGATES}): chi2 {mu_d:.1f} +- {sd_d:.1f} "
        f"-> p = {pd_chi2:.3f}; family-blind max|z| p = {pd_maxz:.3f}"
    )

    # power self-test: planted skip rules at matched doublet rate
    unigram = [sum(1 for r in stream if r == a) / len(stream) for a in range(N)]
    print("planted avoidance (same length, 81% fix rate), max |z| per variant:")
    for label, offsets in [
        ("skip to 1 offset", [7]),
        ("skip to 2 offsets", [7, 15]),
        ("skip to 4 offsets", [3, 7, 15, 22]),
        ("skip to 8 offsets", [3, 5, 7, 11, 15, 19, 22, 26]),
        ("uniform redraw (control)", None),
    ]:
        sim = simulate_avoidance(unigram, len(stream), offsets, rng)
        _, sim_chi2, sim_maxz = nonzero_class_stats(sim)
        d = sum(1 for i in range(len(sim) - 1) if sim[i] == sim[i + 1])
        print(
            f"  {label:26s} doublets {d:3d}  chi2 {sim_chi2:6.1f}  "
            f"max|z| {sim_maxz:.2f}"
        )

    print("VERDICT: if LP's chi2 and max|z| sit inside the shuffle null while")
    print("the planted skips light up, every deterministic skip rule narrow")
    print("enough for this test's power is excluded; the displaced doublet")
    print("mass spreads flat, as uniform redraw and the tuned diagonal predict.")


if __name__ == "__main__":
    main()
