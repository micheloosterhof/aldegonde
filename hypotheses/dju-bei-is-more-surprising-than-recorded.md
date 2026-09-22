---
type: observation
---
# Observation: The DJU-BEI Repeat Is 1 in 2,700 by Chance, Not 1 in 100

## Why this number matters more than it looks

`models-on-the-informative-cells.md` finds `returns` to be the **only** battery cell
failed by every model in this directory *and* by every deliberately wrong cipher. The
corpus has one exact state return — the DJU-BEI repeat — and nothing simulated produces
one. Its weight rests entirely on how likely such a repeat is by chance, and the figure
this project carries, **"~1%"** from `rotor-machine-compact-state.md`, has never been
rederived.

## Three framings, three orders of magnitude

| framing | P(at least one) | |
|---|---|---|
| any repeated 6-gram anywhere | **0.133** | 1 in 8 |
| **block-aligned, whole blocks, 6+ runes** | **0.00037** | **1 in 2,693** |
| (3,3) units only | 0.000028 | 1 in 35,286 |

Computed from the corpus's own unigram distribution (per-rune match probability 0.03455)
over 2,928 blocks and 12,956 runes.

**The middle framing is the principled one.** A key-state recurrence reproduces the same
alphabet at the same phase, so the repeat it causes *necessarily* starts at a block
boundary and spans whole blocks. That is a prediction of the mechanism, not a filter
chosen after seeing the data. Restricting further to (3,3) is post-hoc; ignoring alignment
tests a different hypothesis altogether.

Longer alignments contribute nothing: at length 7 the expectation is already 1.3 × 10⁻⁵,
so the sum over 6-rune and longer windows is dominated by its first term.

## Confirmed by simulation, September 2026

The figure above is an independence calculation, and the body's runes are not independent:
the adjacent-doublet rate is 0.0063 against a chance 0.0345, and a block whose plaintext
repeats a letter needs fewer than six coincidences to match another block. So it was worth
checking by a method that assumes nothing.

`experiments/dju_bei_chance_rate_simulated.py` enciphers a fixed prose corpus under the
walk with a fresh key each time — **no state return by construction** — and counts corpora
carrying a block-aligned whole-block repeat of 6+ runes:

| | |
|---|---|
| 6,000 simulated corpora, with a repeat | **2** |
| rate | **0.00033** (1 in 3,000) |
| 95% interval | 0.00004 to 0.00120 |
| the analytic figure above | 0.00037 (1 in 2,693) |

The recorded figure sits inside the interval and within 12% of the point estimate. It
holds.

**But the two simulated repeats are not returns.** Checked against the generator's own
state, both have a *different* base and a *different* clock phase at the two occurrences.
A walk with no state return still produces this observable, at about the rate chance
predicts.

*Caution*: recomputing the analytic figure from the corpus's own length-pattern
distribution (2,895 minimal runs over 140 patterns) gives 0.00010, three times lower. The
simulation is the authority since it assumes nothing; the likeliest cause is that counting
only *minimal* runs undercounts the opportunities. Recorded so the 1-in-10,514 is not
mistaken for a correction.

## Consequence

**The DJU-BEI repeat is about thirty times more surprising than the number in
circulation.** At 1 in 2,700 it is not comfortably dismissable as coincidence, and it is
the single observation that separates the corpus from every model and every constructed
control.

That does not make it a state return. It makes the choice sharper: either a 1-in-2,700
coincidence, or a mechanism that returns to a previous state once in 12,956 runes — and
every candidate mechanism in this directory has been shown to produce zero such returns
(`rotor_period_closure.py` excludes autonomous periods ≤ 6,478;
`base_pool_floor.py` shows the base is effectively distinct per block).

## Scope

- The per-rune match probability uses the corpus's unigrams, which are flat, so this is
  barely different from (1/29)⁶.
- Windows are counted with overlap, and overlapping windows are not independent; the
  Poisson approximation slightly overstates P for the unaligned framing and is essentially
  exact for the aligned ones, where the expectation is far below 1.
- The 1-in-8 figure for unaligned repeats is worth keeping in view: if the alignment were
  *not* predicted in advance, there would be nothing to explain.

## Status

**Status**: confirmed (computation from the corpus's own statistics).
`experiments/dju_bei_chance.py`. Supersedes the "~1%" figure.

## Related

- `repeated-phrase-dju-bei.md` — the repeat itself.
- `rotor-machine-compact-state.md` — where "~1%" is recorded.
- `models-on-the-informative-cells.md` — why `returns` is the cell that matters.
