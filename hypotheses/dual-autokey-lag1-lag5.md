---
type: hypothesis
---
# Hypothesis: Dual Autokey — Lag-1 Ciphertext plus Lag-5 Plaintext

## Claim

```
c_j = α·p_j + β·c_{j−1} + γ·p_{j−5}   (mod 29)
```

Michel's proposal (August 2026). Two feedback taps at once: a lag-1 **ciphertext**
autokey and a lag-5 **plaintext** autokey. It is the first non-permutation mechanism
to reproduce the doublet suppression *and* the boundary-blindness from structure
alone, with no tuned alphabet relation anywhere.

## Status

**Status**: partial — reproduces four of six signatures; falls ~1.4× short on the
doublet depth against the reference available, and does not produce the d5 echo

## Why it is not covered by the existing autokey disproofs

`ciphertext-autokey.md` is disproved because grouping runes by the previous
ciphertext rune would make each group monoalphabetic, so grouped IoC must rise to
~1.78. Measured within words it is 1.0227.

The dual form escapes that. Grouping fixes `c_{j−1}`, leaving
`c_j = α·p_j + γ·p_{j−5} + const` — a **convolution of two plaintext letters**, far
flatter than plaintext. The signature that kills pure ciphertext autokey never
appears:

| | IoC | **grouped IoC** |
|---|---|---|
| LP | 1.000 | **1.026** |
| pure ciphertext autokey | 1.000 | **1.756** ✗ |
| dual autokey | 1.000 | **1.046** ✓ |

`doublet-suppression-requires-design.md` listed "feedback" as excluded on the
strength of that test. That row covered *ciphertext* feedback only and has been
corrected.

## Mechanism

**β = 1 is forced.** The doublet condition is
`c_j(1−β) = α·p_{j+1} + γ·p_{j−4}`. If β ≠ 1 the left side is a flat ciphertext
value and the condition holds at chance. With β = 1 it collapses to a pure plaintext
relation at distance 5:

```
p_{j+1} = λ · p_{j−4}      λ = −γ/α
```

so the doublet rate is the λ-diagonal of the distance-5 plaintext table. Note this
is a **plaintext** condition — no key material in it — which is why the suppression
costs nothing to design.

Decryption is sequential and needs no inversion trouble: `p_j = α⁻¹(c_j − c_{j−1} −
γ·p_{j−5})`, with `p_{j−5}` already recovered. 29 is prime, so every α ≠ 0 is
invertible.

## Measured (real runeglish prose, LP-matched word lengths)

| signature | LP | dual autokey | |
|---|---|---|---|
| IoC | 1.000 | 1.000 | ✓ |
| grouped IoC | 1.026 | 1.046 | ✓ |
| delta IoC | 1.024 | 1.046 | ✓ |
| seam d1 vs within d1 | 0.79 / 0.63 | 1.91 / 2.28 | ✓ boundary-blind for free |
| within-word d1 | **0.63%** | **2.28%** | short |
| within-word d5 | **4.92%** | **2.99%** | ✗ no echo |

## Evidence against / open

**The doublet floor.** With a bijective value map `v`, the relation
`π = v⁻¹∘(×λ)∘v` is conjugate to multiplication by λ, so its cycle type is fixed by
ord(λ) — and ord(λ) divides 28, so **5 never appears**. Multiplication fixes 0, so π
always carries a fixed point contributing that rune's plaintext distance-5
self-coincidence. Hillclimbing the assignment per order:

| ord(λ) | 1 | 2 | 4 | 7 | 14 | 28 |
|---|---|---|---|---|---|---|
| min diagonal | 6.030% | 0.911% | 0.896% | 0.950% | 0.880% | **0.857%** |

The family floors near **0.86%** against an observed 0.63% — about 1.4× short. Two
caveats keep this from being a refutation: the floor is hillclimbed rather than
proven, and it rests on a Pride & Prejudice distance-5 table, so register uncertainty
could move it by more than 1.4×.

**The d5 echo is the real failure, and the reason is instructive.** The lag-5
*plaintext* term alone produces an echo (5.93% against a 4.92% target). The lag-1
*ciphertext* term alone produces the doublet suppression. Combined, the ciphertext
recursion makes `c_j` depend on the entire prefix, destroying the clean distance-5
relation and washing the echo out to 2.99%. **The two features this cipher needs pull
against each other**, and something else must carry the period-5 that the feedback
does not reach through — a per-word reset, or a period-5 component the recursion does
not touch.

## Predictions, if it can be rescued

- Any rescue must keep β = 1 (else no suppression at all).
- It must restore a distance-5 relation the ciphertext recursion cannot destroy —
  e.g. resetting the recursion per word, which is testable directly.
- ord(λ) | 28 means λ cannot supply the period-5 itself; that has to come from
  elsewhere in the design.

## Scripts

- `experiments/dual_autokey.py` — the simulation, the grouped-IoC comparison and the
  floor computation.

## Related

- `ciphertext-autokey.md`, `plaintext-autokey.md` — the single-tap forms, both
  disproved; this is not covered by either disproof.
- `doublet-suppression-requires-design.md` — the exclusion table this corrects.
- `d5-partial-alphabet-leak.md` — the echo this fails to produce.

## Verdict

The best non-permutation candidate produced so far, and the only one that gets the
doublet suppression and the boundary-blindness without designing an alphabet
relation. It is short by 1.4× on depth and silent on the d5 echo. Recorded as a live
partial rather than a refuted mechanism, because the failure mode is specific and
points at a concrete repair.

A caution against over-reading it: reproducing four signatures is easier than it
looks, since IoC, grouped IoC and delta IoC all measure flatness and any well-mixed
construction gets them together. The load-bearing successes are the doublet
suppression from structure and the free boundary-blindness — two, not four.
