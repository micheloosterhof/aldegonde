---
type: observation
---
# Observation: The Last Slot Holds an Interior Word, and No Structured Rule Beats a Shuffle

## Question

If the body's words were rearranged (`the-words-are-transposed-within-sentences.md`), a
scribe would more plausibly have used a **rule** than a shuffle — something defined for a
sentence of any length, the way a rail fence or a columnar transposition is. Seventeen
such rules are testable directly.

`experiments/which_structured_permutation.py`

## The instrument

Not the mean block length at a span edge, which cancels — `which_edge_is_anomalous.py`
reads the first edge at −0.01 for the author and +0.07 for the body and concludes it
cannot discriminate. The **length-class profile** at each edge does better
(`where_in_the_distribution_is_the_anomaly.py`): four classes at the first edge and four
at the last, eight numbers, against the ten registers with their spread and the body's
own sampling error.

## Result

| rule | χ² first | χ² last | χ² both | P |
|---|---|---|---|---|
| keep first, reverse rest | 5.7 | 1.8 | 7.5 | 0.48 |
| rotate left 2 | 6.7 | 1.4 | 8.1 | 0.42 |
| **full shuffle** | 5.3 | 3.1 | 8.5 | 0.39 |
| rotate left 3 | 5.9 | 2.8 | 8.8 | 0.36 |
| outward-in | 5.8 | 4.1 | 9.9 | 0.27 |
| keep first, shuffle rest | 8.2 | 3.5 | 11.7 | 0.17 |
| rail fence 3, columnar 3, columnar 4 | ~8.3 | 5.2–5.9 | 13.6–14.3 | 0.07–0.09 |
| columnar 2 = rail fence 2 = odd-even split | ~8.1 | 9.5–9.9 | 17.5–18.0 | 0.02 |
| even-odd split | 8.2 | 10.2 | 18.4 | 0.018 |
| swap adjacent pairs | 9.6 | 9.1 | 18.7 | 0.017 |
| rotate left 1 | 8.9 | 10.3 | 19.2 | 0.014 |
| reverse | **22.2** | 6.4 | 28.7 | 0.0004 |
| **identity** | 6.7 | **31.7** | **38.5** | **2e-6** |

**Identity is excluded at 2e-6, entirely on the last edge.** That is the sentence-final
anomaly restated as a profile instead of a mean, and it is the strongest form of it so
far.

**No structured rule beats a full shuffle.** The five best sit within 2.4 of one another
with the shuffle among them. The corpus cannot name a rule.

## What it does constrain

Sorting the rules by what lands in the last slot makes the last-edge misfit nearly
monotone — correlation **+0.71**:

| what lands in the last slot | rules | χ² last |
|---|---|---|
| the sentence's own final word, always | identity | 31.7 |
| that word about half the time | swap pairs, columnar 2, odd-even, even-odd | 9.1–10.2 |
| the sentence's *first* word | rotate left 1, reverse | 10.3, 6.4 |
| that word a quarter to a third of the time | rail fence 3, columnar 3/4 | 5.2–5.9 |
| an interior word, essentially always | rotate 2/3, keep-first-reverse-rest, outward-in, shuffle | 1.4–4.1 |

**The last block of a body span holds a word that was neither its sentence's last nor its
sentence's first.** Rules are penalised in proportion to how often they violate that and
survive whenever they satisfy it.

That is a statement about the destination, not the mechanism, and it is what a
length-only channel can reach. It is consistent with
`lengths_cannot_separate_the_readings.py`: length statistics see multisets and
destinations, never the rule that produced them.

## Falsifiable, and how to break it

- Any rule that places interior words last and still fails would break the +0.71 ordering.
- A rule that places the original final word last and *fits* would break the headline.
- The first edge is claimed only to exclude reversal (χ² 22.2). The body's first-block
  profile does match the author's cell for cell, but the ten registers disagree among
  themselves by ±0.055 and ±0.092 in the first two classes, so against that spread
  identity scores 6.7 and a shuffle 5.3. **"Position 0 is fixed" is not claimed here** —
  it holds against the author and not against the registers.

## Caveat on order of operations

The rearrangement is applied *before* the short-unit joining, on the grounds that a
scribal rearrangement precedes a scribal merge. The reverse order is untested and could
move the marginal rules (columnar 3/4, rail fence 3) in either direction.

## Seed audit: the χ² values are stable

`experiments/are_the_headline_numbers_seed_stable.py`

Every arm in this file applies the joining model to the ten registers **once**. After a
single stochastic draw was found to have flipped a conclusion elsewhere
(`what_would_it_take.py`), these were re-run under forty independent joining seeds:

| rule | published | median | spread | range |
|---|---|---|---|---|
| identity | 38.5 | 39.6 | 0.6 | 38.5 to 40.9 |
| reverse | 28.7 | 28.1 | 0.5 | 26.9 to 29.2 |
| full shuffle | 8.5 | 9.7 | 0.6 | 8.2 to 10.8 |
| keep first, reverse rest | 7.5 | 7.6 | 0.1 | 7.5 to 8.0 |

**A spread of 0.6 on 39.6 does not move a P value.** Identity stays excluded at 2e-6 and
the ranking is unchanged. The published identity-minus-shuffle gap of 30.0 matches the
median gap of 29.9.

The reason these are safe while the author's lag-1 was not is the size of the reference:
ten registers pool 30,281 sentences and average the joining noise away before the
statistic is formed, where the author has 94 spans. Draw-to-draw spread is 1.5% of the
value here and 100% of it there.
