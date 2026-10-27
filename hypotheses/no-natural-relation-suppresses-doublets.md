---
type: observation
---
# Observation: No Natural Relation, Autokey or Machine Suppresses Doublets on the Author's Plaintext

## Feature

`doublet-suppression-requires-design.md` proves that for a cipher that is a bijection at
every position a doublet is `p_j = R(p_{j+1})` for one relation `R`, so the doublet rate
is the plaintext bigram mass on `R`'s graph. The question "which classical cipher makes
the suppression fall out naturally" is therefore a finite computation: evaluate that mass
on the author's own plaintext for every relation a designer would reach for without
tuning, and simulate the machines that have no fixed `R`.

`experiments/natural_relations_doublet_rate.py`, on the register of
`lp_plaintext_register.corpus` (723 words, 2,882 runes, 2,159 within-word pairs).
Chance is 0.0345; the body reads 0.0063 inside words and 0.0079 at seams.

## Measurement

| relation `R` (doublet iff `p_j = R(p_{j+1})`) | rate | note |
|---|---|---|
| identity (the plaintext as written) | 0.0236 | the author's text has few doubles already |
| shift by s, best of 28 | 0.0125 | s = 11; Trithemius (s = 1) 0.0389 |
| multiply by r in GF(29), best of 27 | 0.0116 | r = 11 |
| power map b ↦ bᵏ on GF(29)*, best of 11 | 0.0083 | k = 27, the inverse map, order 2 |
| **affine a·b + s, best of 811** | **0.0079** | a = 2, s = 4; median affine 0.0329 |
| atbash | 0.0255 | |
| 5×5 square step, Futhark fill, row-major / column-major | 0.0333 / 0.0250 | the other direction 0.074 / 0.067 |
| 5×5 square step, frequency fill | 0.0459 | |
| 5×5 square step, used runes in Futhark order, unused four outside | 0.0259 | |
| random 5×5 square, median of 4,000 | 0.0245 | **0.53%** of fills reach the body |
| random permutation, median of 20,000 | 0.0329 | **0.27%** reach the body; minimum 0.0005 |

Autokeys are triple conditions rather than relations:

| cipher | doublet condition | rate |
|---|---|---|
| Vigenère plaintext autokey | p_{j+1} = p_{j−1} | 0.0389 |
| Beaufort plaintext autokey | p_{j+1} = 2p_j − p_{j−1} | 0.0423 |
| second-order autokey | p_{j+1} = p_{j−2} | 0.0507 |
| ciphertext autokey | p_{j+1} = the identity element | F 0.0149; EO 0.0000 |

Machines with no fixed `R`, run on the register's words with their order shuffled:

| machine | doublets | seam | nIoC | within-word lags 1..6 (× chance) |
|---|---|---|---|---|
| Chaocipher-29, Futhark alphabets | 0.0353 | 0.0407 | 1.000 | 0.97 1.01 1.15 0.80 1.20 0.72 |
| Chaocipher-29, random alphabets | 0.0368 | 0.0369 | 0.999 | 1.07 0.96 1.01 0.96 0.83 0.95 |
| move-to-front list | 0.0646 | 0.0437 | 1.356 | all above 1.5 |
| transpose-forward list | 0.0491 | 0.0502 | 1.642 | all above 1.2 |

## Significance

- **Two natural relations reach the body's rate: GF(29) affine maps and power maps.**
  The directory's "the relation cannot be arithmetic" (`sigma_algebraic_floor.py`,
  which reproduces an affine floor of about 0.0125 for `g`) was computed on prose
  tables; on the author's own register the best affine map sits at 0.0079 on 17 hits,
  within 1σ of the body. What excludes them is not the rate but the order: every
  element of AGL(1,29) has order in {1, 2, 4, 7, 14, 28, 29}, and the within-word lag
  profile needs g⁵ = id (`d-profile-pins-g-to-five-cycles.md`). GF(29²)* has order
  840 and so does contain order-5 elements, but only as maps on rune pairs.
- **Every other natural relation is 2× to 7× too high**, and arranged alphabets or
  squares that reach the rate are 0.3% to 0.5% of random ones. In the bijective class
  "natural" can only mean a one-time design choice, never a rule.
- **Autokeys make it worse**, because they turn doublets into plaintext repeats at lag 2
  or 3, which English has more of than chance.
- **Self-mutating machines sit at chance** and show no lag-5 echo; the self-organizing
  lists are not even flat. Chaocipher's doublet condition is "the next plaintext letter
  is the successor of the last in the mutating right alphabet", a relation that averages
  to chance.
- **Non-bijective readings.** Homophones on the spare runes reach φ ≤ 0.42 with five
  spares and ≤ 0.70 with ten, against the body's φ ≈ 0.90. Alternative digraph spellings
  reach φ ≤ 0.10. The author's own key-skip is plaintext-triggered and blind to the
  output. That leaves the dodge (`quagmire-dodge.md`, `doublet-dodge-walk.md`) and one
  reading this directory did not have: a plaintext **null** inserted when the next rune
  would repeat, `null-rune-preventer.md`.

## A proposal made and withdrawn in the same review

The letter step `g` has five 5-cycles and four fixed runes (C-0), and the author's register
has exactly four runes with three or fewer occurrences: J, EO, OE, AE. That invites a
5×5 square of the 25 used runes with the four outside, `g` a translation on Z₅², and the
per-word step an affine map of the square, so the base chain would live in AGL(2,5)
(12,000 elements; ASL(2,5) has 3,000, near the pool the ledger reads). It fails twice on
evidence already recorded:

- a base family that never mixes the outside four leaves their ciphertext mass equal to
  their plaintext mass. The body carries 0.0347, 0.0308, 0.0380 and 0.0343 on J, EO, OE
  and AE; the register carries 0.0017 on all four together;
- if the outside four are used runes instead, they form a block, and
  `no-block-partition.md` enumerates every 4-set at 75% power with a body maximum of
  1.023× its best disjoint rival against 1.11× to 2.9× for planted blocks.

So the compact chain is excluded, and the coincidence of four fixed points with four
unused runes, while real, is untestable: the base relabels runes, and a `g` that fixes
letters the plaintext never uses leaves no trace.

## Scripts

- `experiments/natural_relations_doublet_rate.py` — every number above.
- `experiments/sigma_algebraic_floor.py` — the prose-table floors this re-measures.

## Related

- `doublet-suppression-requires-design.md` — the theorem this computes against.
- `null-rune-preventer.md` — the one non-bijective reading left open.
- `no-block-partition.md`, `rotor-machine-compact-state.md` — why the affine square dies.
- `docs/new-directions.md` — where this sits among the directions.
