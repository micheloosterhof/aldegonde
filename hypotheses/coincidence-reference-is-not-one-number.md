---
type: observation
---
# Observation: "What a Shared Alphabet Gives" Is a Table, Not 1.74

## A constant several files take on trust

Results here are routinely priced against "what a shared alphabet would give", quoted as
**1.74** — that is 0.060 × 29. `rotor-machine-compact-state.md` lists it explicitly under
*taken on trust, not verified here*. `d5-partial-alphabet-leak.md` quietly uses a
different figure, ~1.60, noting that 1.74 belongs to a random dictionary word **list**
rather than to running text.

Both approximate something that is not a constant. If two positions share an alphabet they
coincide at the plaintext's coincidence rate **for that kind of pair**, which depends on
whether the pair sits inside one word and how far apart it is.

## The table, measured on both references

| pair type | LP plaintext | runeglish prose |
|---|---|---|
| **unconditional (cross-block)** | **1.788** (1,963) | **1.783** (127,456) |
| within-block d = 1 | 0.628 (1,477) | 1.055 (95,799) |
| within-block d = 2 | 1.238 (1,007) | 0.986 (65,833) |
| within-block d = 3 | 1.643 (653) | 1.451 (43,083) |
| within-block d = 4 | 1.943 (418) | 1.533 (27,314) |
| within-block d = 5 | 1.667 (261) | 1.557 (16,858) |
| within-block d = 6 | 1.973 (147) | 1.576 (9,847) |
| within-block d = 7 | 2.231 (78) | 1.939 (5,413) |
| **within-block d = 2..4, pair-weighted** | **1.507** | **1.243** |

Two things stand out.

**For cross-block pairs the reference is 1.79, not 1.74**, and the two corpora agree to
three decimals — 1.788 against 1.783 on 1,963 and 127,456 runes. That row is solid and
register-independent.

**For within-block pairs a single constant is wrong by up to a factor of three**, running
from 0.63 to 2.23 on the LP's own words. Distance 1 is the known register split — the LP
suppresses adjacent repeats where prose does not (`lp-plaintext-register.md`, z = −2.73) —
and everywhere else the two agree inside their error bars.

## What it changes

Nothing that was measured against **planted controls**, which is most of the recent work:
`g-has-more-than-one-cycle.md`, `sigma-moves-almost-every-rune.md` and
`no-block-partition.md` all calibrate against simulations rather than the constant. Their
conclusions stand.

It changes the *interpretive* figures quoted alongside them. Where a file says "a shared
alphabet reads about 1.74" for a pooled d = 2..4 statistic, the right figure is **1.51**;
for a cross-block same-position statistic it is **1.79**. Those have been corrected.

## Status

**Status**: confirmed (measurement on 1,963 LP runes and 127,456 prose runes).

*Register note, October 2026.* The LP side is the eleven-page register. On the
sixteen-page one (2,882 runes) the unconditional coincidence is 1.778× chance against the
1.788× recorded here — the headline agreement with prose's 1.783 is unchanged to two
decimals. The within-block rows are measured on fewer pairs than the unconditional one
and move more; recompute them before quoting any individual lag.
`experiments/coincidence_reference.py`. Supersedes the trusted constant wherever a pair
type is identifiable.

## Related

- `rotor-machine-compact-state.md` — where the constant is flagged as unverified.
- `d5-partial-alphabet-leak.md` — which already used 1.60 for the d5 row.
- `lp-plaintext-register.md` — the d1 register split.
