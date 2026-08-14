---
type: observation
---
# Observation: No Pairwise Dependence Except Lag 1

## Feature

The full 29x29 contingency table of (C[i], C[i+d]) is at chance for every lag
d = 2..100; only d=1 (the doublet diagonal) shows dependence.

## Measurement

`experiments/obs_dependence.py` (clean corpus), chi-square vs independence,
784 df:

| lag | chi2 | z |
|-----|------|---|
| 1 | 1115 | **+7.4** (doublet diagonal) |
| 2 | 778 | -0.1 |
| 3-10 | 750-843 | \|z\| < 1.5 |
| 11-100 | — | worst \|z\| = 2.4 (lag 80), under the 100-lag Bonferroni bar ~3.3 |

## Significance

The ONLY pairwise structure at any distance is the lag-1 doublet diagonal. No
lag carries a hidden bigram dependency, which excludes lagged-feedback ciphers
whose relation would surface as off-diagonal contingency structure. (The lag-5
anomaly is NOT a pairwise-dependence effect -- it is a higher-order pairing of
coincidences, invisible to this test; see `lag5-digraph-structure.md`.)

## Second order (bigram → next rune): also flat, and it rejects 2-back autokeys

The table above is 2-variable (marginal at each lag). A cipher could pass it and
still carry **joint** 2nd-order structure — `c[i]` depending on the pair
`(c[i-1], c[i-2])` while being marginally independent of `c[i-2]` alone. Tested
directly (`experiments/obs_second_order.py`) and it is flat too:

| statistic | LP | exact-bigram null | z |
|---|---|---|---|
| conditional MI `I(next ; 2-back \| 1-back)` | 0.8751 | 0.877 ± 0.005 | **−0.48** |
| trigram IoC | 1.0407 | 1.053 ± 0.016 | −0.76 |
| doublet rate by 2-back rune | — | — | χ² = 23.9 / 28 df, flat |

So knowing two runes predicts the third no better than knowing one.

**Null choice is load-bearing (a fifth face of the doublet-suppression trap,
`bigram-ioc.md`).** A Markov *resample* null — draw a fresh stream from the
estimated bigram transition matrix — is WRONG: it smooths the sampling noise in
the transition matrix, lowers the null MI, and manufactures a spurious **+4.8σ**
for the LP (and a trigram IoC null of 1.19 vs the observed 1.04). The correct
null preserves the bigram counts *exactly* (per-state successor shuffle → random
Eulerian path) and randomises only the 2nd order; against it the LP sits at
z ≈ 0.

**The flatness is informative, not data starvation.** The pooled MI test *has
power*: planted 2-back autokeys, each against its own exact-bigram null, light
up at **z ≈ +42** (additive `c[i]=p[i]+c[i-1]+c[i-2]`) and **+40** (a Quagmire
mixed-alphabet version — the mixing cannot hide it, since conditional MI is
invariant under bijective relabelling). The LP at z = −0.48 flatly rejects both.
This is the pooled test succeeding where the *per-context* test cannot: grouping
ciphertext by the previous BIGRAM to expose a monoalphabetic group (the length-1
grouped-IoC test extended, `dual-autokey-lag1-lag5.md`) is dead at ~15 samples
per bigram context, but conditional MI aggregates the signal and keeps power.

**It discriminates feedback from latent-state mechanisms.** Running-feedback
ciphers (autokey — output depends on recent *output*) leave conditional MI; the
walk does not, because its context enters through a per-word `base` bijection
that is constant within a word (within-word structure is scrambled plaintext
equality patterns, cross-word is key-global). So this test is consistent with
the walk and is another independent nail in the 2-back autokey family.

**Third order is unmeasurable.** 9,945 of 24,389 possible trigrams occur (max
repeat 5) over ~13k runes — <1 sample per trigram context — and only 1 of 841
bigram contexts reaches ≥30 samples. Per-context extension stops here; the
pooled 2nd-order test above is already conclusive.

## Consequences

- Excludes lagged ciphertext autokey at every depth (`ciphertext-autokey.md`),
  now including genuine **2-back** feedback (additive and Quagmire), which the
  marginal table alone could not reach.
- Bounds any bounded-context inner layer (`autokey-plus-substitution.md`).

## Scripts

- `experiments/obs_dependence.py` — the marginal per-lag contingency tables.
- `experiments/obs_second_order.py` — the joint 2nd-order test, its
  exact-bigram null, the planted-autokey power check, and the data budget.

## Related

- `kappa-spectrum.md`, `bigram-ioc.md` — the null-choice trap this shares.
- `dual-autokey-lag1-lag5.md` — the grouped-IoC (per-context) test this
  pooled test complements.
