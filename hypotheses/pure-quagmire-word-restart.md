---
type: hypothesis
---
# Hypothesis: A Plain Quagmire Restarting in Every Word

## Claim

Michel's proposal (September 2026). Drop `g` and σ. No general permutation anywhere.
One keyed alphabet `K`, a five-step shift schedule, the key restarting at a fixed offset
in every word — "probably not at 1" — and the doublet preventer on top. In K coordinates
every operation is then a shift:

```
c_j = K[ (pos_K(p_j) + u_w + S[(r + j) mod 5]) mod 29 ]
```

with `r` the restart offset and the preventer advancing the phase on a repeat.

## Status

**Status**: the restart is **disproved**. The rest of the proposal is not, and one part
of it is new and useful: the general permutation σ is not needed, only a per-word step
with enough states.

## The restart dies on the seam

The corpus suppresses doublets inside words (d1w 0.0063) and across word boundaries
(seam 0.0079) at nearly the same rate — a ratio of 1.25.

Inside a word the preventer fails at one phase in five, which is where the surviving
doublets come from, so d1w = (1/5) × a diagonal. A word boundary is that same event at
whichever phase the clock happens to be on. A **fixed** restart puts every boundary on
the same phase `r`, so the preventer there fails at every boundary or at none, according
to whether `offsets[(r+1) % 5]` is the zero one. The seam is therefore bimodal.

Measured over 16 draws (`experiments/pure_quagmire_restart.py`), seam ÷ d1w:

| boundary phase | draws | ratio |
|---|---|---|
| sits on the zero offset | 6 | 3.4, 8.2, 10.3, 11.7, 23.8, 25.5 |
| does not | 10 | 0.0 (every draw) |
| **the corpus** | | **1.25** |

Neither branch contains it, and the split does not depend on the keyword, the schedule
or the per-word step — only on which phase the boundaries sit at.

**The escape is closed.** A preventer that stopped at the word break would leave the
seam unsuppressed and free of the bimodality. It reads 0.0355 then, against chance
0.0345 and the corpus's 0.0079. So the corpus's boundary really is suppressed and the
preventer really does run across it.

A ratio near 1 needs the boundaries spread over all five phases. That is a clock that
runs **on** through the word break, which is the opposite of a restart. The existing
models have it, which is why their seam lands.

## What survives: σ need not be a permutation

Two measurements on the parts of the proposal the seam does not touch. Both use a prose
register matched to the LP's word lengths, which matters: `identical` counts only words
of MIN_WORD runes or more, and unmatched prose has longer words and so understates the
collisions.

**The IoC permits an all-shift cipher.** With nothing changing between words the text
uses five alphabets and reads nIoC 1.2816 against the corpus's 0.9999 — dead. One
per-word shift covers all 29 residues in K coordinates and washes the excess out
completely, 0.9999. So the per-word step is not optional, and it also need not be a
general permutation to flatten the corpus.

**Identical words set the step's size.** The corpus holds 17 pairs of equal words.

| per-word states | nIoC | identical |
|---|---|---|
| 1 (nothing changes) | 1.2447 | 13,086 |
| 5 | 1.0642 | 2,716 |
| 29 (one shift) | 1.0064 | 478 |
| 145 (shift and restart) | 1.0017 | 110 |
| 841 | 1.0004 | 33 |
| 4,000 | 1.0002 | 20 |
| 20,000 | 0.9999 | 15 |
| **the corpus** | **0.9999** | **17** |

So the per-word step needs on the order of 5,000–10,000 states. σ, a general
permutation, has far more than needed; one shift has far too few.

**A caution on reaching that budget with shifts.** A per-word state that is a LINEAR
function of the word index has 29 values however many dials it carries, because dials
advancing at fixed rates stay on a line. Two dials each stepping by 1 give 480 identical
pairs — the same as one dial. Drawn independently they give 30, close to the corpus's
17. So two **decorrelated** dials would meet the budget: an odometer with a carry, or an
advance that depends on the word rather than on its index.

## What to do next

1. **Build the odometer version.** One shift inside K and one outside, the second
   advancing only when the first wraps, giving 841 states, or 4,205 with the restart
   folded in. It has no general permutation and it is a much smaller key than σ. The
   clock must run on through the word break, not restart.
2. **Check it against the whole battery**, not the four cells used here.
3. Note it inherits the scorer problem of `quagmire-dodge.md`: any model with the
   doublet preventer is invisible to `walk_score_kernel`, which assumes clock =
   position.

## Scripts

- `experiments/pure_quagmire_restart.py` — the three restart variants, the state-budget
  pool sweep, the bimodal seam and the unsuppressed-boundary control.

## Related

- `quagmire-dodge.md` — the same preventer on a continuous clock, which is what the seam
  says the clock must be.
- `doublet-dodge-walk.md` — where the preventer's seam/within-word equality is recorded
  as automatic; this file shows the equality is evidence about the CLOCK, not just the
  rule.
- `length-clocked-walk.md` — the incumbent, whose σ this proposal tried to remove.

## Verdict

The restart at a fixed phase is disproved by the seam, cleanly and independently of the
rest of the key. The larger idea behind the proposal survives and is worth pursuing: the
per-word step has to supply thousands of states, but nothing requires it to be a general
permutation, and two decorrelated shift dials would do. That is a genuinely smaller key
than σ.
