---
type: observation
---
# Observation: A Zoo of Encryption Algorithms Scored on the Body's Fingerprint

## Feature

Eighteen algorithms, each enciphering the author's own plaintext (the register, words
cycled with their order shuffled, 2,928 words), scored on the cells the body is measured
on. `experiments/cipher_zoo_fingerprint.py`, six key draws per algorithm, averaged.
Columns: nIoC; doublet rate inside words (d1w) and at seams; triplets; within-word
coincidence at lags 2–6 as multiples of chance; lag-5 coincidence across one separator
(d5x); the largest |z| of kappa at skips 2–40; identical 3+-rune words; adjacent
identical pairs.

| algorithm | nIoC | d1w | seam | trip | d2 | d3 | d4 | d5 | d6 | d5x | kmax | ident | ret |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Liber Primus body | 1.000 | 0.0063 | 0.0079 | 0 | 1.01 | 1.07 | 1.19 | 1.43 | 0.71 | 0.95 | 2.9 | 17 | 1 |
| plaintext (register, order shuffled) | 1.785 | 0.0234 | 0.0417 | 3 | 1.14 | 1.47 | 1.70 | 2.12 | 1.68 | 1.66 | 18.9 | 22576 | 297 |
| walk: rare order-5 g, σ chain, none | 1.007 | 0.0027 | 0.0342 | 0 | 0.99 | 0.90 | 0.93 | 2.12 | 1.12 | 1.02 | 4.7 | 18 | 0 |
| walk: rare order-5 g, σ chain, dodge | 1.007 | 0.0007 | 0.0064 | 0 | 1.00 | 0.90 | 0.94 | 2.13 | 1.17 | 1.02 | 4.8 | 17 | 0 |
| walk: rare order-5 g, σ chain, hold | 1.007 | 0.0007 | 0.0066 | 0 | 0.99 | 0.91 | 0.93 | 2.12 | 1.17 | 1.00 | 4.6 | 17 | 0 |
| walk: rare order-5 g, σ chain, null | 1.007 | 0.0002 | 0.0000 | 0 | 1.01 | 0.91 | 0.94 | 2.06 | 1.22 | 1.04 | 4.6 | 18 | 0 |
| walk: untuned g, σ chain, dodge | 1.002 | 0.0012 | 0.0058 | 0 | 0.84 | 0.97 | 1.39 | 1.79 | 1.00 | 0.92 | 3.7 | 15 | 0 |
| quagmire: 5-letter keyword with a doubled letter, | two | dials, | dodge | 0.999 | 0.0051 | 0.0089 | 0 | 0.77 | 1.24 | 0.97 | 1.82 | 1.08 | 0.88 | 3.5 | 15 | 0 |
| quagmire: 5-letter keyword, distinct letters, two | dials, | dodge | 1.000 | 0.0000 | 0.0000 | 0 | 1.10 | 1.08 | 0.84 | 1.99 | 0.88 | 0.94 | 4.1 | 16 | 0 |
| quagmire: 5-shift schedule with a zero, two dials, | none | 1.000 | 0.0229 | 0.0322 | 4 | 0.89 | 0.71 | 0.84 | 2.12 | 1.04 | 0.91 | 3.9 | 15 | 0 |
| quagmire: 5-shift schedule with a zero, two dials, | dodge | 1.000 | 0.0046 | 0.0035 | 0 | 0.81 | 0.61 | 0.99 | 2.10 | 1.06 | 0.88 | 2.8 | 15 | 0 |
| quagmire: 5-shift schedule with a zero, two dials, | hold | 1.000 | 0.0038 | 0.0080 | 1 | 0.80 | 0.75 | 1.04 | 1.91 | 1.29 | 0.96 | 2.8 | 11 | 0 |
| quagmire: 5-shift schedule with a zero, two dials, | null | 1.000 | 0.0009 | 0.0000 | 0 | 0.99 | 0.61 | 0.87 | 2.00 | 1.10 | 0.92 | 2.9 | 16 | 0 |
| five mixed rows by phase, two dials, dodge | 1.000 | 0.0014 | 0.0010 | 0 | 1.03 | 0.96 | 1.08 | 1.93 | 0.84 | 0.92 | 3.2 | 12 | 0 |
| five mixed rows by phase, two dials, hold | 1.000 | 0.0009 | 0.0012 | 0 | 1.05 | 1.00 | 0.96 | 1.96 | 0.92 | 0.91 | 2.9 | 15 | 0 |
| five mixed rows by phase, two dials, null | 1.000 | 0.0017 | 0.0000 | 0 | 1.05 | 0.97 | 0.98 | 1.88 | 0.93 | 0.85 | 3.2 | 11 | 0 |
| quagmire, dial 1 = plaintext sum so far, dodge | 0.999 | 0.0046 | 0.0071 | 0 | 0.85 | 0.76 | 0.96 | 2.09 | 0.94 | 0.99 | 3.2 | 17 | 0 |
| three rotors stepping per letter, dodge | 1.000 | 0.0006 | 0.0010 | 0 | 1.13 | 0.89 | 1.00 | 0.99 | 1.04 | 0.97 | 2.9 | 8 | 0 |
| quagmire, progressive shift +3 per letter, dodge | 1.000 | 0.0000 | 0.0000 | 0 | 1.09 | 0.66 | 1.01 | 3.32 | 0.65 | 0.96 | 6.8 | 38 | 0 |
| per-word alphabet only, no letter clock, dodge | 1.000 | 0.0234 | 0.0380 | 7 | 1.14 | 1.47 | 1.70 | 2.12 | 1.68 | 0.91 | 5.7 | 29 | 0 |

`ident` is not comparable with the body's 17: the cycled plaintext repeats every word
four times, so the column reads the pool of alphabets.

## What the table shows

**The three parts are each visible in one cell.**

- The *letter clock* owns d5. Every machine with a period-5 clock (walk, Quagmire
  schedule, five rows) reads d5 at 1.8–2.1, the plaintext's own lag-5 coincidence
  passed through; the rotors (d5 0.99) and the Trithemius progression (d5 3.32 and
  kmax 6.8, a fixed shift difference on the lag-5 table plus periodicity) do not. The
  body's 1.43 is below full pass-through: either the plaintext's lag-5 coincidence is
  lower than the register's 2.12 (prose reads about 1.6) or the preventer's drift breaks
  more lag-5 pairs than it does here.
- The *word chain* owns nIoC, kmax and the pool. Two dials with carry, the σ product
  and a plaintext-sum accumulator are indistinguishable in every cell: the chain's
  identity is invisible to the fingerprint, as `the-chain-shows-only-in-extension.md`
  says.
- The *preventer* owns d1w and seam, and here the table is decisive. Every preventer
  that always acts lands far below the body: the rare-g walk with a dodge 0.0007, with
  a hold 0.0007, with a null 0.0002; five rows 0.0009–0.0017; a keyword of five distinct
  letters **0.0000**. The body's 0.0063 and 0.0079 are reached only when the preventer
  **fails about one time in five**: a Quagmire whose 5-letter keyword has a doubled
  letter reads 0.0051 / 0.0089, the zero-increment schedule 0.0046 / 0.0035 (dodge) or
  0.0038 / 0.0080 (hold).

**The doubled letter is the keyword form of the recorded zero offset.** `quagmire-dodge.md`
already states the mechanism: the dodge fails exactly when `s_(k+1) = 0`, "two identical
adjacent alphabets", a property of the schedule. In a Quagmire the shifts are the
keyword's letters, so a zero step is a doubled adjacent letter in a 5-rune keyword; the
zoo adds the wording and the numbers, not the mechanism. With one such pair the preventer
fails one time in five and the rate is chance over five, which `stream-cipher-no-repeat.md`
recorded as P = (1/5)(1/29).

**Tuning and the preventer are alternatives on these two cells.** The walk with a
rare-diagonal `g` and no preventer reads 0.0027 inside words and 0.034 at seams here;
with `g` and σ fitted to the body's two rates, as `length-clocked-walk.md` does, it
reads 0.0063 and 0.0079 by construction. An untuned relation with a preventer failing one
time in five reads the same. The doublet cells cannot separate the two; what cannot be
had is a tuned relation **and** an always-acting preventer, which overshoots by an order
of magnitude. The case for the preventer over the tuned relation rests on other rows
(D3, D5, D9, D11 of `what-any-solution-must-satisfy.md`), not on this table.

**d6 misses everywhere.** The body reads 0.71 on 1,267 pairs; every algorithm reads
0.85–1.3. `distance-6-has-no-power.md` puts the body's figure at z −1.95, so this is a
2σ cell, but no construction here produces it.

**Two columns need a caveat.** `kmax` is inflated by the plaintext: the cycled register
reads 3.3–4.0 even with independent random bases per word, against the body's 2.9, so
only differences between rows mean anything there. And the walk rows read nIoC
1.006–1.007 where every other carrier reads 1.000; that is the chain, not the tuned g
(`experiments/walk_chain_traps.py`). The preimage of a ciphertext rune follows a
deterministic orbit `x_(w+1) = σ⁻¹ g^-(L-1) x_w`; when σ fixes a point g also fixes, the
orbit can stop and one rune carries one plaintext letter. Over 300 random keys, 16%
share such a point and read nIoC 1.025 with rune counts from 8 to 1,035; the rest read
1.0010 ± 0.0120 with outliers to 1,057, against 1.0002 ± 0.0006 for independent bases.
The body's counts run 399–492, so under the walk the key must keep g's fixed points off
σ's short cycles; the directory's fitted key reads kappa_max_z 4.1 against the body's
2.9 (`fingerprint_battery.py`), which is the same trace seen from the other side.

## What this adds to the directory

- A pluggable simulator for the three parts, which is the prototype of the library
  cipher `docs/new-directions.md` 3.4 asks for.
- The negative controls in one place: rotors stepping per letter (no echo), a
  progressive shift (periodic, no echo), one alphabet per word (the plaintext's whole
  lag profile passes through), and a keyword of distinct letters (no doublets at all).
- The keyword wording of the zero offset: a doubled adjacent letter in a 5-rune keyword.
- The chain trap: under the walk, σ may not fix a fixed point of g, or one rune carries
  one letter.

## Corrections after review, 2026-10-25

The first version of this file said tuning was "excluded by the rate" and presented the
doubled keyword letter as a new mechanism; both are withdrawn above. It also said every
row read nIoC 1.000; the walk rows did not, and the reason is now recorded.

## Scripts

- `experiments/cipher_zoo_fingerprint.py`
- `experiments/walk_chain_traps.py`

## Related

- `quagmire-dodge.md`, `quagmire-odometer.md`, `doublet-dodge-walk.md` — the carriers.
- `stream-cipher-no-repeat.md` — the (1/5)(1/29) fit.
- `no-natural-relation-suppresses-doublets.md` — why the relation alone cannot do it.
- `null-rune-preventer.md` — the null here reads 0.0002–0.0017 with zero seams, so a null
  that always acts is too strong; it would need the same one-in-five failure.
