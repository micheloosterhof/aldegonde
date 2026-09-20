---
type: hypothesis
---
# Hypothesis: Dual Autokey — Lag-1 Ciphertext plus Lag-5 Plaintext

## Claim

```
c_j = α·p_j + β·c_{j−1} + γ·p_{j−5}   (mod 29)
```

Michel's proposal (August 2026). Two feedback taps at once: a lag-1 **ciphertext**
autokey and a lag-5 **plaintext** autokey. It was first recorded here as reproducing the doublet suppression and the
boundary-blindness *from structure alone*. **That was wrong.** Over 200 random
rune→value labellings the mechanism gives d1 = 3.41% ± 0.76 — chance. The 2.28%
originally reported came from the rune-index labelling, sitting at z = −1.48: one
arbitrary choice's fluctuation, reported as a property of the mechanism.

The suppression in every variant of this family comes from **tuning the labelling**,
and a labelling is a 29-permutation. So this does not escape
`doublet-suppression-requires-design.md`; that note's conclusion stands.

## Status

**Status**: closed as a mechanism for this corpus, on the lag theorem alone
(September 2026).

Two supporting objections recorded in August are retracted. The 0.86% doublet floor
was an artifact of the linear parametrisation, and a constant delimiter step — which
is not a reset — holds the within-word rate and the seam at their observed values
together. What closes the family is that d4, d5 and d6 stay at chance under every
setting: linear feedback lets at most one distance carry a clean relation, and the LP
needs four. See "Two of the three objections fall" below.

Also retracted from the original "live partial" reading: the doublet suppression is
not structural. Over 200 random rune-to-value labellings the linear mechanism gives
d1 = 3.41% ± 0.76, which is chance; the 2.28% first reported was one labelling's
fluctuation at z = −1.48.

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

What survives, and it is narrower: the family needs **one** tuned permutation (the
labelling, ~104 bits) where the walk needs **two** (`g` and σ, ~178 bits). If it fit,
it would be the simpler key. It does not fit — see the held-out test below.

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

## Held-out test — the fitted match is not evidence

Fitting the labelling against four targets (d1, seam, d5, grouped IoC) reaches them
almost exactly. That is expected and means nothing: ~104 bits of freedom against four
scalars. The test is what happens on distances NOT in the objective:

| | fitted? | model | LP | diff |
|---|---|---|---|---|
| d1 | yes | 0.65 | 0.63 | +0.02 |
| d5 | yes | 4.92 | 4.92 | 0.00 |
| seam | yes | 0.55 | 0.79 | −0.24 |
| grouped IoC | yes | 1.104 | 1.026 | +0.078 |
| **d2** | **no** | 3.10 | 3.47 | −0.38 |
| **d3** | **no** | 3.47 | 3.70 | −0.23 |
| **d4** | **no** | 3.28 | 4.10 | **−0.81** |
| **d6** | **no** | 3.24 | 2.45 | **+0.79** |

The model returns ~chance at every held-out distance while the LP carries real
structure — d4 high, d6 low. Errors of 1–2σ each. So the mechanism reproduces what it
is fitted to and nothing else.

## The lag structure is the obstruction, and it is a theorem

(August 2026, `experiments/autokey_lag_family.py`.) The held-out failure above is
not a tuning shortfall. Writing `D_j = c_j - c_{j-1}`, lag-1 feedback makes `D_j` a
function of the plaintext taps alone, so for any distance

    c_j - c_{j-d} = D_{j-d+1} + ... + D_j        (d consecutive terms)

At d = 1 that is ONE plaintext term — structured, and tunable to any rate at all.
At d >= 2 it is a sum of two or more near-independent values mod 29, and summing
mod 29 convolves toward uniform. **Every cell past d1 is pinned at chance by the
architecture.**

Sweeping the family `c_j = v(p_j) + a1·c_{j-1} + a5·c_{j-5} + b1·v(p_{j-1}) +
b5·v(p_{j-5})` over 48 random labellings each gives the reachable ranges:

| feedback | d1 reachable | d5 reachable |
|---|---|---|
| `c(n-1)` alone | **[0.001, 0.105]** — brackets 0.0063 | 0.0347 (chance) |
| `c(n-5)` alone | 0.0346 (chance) | **[0.000, 0.134]** — brackets 0.0492 |
| **both** | 0.0346 (chance) | 0.0344 (chance) |

Each feedback lag alone gives exactly one clean relation, `c_j - c_{j-k} = v(p_j)`,
firing when `p_j` is the letter labelled 0 — so that cell equals one letter's
frequency and tunes anywhere. **Adding the second feedback destroys both**, because
`c_j - c_{j-1}` then contains `c_{j-5}` and vice versa.

So: with linear feedback, **at most one distance can carry a clean plaintext
relation — the one equal to the single feedback lag.** The LP needs four cells off
chance (d1 0.0063, d4 0.0410, d5 0.0492, d6 0.0245). No member of the family fits,
and no labelling can rescue one. Coefficients in Z/29* do not help: any `alpha` on
`c_{j-5}` still leaves `c_j - c_{j-1}` ciphertext-dependent.

The walk delivers all four with one object. Distances 1 and 6 differ by 5, so an
order-5 `g` suppresses both with the SAME relation on two different tables, and d4
is `g^4`, d5 is `g^0`. That coupling is the LP's signature and the autokey family
has no analogue for it.

What remains useful is the negative — mixed feedback was the last candidate in
`doublet-suppression-requires-design.md` that looked like it might escape the
designed-permutation conclusion, and it does not.

## Two of the three objections fall; the third is the whole story (September 2026)

Michel returned to this family with the suggestion of "extra word delimiter action".
`experiments/dual_autokey_delimiter.py` tests it. Two of the objections below were
artifacts of how the family was parametrised, and the closure now rests on one thing.

**1. The 0.86% doublet floor does not apply to the family, only to its linear form.**
The floor was computed for `c_j = α·p_j + c_{j−1} + γ·p_{j−5}` under a rune-to-value
labelling `v`, where the induced plaintext relation is `π = v⁻¹∘(×λ)∘v`, conjugate to
multiplication, so its cycle type is fixed by ord(λ) | 28. Written with arbitrary
permutation taps,

    c_j = a(p_j) + c_{j−1} + b(p_{j−5})   (mod 29)

the doublet condition is `a(p_j) + b(p_{j−5}) = 0`, i.e. `p_j = π(p_{j−5})` with
`π = a⁻¹(−b(·))` an ARBITRARY permutation. The assignment-problem optimum on the
plaintext distance-5 table reaches **0.0051**, below the LP's 0.0063. The floor
argument is retracted; it constrained the parametrisation, not the mechanism.

**2. A delimiter step is not a reset, and it fixes the seam.** "Every reset that
would word-anchor the echo also randomises the seam" is confirmed: a per-word reset
measures a seam of 0.0348 against chance 0.0345. But a separator that ADVANCES the
state by a constant δ is not a reset. The state still cancels, so the seam condition
stays a single plaintext term, `a(p_first) + b(tap) + δ = 0`. Because the seam reads
a different plaintext table from the within-word rate, δ is a free knob on one and
not the other. Over its 29 values the seam runs from 0.0475 down to **0.0106** while
the within-word rate stays fixed at 0.0045. Tuned together the pair reaches
**d1 = 0.0051, seam = 0.0072** against the LP's 0.0063 and 0.0079.

That answers a question this file left open — it is the first mechanism here to hold
the within-word and seam rates at their observed values at once, and it does so with
one permutation and one constant rather than the walk's two permutations.

**3. The period-5 cells are absent, at every setting.** Sweeping π from the tuned
assignment to the identity, under both tap clocks (stream and per-word) and all 29
delimiter values:

| π fixed points | d1 | seam | d2 | d4 | d5 | d6 |
|---|---|---|---|---|---|---|
| 0 (tuned) | 0.0051 | 0.0072 | 0.0355 | 0.0367 | 0.0329 | 0.0343 |
| 10 | 0.0600 | 0.0210 | 0.0361 | 0.0348 | 0.0352 | 0.0334 |
| 29 (identity) | 0.0650 | 0.0222 | 0.0371 | 0.0317 | 0.0320 | 0.0353 |
| **LP** | **0.0063** | **0.0079** | 0.0347 | **0.0410** | **0.0492** | **0.0245** |

d4, d5 and d6 sit at chance everywhere. Note the identity end does not produce an
echo either, which corrects a natural guess: `π = id` makes the DOUBLET condition
"the plaintext repeats at distance 5" (hence d1 = 0.065, the plaintext rate), but the
distance-5 CIPHERTEXT relation is still a sum of ten plaintext terms.

So the closure stands for exactly the reason the lag theorem gives: with lag-1
feedback `c_j − c_{j−d}` is a sum of d plaintext terms, and a sum of two or more mod
29 convolves to uniform. Permutation taps and a delimiter step do not touch that,
because the combination is still addition. **The family now reproduces every cell of
the LP profile except the three that carry the period-5 structure.**

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

## The per-word reset does not rescue it — and why is the general lesson

The obvious repair is to reset the recursion per word: the LP's d5 echo is
word-anchored (within-word 4.92%, cross-word 1.01), so something must reset. Michel
asked the right question about it — *then how do we get low doublets between the
resets?* Measured:

| variant | d1 within | d1 seam | d5 within |
|---|---|---|---|
| LP target | 0.63 | **0.79** | 4.92 |
| continuous | 2.28 | **1.91** | 2.99 |
| ciphertext tap resets per word | 2.28 | **3.18** | 2.99 |
| plaintext tap resets per word | 2.11 | **3.83** | 3.14 |
| continuous + per-word offset | 3.58 | 3.21 | 3.14 |

**Every reset that would word-anchor the echo also randomises the seam.** The reason
is structural: the suppression is carried by the ACCUMULATED STATE — the doublet
condition reduces to a plaintext relation only because the state cancels between
adjacent positions. A reset breaks that cancellation, so the seam condition involves
the fresh state, which is flat, and the rate reverts to chance. A per-word additive
offset is worse: it destroys the within-word suppression as well.

So the corpus demands two opposite scopes — a word-anchored d5 echo and a
boundary-blind suppression — and in this family a single accumulated state cannot
supply both.

**That is exactly why the walk carries two objects.** It buys the seam suppression
with a SECOND tuned permutation, σ, whose diagonal is designed separately from `g`'s.
It also explains an observation from `key-local-channel-is-empty.md` §5: σ has no
local footprint beyond the seam rate because the seam diagonal is the whole of its
observable job.

## Predictions, if it can be rescued

- Any rescue must keep β = 1 (else no suppression at all).
- It must carry the suppression in something that survives a per-word reset, or
  supply the echo without one. A single accumulated state does neither.
- ord(λ) | 28 means λ cannot supply the period-5 itself; that has to come from
  elsewhere in the design.
- A recurrence search over plaintext taps at lags 1–6 and ciphertext taps at lags
  1, 2, 5 (coefficients in {0, ±1}, ≤4 terms) found nothing better: the closest was
  `c_j = p + p[-3] + c[-1]` at d1 = 2.13%, d5 = 4.05%, still 3× short on depth.

## Scripts

- `experiments/dual_autokey.py` — the simulation, the grouped-IoC comparison and the
  floor computation (whose floor the September 2026 section retracts).
- `experiments/dual_autokey_delimiter.py` — permutation taps, the delimiter step, and
  the profile sweep; self-tests round-trip decryption and the seam behaviour.

## Related

- `ciphertext-autokey.md`, `plaintext-autokey.md` — the single-tap forms, both
  disproved; this is not covered by either disproof.
- `doublet-suppression-requires-design.md` — the exclusion table this corrects.
- `d5-partial-alphabet-leak.md` — the echo this fails to produce.

## Verdict

Closed. The September 2026 section supersedes the reading below: the family reaches
the within-word doublet rate and the seam rate together, so it is not short on depth
and not dependent on a designed labelling in the way first recorded, but it produces
no period-5 structure at any setting and that is decisive.

The August reading, kept for the record:

The best non-permutation candidate produced so far, and the only one that gets the
doublet suppression and the boundary-blindness without designing an alphabet
relation. It is short by 1.4× on depth and silent on the d5 echo. Recorded as a live
partial rather than a refuted mechanism, because the failure mode is specific and
points at a concrete repair.

A caution against over-reading it: reproducing four signatures is easier than it
looks, since IoC, grouped IoC and delta IoC all measure flatness and any well-mixed
construction gets them together. The load-bearing successes are the doublet
suppression from structure and the free boundary-blindness — two, not four.
