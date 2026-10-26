# ABOUTME: Census of within-block runes and adjacent pairs by clock phase (position mod 5) and
# ABOUTME: what a doublet gate at one phase would predict, against the observed doublets.
"""Phase-gated doublets under a per-block clock reset.

If the letter clock restarts at each block, a rune's phase is its position mod 5, and the
five phases are not equally represented: phase 0 opens every block, phase 4 exists only
in blocks of five or more. A gate that admits doublets at one phase only would then make
the doublet rate depend on position in the block and on block length, and would decide
whether seam doublets (whose second rune is at phase 0) are admitted at all.

The continuous-clock convention is not tested here: there the phase drifts off position
and the record already shows the position tests have no power
(`period5-doublet-linkage.md`).

    python experiments/doublet_phase_gate_by_word.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from scipy.stats import binom

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from within_word_d5 import M, parse_clean_sections  # noqa: E402

PHASES = 5


def main() -> None:
    sections = parse_clean_sections(str(ROOT / "data/page0-56.txt"))
    words = [w for s in sections for w in s]

    runes = Counter()
    pairs = Counter()
    doublets = Counter()
    by_length = {}
    for w in words:
        for j, _ in enumerate(w):
            runes[j % PHASES] += 1
        for j in range(len(w) - 1):
            phase = (j + 1) % PHASES  # phase of the second rune of the pair
            pairs[phase] += 1
            if w[j] == w[j + 1]:
                doublets[phase] += 1
        length = min(len(w), 10)
        entry = by_length.setdefault(length, [0, 0])
        entry[0] += len(w) - 1
        entry[1] += sum(w[j] == w[j + 1] for j in range(len(w) - 1))

    seam_pairs = sum(1 for s in sections for _ in s[1:])
    seam_doublets = sum(1 for s in sections for a, b in zip(s, s[1:]) if a[-1] == b[0])
    total_pairs = sum(pairs.values())
    total_doublets = sum(doublets.values())
    print(
        f"within-block adjacent pairs {total_pairs}, doublets {total_doublets} ({total_doublets / total_pairs:.4f})"
    )
    print(
        f"seam pairs {seam_pairs}, doublets {seam_doublets} ({seam_doublets / seam_pairs:.4f}); chance {1 / M:.4f}\n"
    )

    print(
        "phase (position mod 5)   runes   share   pairs ending here   share   doublets   rate"
    )
    for phase in range(PHASES):
        r, p, d = runes[phase], pairs[phase], doublets[phase]
        print(
            f"{phase:>5}{r:>24}{r / sum(runes.values()):>8.3f}{p:>14}{p / total_pairs:>13.3f}"
            f"{d:>11}{d / p if p else 0:>7.4f}"
        )

    print(
        "\ngate admitting doublets at one phase only, chance rate there, none elsewhere:"
    )
    print(
        f"{'gate':>5}{'predicted within':>18}{'observed':>10}{'off-phase observed':>20}{'seam predicted':>16}{'seam observed':>15}"
    )
    for phase in range(PHASES):
        predicted = pairs[phase] / M
        off = total_doublets - doublets[phase]
        seam_pred = seam_pairs / M if phase == 0 else 0.0
        print(
            f"{phase:>5}{predicted:>18.1f}{total_doublets:>10}{off:>20}{seam_pred:>16.1f}{seam_doublets:>15}"
        )
    print(
        "  (a one-phase gate forbids every doublet at the other four phases; the off-phase"
        " column counts the ones the body has there)"
    )

    print("\nwithin-block doublets by block length (opportunity-normalised):")
    print(f"{'length':>7}{'pairs':>8}{'doublets':>10}{'rate':>8}{'z vs pooled':>13}")
    pooled = total_doublets / total_pairs
    for length in sorted(by_length):
        p, d = by_length[length]
        if p == 0:
            continue
        z = (d - p * pooled) / (p * pooled * (1 - pooled)) ** 0.5
        tag = f"{length}+" if length == 10 else str(length)
        print(f"{tag:>7}{p:>8}{d:>10}{d / p:>8.4f}{z:>+13.2f}")

    # a gate at phase 4 admits no doublet in blocks shorter than 5; at phase 0 none shorter than 6
    for phase, shortest in ((4, 5), (0, 6), (3, 4), (2, 3), (1, 2)):
        short_pairs = sum(p for L, (p, _) in by_length.items() if shortest > L)
        short_d = sum(d for L, (_, d) in by_length.items() if shortest > L)
        if short_pairs:
            print(
                f"gate at phase {phase}: blocks shorter than {shortest} runes hold {short_d} doublets in"
                f" {short_pairs} pairs where the gate predicts 0; chance would give {short_pairs / M:.1f}"
                f" (P of >= {short_d} at the body's pooled rate: {binom.sf(short_d - 1, short_pairs, pooled):.3f})"
            )


if __name__ == "__main__":
    main()
