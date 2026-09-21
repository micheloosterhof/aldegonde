# ABOUTME: A doublet preventer that re-emits with the next alphabet WITHOUT advancing the
# ABOUTME: clock, which makes the surviving doublets' clock phase readable off the corpus.
"""A preventer that does not move the clock, and the test that opens up.

`space-eats-clock-steps.md` records the obstacle: every test needing the absolute clock
phase is unavailable while the preventer skips clock steps, because the skips are
invisible in the ciphertext and drift the phase by a full period every 111-161 runes.

The skip is separable from the suppression. The dodge does two things at once — it
re-emits with the NEXT alphabet, and it advances the clock. Keep the first and drop the
second:

    c = A_k(p);  if c == previous:  c = A_(k+1)(p)      the clock still goes k -> k+1

The failure condition is untouched. The re-emission repeats only when
`A_(k+1)(p) = A_k(p)`, which is `s_(k+1) = 0`, so a schedule with one zero offset still
admits doublets at one clock phase in five and forbids them at the other four. The
doublet rate is still (1/5) x a diagonal.

Three things change, all for the better.

**The clock is readable.** Position j is at clock phase `(start + j + k x word) mod 5`
for a space eating `k` steps, with no drift term. So the phase of every surviving
doublet can be computed from the corpus.

**Decoding errors cannot propagate.** Both readings at an ambiguous position leave the
clock at k+1, so a wrong choice costs that rune and nothing after it. The dodge's wrong
branch carried a permanent clock offset.

**A prediction lands on the LP.** Under a one-zero schedule EVERY surviving doublet sits
at the same clock phase. The corpus holds 63 within-word doublets and 23 at the seam, so
86 events across five classes. If one value of `k` concentrates them and the others do
not, that settles both the preventer's shape and the space convention at once.

Run with no arguments.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from ea_direction_test import PROSE_CACHE  # noqa: E402
from fingerprint_battery import M, fingerprint, lp_words  # noqa: E402
from pure_quagmire_restart import matched_register, running, schedule  # noqa: E402
from quagmire_runner import load_clean, load_register  # noqa: E402

SKIPS = (0, 1, 2, 3, 4)


# The preventer does two separable things: it re-emits with a NEIGHBOURING alphabet, and
# it changes how far the clock moves. Michel's negative skip is the second row's mirror.
#
#   name        escape uses   clock on a fire   fails when        drift per rune
#   advance     A_(k+1)       k + 2             offsets[k+1] = 0  +q
#   re-emit     A_(k+1)       k + 1             offsets[k+1] = 0   0
#   hold        A_(k-1)       k                 offsets[k]   = 0  -q
#   back        A_(k-1)       k + 1             offsets[k]   = 0   0
VARIANTS = {
    "advance": (+1, 2),
    "re-emit": (+1, 1),
    "hold": (-1, 0),
    "back": (-1, 1),
}


def encipher(plain, K, offsets, start, space_skip=0, variant="re-emit"):
    """The odometer Quagmire with one of the four preventer variants."""
    direction, advance = VARIANTS[variant]
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    a, b = start
    out, previous, clock = [], None, 0
    for word in plain:
        cipher_word = []
        for p in word:
            c = (K[(pos[p] + a + S[clock % 5]) % M] + b) % M
            step = 1
            if c == previous:
                c = (K[(pos[p] + a + S[(clock + direction) % 5]) % M] + b) % M
                step = advance
            cipher_word.append(c)
            previous = c
            clock += step
        out.append(cipher_word)
        clock += space_skip
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    return out


def clock_drift(plain, K, offsets, start, variant) -> float:
    """Clock steps per rune minus one: zero means the phase stays readable."""
    direction, advance = VARIANTS[variant]
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    a, b = start
    previous, clock, runes = None, 0, 0
    for word in plain:
        for p in word:
            c = (K[(pos[p] + a + S[clock % 5]) % M] + b) % M
            step = 1
            if c == previous:
                c = (K[(pos[p] + a + S[(clock + direction) % 5]) % M] + b) % M
                step = advance
            previous = c
            clock += step
            runes += 1
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    return clock / runes - 1.0


def doublet_phases(words, space_skip: int):
    """Clock phase of the second rune of every doublet, within words and at seams.

    The phase is `(j + space_skip x word_index) mod 5`, exact because this preventer
    never moves the clock. An unknown starting phase only rotates the labels, which a
    concentration test does not care about.
    """
    phases = []
    j = 0
    previous = None
    for w, word in enumerate(words):
        for r in word:
            if previous is not None and r == previous:
                phases.append((j + space_skip * w) % 5)
            previous = r
            j += 1
    return phases


def concentration(phases) -> tuple[float, int, list[int]]:
    """Chi-square against a flat spread over five phases, plus the fullest class."""
    counts = [phases.count(r) for r in range(5)]
    expected = len(phases) / 5
    chi2 = sum((c - expected) ** 2 / expected for c in counts)
    return chi2, int(np.argmax(counts)), counts


def self_test() -> None:
    rng = random.Random(3301)
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]
    pools, _t, _f = load_register(PROSE_CACHE)
    lp = fingerprint(lp_words())

    K = rng.sample(range(M), M)
    offsets = schedule(rng)
    start = (rng.randrange(M), rng.randrange(M))
    plain = matched_register(rng, lens, pools)

    got = fingerprint(encipher(plain, K, offsets, start))
    print(f"schedule {offsets} (one zero offset)")
    print(
        f"doublet rate {got['d1w']:.5f} against the corpus's {lp['d1w']:.5f}; "
        f"seam {got['seam']:.5f} against {lp['seam']:.5f}"
    )
    assert got["d1w"] > 0, "a one-zero schedule must still admit doublets"

    # the control: with no zero offset the re-emission can never repeat
    clean = fingerprint(encipher(plain, K, schedule(rng, zeros=0), start))
    print(f"no zero offset in the schedule: doublet rate {clean['d1w']:.5f}")
    assert clean["d1w"] == 0.0, "without a zero offset the preventer cannot fail"

    # the payoff: on ciphertext this model made, every doublet sits at one phase
    truth = doublet_phases(encipher(plain, K, offsets, start, space_skip=2), 2)
    chi2, best, spread = concentration(truth)
    print(f"\nsimulated corpus, space eating 2 steps: {len(truth)} doublets")
    print(f"   phase counts {spread}, all in phase {best}: chi2 {chi2:.1f}")
    assert spread.count(0) == 4, (
        "with the clock undisturbed every surviving doublet must share one phase"
    )
    wrong = concentration(doublet_phases(encipher(plain, K, offsets, start, 2), 0))[2]
    print(f"   read with the WRONG skip (0 instead of 2): {wrong}")
    assert wrong.count(0) < 4, "the wrong skip must smear the phases"

    variant_table(plain, K, offsets, start, lp)
    print("\nself-test passed")


def variant_table(plain, K, offsets, start, lp) -> None:
    """All four preventers: the doublet rate, the clock drift, and the phase spread.

    Michel's negative skip is `hold`. It suppresses doublets by the same one-zero
    mechanism as the dodge, with a different offset carrying the zero, and it drifts the
    clock BACKWARD at the same rate the dodge drifts it forward. So it hides the phase
    just as effectively.

    `back` is its drift-free mirror, the negative counterpart of `re-emit`.
    """
    print(
        f"\n{'variant':<10}{'escape':>10}{'fires':>9}{'d1w':>9}"
        f"{'drift/rune':>12}{'phase spread on its own output':>34}"
    )
    for name, (direction, _advance) in VARIANTS.items():
        cipher = encipher(plain, K, offsets, start, space_skip=2, variant=name)
        cells = fingerprint(cipher)
        drift = clock_drift(plain, K, offsets, start, name)
        counts = concentration(doublet_phases(cipher, 2))[2]
        readable = "concentrated" if counts.count(0) == 4 else "smeared"
        print(
            f"{name:<10}{f'A(k{direction:+d})':>10}{sum(counts):>9}"
            f"{cells['d1w']:>9.5f}{drift:>12.4f}   {str(counts):<22}{readable}"
        )
    print(
        f"\nthe corpus reads d1w {lp['d1w']:.5f}. Drift-free variants put every"
        "\nsurviving doublet at one phase; drifting ones scramble it, which is exactly"
        "\nwhy only the drift-free pair can be tested against the LP."
    )


def on_the_corpus() -> None:
    """Run the prediction against the LP."""
    words = lp_words()
    print(f"{len(words)} words\n")
    print(f"{'space skip':>11}{'doublets':>10}{'phase counts':>22}{'chi2':>9}{'p':>9}")
    rows = []
    for k in SKIPS:
        phases = doublet_phases(words, k)
        chi2, _best, counts = concentration(phases)
        # four degrees of freedom; survival of the chi-square by series
        p = math.exp(-chi2 / 2) * (1 + chi2 / 2)
        rows.append((chi2, k, counts, p))
        print(f"{k:>11}{len(phases):>10}{str(counts):>22}{chi2:>9.1f}{p:>9.3f}")
    best = max(rows)
    print(
        f"\nthe model predicts ONE class holding all {sum(rows[0][2])} and four at zero."
    )
    print(
        "this covers BOTH drift-free preventers. The negative escape only changes which"
        "\noffset must be zero, which rotates the labels, and the test ignores rotation."
    )
    print(
        f"the strongest reading is skip {best[1]} at chi2 {best[0]:.1f} "
        f"(p {best[3]:.3f} before correcting for trying {len(SKIPS)} skips)."
    )
    flat = sum(rows[0][2]) / 5
    print(f"a flat spread would put {flat:.1f} in each class.")


if __name__ == "__main__":
    self_test()
    print()
    on_the_corpus()
