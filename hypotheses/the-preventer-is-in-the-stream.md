---
type: observation
---
# Observation: The Doublet Suppression Crosses Line Breaks, So It Is Not Done By Eye

## Question

The body's adjacent-repeat rate is 0.0063 against a chance 0.0345 — a 17σ deficit and the
largest single signal in the corpus. `the_transposition_precedes_the_cipher.py` shows it
also acts across a word boundary, the seam rate being 0.0079. Nothing had tested whether
it acts across a **written line break**.

The distinction is sharp. To an algorithm a line break does not exist: the runes are a
stream and the line is layout. To a person checking his own output for a repeated rune, a
line break is where a repeat stops being visible — the two runes sit at opposite ends of
the page.

`experiments/does_the_preventer_cross_a_line_break.py`

## Result

| cell | pairs | doublets | rate | vs chance |
|---|---|---|---|---|
| inside a word, no line break | 9,640 | 60 | 0.0062 | −15.21 |
| inside a word, across a line break | 388 | 3 | 0.0077 | −2.89 |
| across a separator, no line break | 2,722 | 22 | 0.0081 | −7.55 |
| across a separator and a line break | 205 | 1 | 0.0049 | −2.32 |
| **all straddling a line break** | **593** | **4** | **0.0067** | |
| **all not straddling one** | **12,362** | **82** | **0.0066** | |

The two rates agree to the fourth decimal place. An eye rule predicts 20.4 doublets among
the 593 straddling pairs and four were found: **P = 9.3e-06**, likelihood ratio **25,700
to 1** for a stream rule.

**No cell escapes suppression** — not across a word boundary, not across a line break, not
across both.

## Consequence

The suppression is a property of the rune stream, not of the page. This supports the
preventer as a cipher-level mechanism — a clock perturbation applied while enciphering —
which `doublet-suppression-requires-design.md` assumes and had not tested, and which
`the-preventer-is-strictly-adjacent.md` characterises.

It also matters for the drift correction in `key-local-channel-is-empty.md`: a stream-level
preventer perturbs the clock, and a scribal one would not, so the `(1−q)^k` attenuation on
the d-profile is the right model rather than an assumption.

## What it does not settle

A scribe who applied the rule to his **exemplar** before copying it into the final layout
would show exactly this pattern, because the line breaks did not yet exist. The result is
"not applied by eye at write time", not "not scribal at all".

## Falsifiable

- Find any cell defined by layout — line position, column, page edge — where the doublet
  rate rises toward chance.
- The 205 pairs crossing both a separator and a line break carry one doublet against 7.1
  expected at chance; a larger corpus that moved that cell toward chance would reopen this.

## The full census: the stream crosses everything testable

`experiments/what_does_the_suppression_cross.py`

Classifying every adjacent rune pair by what lies between the two runes:

| between | pairs | doublets | rate | LR for a continuing stream |
|---|---|---|---|---|
| nothing (inside a word) | 9,640 | 60 | 0.0062 | (the baseline) |
| a separator only | 2,587 | 21 | 0.0081 | 3e+16 to 1 |
| a line break only | 389 | 3 | 0.0077 | 403 to 1 |
| **a mark (any dot cluster)** | **156** | **1** | **0.0064** | **16 to 1** |
| a separator and a line break | 124 | 1 | 0.0081 | 6 to 1 |
| a page break | 45 | 0 | 0.0000 | unresolvable |
| a section break | 14 | 0 | 0.0000 | unresolvable |

**The mark cell reads the within-word rate.** One doublet where a break at the mark
predicts 5.4: P = 0.028 against a break. At 16 to 1 this is support rather than proof.

### Why this is a new claim about the mark

Three different things are now excluded at the four-dot, and they are not the same claim:

| claim | what it would change | test | result |
|---|---|---|---|
| the base resets | which alphabet | `does_the_cipher_restart.py` | z = −0.96 against +53 planted |
| the key cycles | which alphabet, periodically | `a_shifted_stop_or_a_switched_key.py` | nothing at any period to 8 |
| **the stream breaks** | **what counts as adjacent** | this file | 16 to 1 against |

The preventer is the only instrument that can see the third, because it is the only
mechanism in the model that depends on adjacency.
