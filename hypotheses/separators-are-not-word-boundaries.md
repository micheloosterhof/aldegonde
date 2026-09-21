---
type: hypothesis
---
# Hypothesis: The Body's Separators Mark Cipher Blocks, Not Plaintext Words

## The measurement, on data no cipher touches

Every cipher still entertained here is position-preserving. The ciphertext has the same
runes in the same places, so the **sequence of word lengths passes through untouched** —
whatever the body's plaintext is, its word-length sequence is already readable.

English word lengths are strongly serially dependent: short function words alternate with
long content words. The statistic is the G² of the length-transition table, bucketed at
6+, against a surrogate that shuffles the same lengths within the same page or section.
Reported per pair, so corpora of different sizes compare directly.

| corpus | words | excess G² per pair |
|---|---|---|
| prose, six Gutenberg books carried into runeglish | 120,000 | 0.0484 ± 0.0160 |
| the LP's own solved plaintext | 723 | 0.0397 ± 0.0101 |
| **the unsolved body** | **2,928** | **0.0039 ± 0.0025** |

The two references agree with each other — one register-matched and noisy, one
register-mismatched and tight — and the body sits an order of magnitude below both, on
four times the plaintext's data. Against the LP's own plaintext that is **z = +3.46**;
against prose, **z = +2.75**.

The body's own excess, 0.0039 ± 0.0025, is consistent with **zero**.

## Why the significance is 3σ and not 15σ

A naive comparison — the body's G² of 36.3 against what the plaintext rate predicts,
138.5, divided by the body's own surrogate spread — reads 15σ. That is wrong. The
reference is measured on 723 words and carries ±0.0101 of its own, which dominates the
comparison. Propagating it gives 3.5σ. The same error class as
`scan-maxima-need-surrogate-nulls`: the uncertainty that matters is the one in the
quantity being compared against.

## The merge family, swept properly, cannot fit both observables

`separator-loss-is-selective.md` proposes that separators were lost, merging adjacent
words. Merging prose at the rate that matches the body's mean word length:

| merge p | mean length | 2-rune share | excess per pair |
|---|---|---|---|
| 0.00 | 4.03 | 0.228 | 0.0337 |
| **0.08** | **4.38** | 0.209 | 0.0237 |
| 0.16 | 4.81 | 0.191 | 0.0201 |
| **body** | **4.42** | **0.159** | **0.0039** |

Random merging fails on both axes at once. But the version that could work is merging
only SHORT words, because that removes exactly the short-long alternation the structure
is made of. Swept over the merge probability q:

| rule | mean | 2-rune share | excess per pair |
|---|---|---|---|
| prose untouched | 4.11 | 0.227 | 0.0341 |
| **merge length ≤ 2, q = 0.3** | **4.43** | **0.164** | 0.0199 |
| merge length ≤ 2, q = 0.5 | 4.66 | 0.121 | 0.0115 |
| merge length ≤ 2, q = 0.7 | 4.89 | 0.071 | 0.0062 |
| merge length ≤ 2, q = 0.9 | 5.12 | 0.024 | 0.0043 |
| merge length ≤ 3, q = 0.5 | 5.16 | 0.117 | 0.0074 |
| **body** | **4.42** | **0.159** | **0.0039 ± 0.0025** |

**The two observables demand different rules.** At q = 0.3 the histogram matches almost
exactly — mean 4.43 against 4.42, 2-rune share 0.164 against 0.159 — and the sequence
still carries 0.0199 where the body has 0.0039, a gap of **5.7σ**. Reaching the body's
sequence needs q = 0.9, which drops the 2-rune share to 0.024 and the mean to 5.12.

No rule in the family fits both. This is the quantitative version of the refutation:
the length histogram and the length order cannot be produced by one merge process.

## But the blocks are not memoryless either

A block process that starts a new block with fixed probability per rune would give
**geometric** lengths. The body's are not geometric, and not by a little: G² per word
against a matched-mean geometric is 0.4110 for the body, against 0.4144 for the LP's own
plaintext and 0.4356 for prose. **The body is exactly as far from memoryless as language
is** — mode at 3, near-absent at 1.

So whatever placed these boundaries produced a language-shaped histogram in a random
order. The histograms do still differ from language, and the two references show how much
of that is register:

| G² per word | |
|---|---|
| body vs LP plaintext | 0.0668 |
| body vs prose | 0.0656 |
| **LP plaintext vs prose** | **0.0173** |

The references agree with each other four times better than either agrees with the body.

## The hypothesis

If the separators were placed by a process independent of the plaintext's words, the
resulting lengths would be serially independent and the transition structure would be
zero — which is what the body shows. So:

> **The body's separators delimit cipher blocks, not plaintext words.**

This is not in tension with the word-anchored results; it explains them. It predicts,
and is consistent with:

- **Word-anchored key state.** The blocks *are* the key's unit, so a base change at each
  separator is exactly right. The measured 1.01× leak across boundaries follows.
- **The within-block d5 echo.** The letter phase is scoped to the block because the block
  is the cipher's unit.
- **The 2-rune deficit at z = −10.** Block lengths follow the cipher's rule, not English
  word statistics, so there is no reason for them to match a plaintext length histogram.
- **The mean length gap**, 4.42 against the plaintext's 4.04, for the same reason.
- **Why the front matter differs.** There the separators *are* words — those pages are
  plaintext or monoalphabetic, and their boundaries have to be readable.

## What would falsify it

1. **Block lengths should be i.i.d.** Measured: excess per pair 0.0039 ± 0.0025,
   consistent with zero. Any serial dependence found at higher order kills it.
2. **~~The length distribution should be the cipher's, not language's.~~** Tested and
   **failed**: the histogram is as far from geometric as language is. A memoryless block
   process is out. Two readings survive and are the live ones:
   - **an i.i.d.-length source** — a list rather than prose, whose word lengths carry no
     order because there is no sentence order to carry;
   - **block-level reordering** — the lengths are the plaintext's, permuted, which
     preserves the histogram exactly and destroys the order exactly. This one predicts
     the residual histogram gap above comes from the merge step, and pairs naturally with
     the q = 0.3 merge that fits it.

   Both are testable against rune-level statistics that survive reordering.
3. **The plaintext word boundaries are then absent from the text entirely**, so a
   correct decryption would produce unbroken runeglish. Any solution that recovers
   space-delimited words at these separators refutes this outright.
4. **Register.** The prose reference is novels and the LP reference is didactic front
   matter. A register whose word lengths are genuinely serially independent would
   explain the measurement without any of this — but no natural language register is,
   and the two references here bracket the question from both sides.

## Status

**Status**: plausible, and consequential if true. The measurement is confirmed at 3σ
against two independent references; the interpretation is one hypothesis among others.
`experiments/word_length_sequence.py`, `--merge` for the merge control.

## Related

- `separator-loss-is-selective.md` — the merge explanation this refutes.
- `two-rune-deficit.md` — the anomaly this would explain.
- `length-clocked-walk.md`, `pure-quagmire-word-restart.md` — models that take the
  separator as the key's unit, which this supports while renaming what it delimits.
- `lp-plaintext-register.md` — the register-matched reference.
