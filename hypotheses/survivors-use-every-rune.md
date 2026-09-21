---
type: observation
---
# The Surviving Doublets Use Every Rune, Which Kills the Substitution Preventer

## Status

**Status**: confirmed, and the refutation is arithmetic rather than statistical. It
needs no key, no model fit and no surrogate corpus — the corpus answers it directly.

## The discriminator

`nothing-else-in-the-book-suppresses-repeats.md` establishes that the body's cipher
inspects its own output and refuses to repeat, and that it fails about one time in five:
**86 doublets survive where 448 are expected, 81% suppression.**

The three candidate preventers disagree sharply about *which* 86.

| rule | what survives | prediction |
|---|---|---|
| **substitution** — emit `τ(c)` instead of `c` | exactly the `c` with `τ(c) = c` | survivors confined to `fix(τ)` |
| **clock dodge** — re-run the clock | whatever the second emission happens to be | spread over all 29 by frequency |
| **probabilistic** — skip with probability φ | rune-independent by construction | spread over all 29 by frequency |

The battery cannot separate these — `battery-cells-test-the-key.md` shows only four of
nineteen cells move between the shapes at all, and the informative ones are
key-determined. This statistic separates them with no key at all.

## The measurement

`experiments/which_runes_survive.py`

**The 86 survivors use 28 of the 29 runes.** The one missing is B. Spread over runes in
proportion to rune frequency: χ² = 27.8 on 28 df — a textbook fit.

| statistic | observed | null | z |
|---|---|---|---|
| share held by the top 6 runes | 0.372 | 0.379 ± 0.030 | −0.22 |
| share held by the top 8 runes | 0.465 | 0.474 ± 0.032 | −0.27 |
| share held by the top 12 runes | 0.640 | 0.637 ± 0.033 | +0.09 |
| runes with no survivor | 1 | 1.5 ± 1.1 | −0.43 |

The survivors are spread exactly as a rune-blind rule predicts.

## The refutation

Two bounds on the same quantity, from two different measurements, and they do not meet.

- **From below.** Every survivor is a fixed point of τ, so the number of *distinct*
  runes among the survivors is a lower bound: `|fix(τ)| ≥ 28`.
- **From above.** A would-be doublet survives with probability `|fix(τ)|/29`, so 81%
  suppression forces `|fix(τ)| = 0.19 × 29 ≈ 5.6`.

**No permutation of 29 points satisfies both.** A τ that fixes 28 points fixes all 29 —
it is the identity, and suppresses nothing.

This is not a p-value. It does not depend on the key, on `g`, on `σ`, or on a prose
surrogate. The substitution preventer is wrong in its stated form.

What survives the argument is a rule whose *failures are rune-blind*: the clock dodge,
the probabilistic preventer, or any rule whose substitution varies with position or state
rather than being one fixed τ. The last is worth saying explicitly — a τ drawn fresh at
each collision would be rune-blind and is untouched here, but it is a different model
with a different key.

## The other half: where the suppressed doublets went

The argument above is about the 86 that survived. `experiments/where_the_doublets_went.py`
follows the 361 that did not.

Whatever the rule emitted instead landed in the off-diagonal bigram table, and the shape
of the landing measures how many distinct substitutions could be in play. With one fixed
τ the mass falls in 29 cells, one per row, each gaining 361/29 = **12.4 on a base of
15.8** — an eighty percent bump. With k substitutions it splits 29k ways. A rune-blind
rule spreads it over all 812 cells at 0.44 each, which is invisible.

Observed: off-diagonal χ² **841.2 on 811 df**, largest standardised row maximum **3.70**.
Planting the same 361 into k one-per-row targets:

| k | off-diagonal χ² | largest row-max z | |
|---|---|---|---|
| rune-blind | 814 ± 39 (z +0.7) | 3.47 ± 0.43 (z +0.5) | **the corpus sits here** |
| 1 | 1086 ± 48 (z −5.2) | 5.77 ± 0.67 (z −3.1) | **excluded** |
| 2 | 945 ± 46 (z −2.3) | 4.34 ± 0.62 (z −1.0) | **excluded** |
| 3 | 899 ± 45 (z −1.3) | 3.92 ± 0.55 (z −0.4) | open |
| 6 | 856 ± 42 (z −0.4) | 3.65 ± 0.48 (z +0.1) | open |

So a substituting preventer is not refuted outright by this second test — but it needs
**at least three distinct substitutions**, three more permutations of key doing what one
clock re-run does for nothing. That is a parsimony argument and should be quoted as one;
the arithmetic refutation above is the one that stands on its own, and it applies to the
single-τ case.

## Placement says nothing more

A rule that failed in bursts would show it. It does not.

| statistic | observed | null | |
|---|---|---|---|
| smallest gap | 6 | 2.3 ± 1.7 | P = 0.057 |
| gaps of 20 or less | 6 | 10.6 ± 2.9 | z = −1.61 |
| gap coefficient of variation | 0.945 | 0.978 ± 0.101 | z = −0.33 |
| by decile of the corpus | | | χ² 13.8 on 9 df |

The survivors sit where chance puts them, with a mild reluctance to fall close together
that reaches about 1.5 sigma and is what `doublet_gap_min` has been reporting.

## Consequences

- `seam-to-d1w-ratio-is-a-constraint.md` names the substitution shape as the one the
  seam ratio leaves open. It is now closed by a different measurement, and the ratio
  argument needs a different candidate.
- Any future preventer must be **rune-blind in its failures**. That is a sharper version
  of constraint D5 (context-free failures): not only must the failure rate be the same at
  a seam as inside a word, it must be the same for every rune.
- The 81% figure is now doing real work. It is no longer only a fitted quantity; combined
  with the survivor count it excludes a whole family.

## Falsification

- If the suppression rate is not 81% — if some doublets are lost to transcription, say —
  the upper bound on `|fix(τ)|` moves. It would have to reach 28, meaning suppression
  under 4%, against a measured 81%.
- If the body's cipher is not bijective at every position the counting argument changes.
  `the-body-passes-nothing-through.md` rules out the one non-bijective convention the
  author is known to use.
- A position-dependent or state-dependent substitution is not excluded and would be
  worth modelling separately.

## Scripts

- `experiments/which_runes_survive.py`

## Related

- `nothing-else-in-the-book-suppresses-repeats.md` — the 81% this uses.
- `substitution-preventer` (`experiments/substitution_preventer.py`) — the model refuted.
- `battery-cells-test-the-key.md` — why a key-free discriminator was needed.
