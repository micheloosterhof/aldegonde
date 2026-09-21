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

## The obvious mechanism is refuted

`separator-loss-is-selective.md` proposes that separators were lost, merging adjacent
words. Merging prose at the rate that matches the body's mean word length:

| merge p | mean length | 2-rune share | excess per pair |
|---|---|---|---|
| 0.00 | 4.03 | 0.228 | 0.0337 |
| **0.08** | **4.38** | 0.209 | 0.0237 |
| 0.16 | 4.81 | 0.191 | 0.0201 |
| **body** | **4.42** | **0.159** | **0.0039** |

At the rate that reproduces the body's mean, merging leaves the 2-rune share at 0.209
against the body's 0.159, and two thirds of the transition structure survives. **Merging
cannot produce the body's profile.** Neither the 2-rune deficit nor the transition
collapse is a merge artifact.

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
2. **The length distribution should be the cipher's, not language's.** It should fit a
   simple generative rule — geometric, uniform on a range, or a keyed sequence — better
   than it fits a word-length histogram. Untested.
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
