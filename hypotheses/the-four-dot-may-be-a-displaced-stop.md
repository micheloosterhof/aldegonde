---
type: hypothesis
---
# Hypothesis: The Four-Dot Is a Full Stop Written a Variable Block or Two Off

## Status

**Live.** Not excluded, fits the offset profile as well as any surviving reading, and is
the only reading that keeps the four-dot a sentence mark.

`experiments/a_shifted_stop_or_a_switched_key.py`

## What was already excluded

`the_long_block_is_nowhere.py` rules out every **fixed** displacement. Mean block length at
each offset from a mark shows the body's largest value anywhere in ±4 is +0.44 at offset
+3, against English's +1.19 at −1; each constant shift scores −2.6σ or worse.
`which_permutation_survives.py` extends that to −12.

## What was not

A **variable** shift. If the mark falls one block past the stop sometimes and two or none
at other times, the long sentence-final block is spread over several offsets and every
per-offset mean is diluted. No constant shift describes it, so the fixed-displacement scan
cannot see it.

The instrument is a forward model. English's whole offset profile is smeared by each
candidate shift distribution, and the body is scored against the result.

| offset | ten registers | the LP author | the LP body |
|---|---|---|---|
| −4 | +0.03 ± 0.07 | +0.19 | +0.05 ± 0.26 |
| −3 | −0.01 ± 0.10 | +0.22 | −0.23 ± 0.22 |
| −2 | −0.22 ± 0.07 | −0.09 | +0.04 ± 0.22 |
| **−1** | **+1.22 ± 0.26** | **+0.85** | **−0.16 ± 0.24** |
| +1 | −0.69 ± 0.21 | −0.12 | +0.08 ± 0.28 |
| +2 | −0.12 ± 0.16 | −0.72 | +0.35 ± 0.26 |
| +3 | −0.05 ± 0.11 | −0.15 | +0.47 ± 0.27 |
| +4 | +0.02 ± 0.07 | −0.57 | −0.15 ± 0.24 |

| the mark is | χ², 8 offsets | P |
|---|---|---|
| exactly at the stop | 28.3 | **0.0004** |
| displaced by up to ±1 block | 13.0 | 0.11 |
| displaced by up to ±2 | 12.3 | 0.14 |
| displaced by up to ±3 | 8.1 | 0.43 |
| displaced by up to ±4 | 5.0 | 0.75 |
| unrelated to any stop | 5.6 | 0.69 |

**A stop exactly at the mark is excluded. A stop displaced by a variable block or two is
not.**

## The limit of the test, stated plainly

The fit improves as the smear widens, and by ±3 it is indistinguishable from "unrelated to
any stop" (8.1 and 5.0 against 5.6). Smearing flattens the profile, and a flat profile is
what every surviving reading predicts. So this does not favour a displaced stop over the
alternatives; it removes the objection that displacement had been ruled out.

A symmetric window mean or maximum cannot be used here. English puts +1.19 at offset −1
and −0.71 at +1, so any symmetric window averages them away: planting a ±1 to ±3 shift in
English moves the ±2 window mean from +0.05 to at most +0.08. That was the first
instrument tried and it had no power.

## Why a scribe might displace a stop

Unstated, and that is a weakness. The hypothesis is currently a shape that fits, not a
mechanism. A mechanism would have to explain why the displacement varies rather than being
constant — a mark written at the end of the line containing the stop, or after the first
word of the next clause, would both give small variable shifts and are separately
testable against the layout.

## Falsifiable

- The layout version is directly checkable: if the mark is written at the end of the line
  holding the stop, its line-end rate would be high. **CORRECTED:** it is 0.106 against a
  word separator's **0.039**, not 0.115 — the earlier baseline was contaminated by
  annotation hyphens. At +4.02σ the four-dot *is* line-break coupled, so **this version is
  live rather than dead**, though the coupling is far weaker than real punctuation's
  (5.7× its baseline against the four-dot's 2.7×).
- A larger corpus sharpens the ±1 row: at P = 0.11 it is the only smear still close to
  rejection.
- Any channel that locates a sentence end independently would settle it. The red ink does
  this for ⑬ and not for ④.

## The gap law supports this reading, weakly

`experiments/are_the_four_dot_gaps_memoryless.py`

The body's 137 four-dot gaps, in blocks, have the **mean of English sentences** (21.40
against 22.76) and the **shape of the author's own spans** (7.65 mean, but the right
short-gap deficit). Thinning the author's sentence ends to p = 0.357 reproduces both, and
wins the binned likelihood comparison:

| arm | log-likelihood | ratio |
|---|---|---|
| the author's spans, thinned to p = 0.357 | −239.07 | 1.000 |
| the LP author's spans | −240.52 | 0.235 |
| memoryless (geometric) | −241.08 | 0.134 |
| English sentences, joined | −242.11 | 0.048 |

4.3 to 1 over the next arm is weak, and the control says why: thinned-author and
memoryless are only separated 70% of the time at n = 137. The well-separated arms (English
joined 94%, author unthinned 92%) are the two the body rejects.

**Why it matters here.** A thinned-sentence-end gap law says every four-dot sits at a real
sentence end. This reading is one of only two that can hold that together with the missing
lengthening — a mark displaced by a variable block or two keeps the gap law intact while
the block immediately before it is no longer the sentence's last word. The other is
`the-words-are-transposed-within-sentences.md`.

The reading it weighs against is "the four-dot is unrelated to the syntax"
(`the-four-dot-is-not-layout-coupled.md`), which has no account of why the gaps should fit
thinned sentence ends at all. That reading still holds the layout channel, which this does
not touch.

## The thinning reading is dead

`experiments/the_thinning_model_is_dead.py`

The gap law fits the author's own spans thinned to p = 0.357 at 4.3 to 1 over the next arm
(`are_the_four_dot_gaps_memoryless.py`), and that has been treated here as compatible with
the missing lengthening. It is not.

**Thinning's p is the share of sentence ENDS that carry a mark, not the share of MARKS
that sit at ends** — the latter is 1 by construction, since a thinned process marks a
subset of real ends and nothing else. Reading p as though it described the marks is what
made the two look compatible.

The rank statistic measures the share of marks at genuine ends directly:

| model | predicted f | σ away from the measured −0.131 ± 0.156 |
|---|---|---|
| **thinning: every mark is a sentence end** | 1.000 | **7.2** |
| a mixture at the layout rate | 0.106 | 1.5 |
| no four-dot is a sentence end | 0.000 | 0.8 |

**Excluded at seven sigma.** So the gap law's 4.3-to-1 preference on 137 gaps is a
coincidence of shape, not evidence for a mechanism — which is what a weak likelihood ratio
looks like when a sharp test arrives.

The standing tension between spacing and content resolves by the spacing losing. What
survives is unchanged: a small mixture at the layout rate and no-mark-is-an-end are 1.5σ
and 0.8σ away respectively, and the corpus cannot separate them.
