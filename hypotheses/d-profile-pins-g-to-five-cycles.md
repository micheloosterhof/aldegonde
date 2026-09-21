---
type: observation
---
# The Coincidence Profile Filters g by a Hundred and Says It Fixes Four Runes

## Status

**Status**: confirmed, with planted controls at three different cycle structures. The
filter is key-free — it uses no base, no σ and no search.

## Why every lag except 5 measures g

Inside a block the alphabet at position `j` is `base ∘ g^(c+j)`. For a lag-k pair,

    c_i = c_(i+k)  ⟺  g^(c+i)(p_i) = g^(c+i+k)(p_(i+k))  ⟺  p_i = g^k(p_(i+k))

**The base cancels.** Since `g` has order 5 only `k mod 5` survives, so

    d_k = P(p_i = g^(k mod 5)(p_(i+k)))

is a function of the plaintext and of `g` alone. At k = 5 the power is the identity and
d5 is the plaintext's own coincidence — which is exactly why it is the leak
(`d5-bounds-the-clock-perturbation.md`). At every other k it is a **measurement of g**.

Five lags are usable: 2, 3, 4, 6, 7. Lag 1 is spoiled by the preventer and lag 5 carries
no g.

## The body against a pool of candidate g

`experiments/d_profile_constrains_g.py`, 6,000 order-5 permutations with one to five
five-cycles, uniformly over the count. Plaintext lag-k tables from 60 prose corpora.

| lag | g power | body measured | predicted over the pool |
|---|---|---|---|
| 2 | g² | 0.0347 ± 0.0022 | 0.0352 ± 0.0086 |
| 3 | g³ | 0.0370 ± 0.0027 | 0.0456 ± 0.0104 |
| 4 | g⁴ | 0.0410 ± 0.0035 | 0.0434 ± 0.0080 |
| 6 | g¹ | **0.0245 ± 0.0043** | 0.0495 ± 0.0117 |
| 7 | g² | 0.0421 ± 0.0075 | 0.0517 ± 0.0127 |

The spread over g is two to three times the measurement error at every lag, so each row
carries real information. χ² over the pool: min 1.3, median 79.8.

| cut | permutations kept | reduction | five-cycle counts (k = 1…5) |
|---|---|---|---|
| top 1% | 60 | **100×** | **[0, 0, 2, 22, 36]** |
| top 5% | 300 | 20× | [0, 6, 39, 99, 156] |

## The controls, which are what make this usable

Absolute χ² is contaminated by model error — the plaintext tables are prose, not the
body's own plaintext — so the valid output is a **rank**, and planted controls calibrate
it. Enciphering prose through the walk with a known `g` and filtering the same pool:

| true k | rank of the true g | five-cycle counts in the top 1% |
|---|---|---|
| 1 | 832 / 6,000 | [20, 25, 11, 3, 1] |
| 3 | 89 / 6,000 | [6, 20, 19, 12, 3] |
| 5 | 2 / 6,000 | [0, 1, 2, 23, 34] |

**The top-1% profile tracks the truth in all three.** The filter sharpens as `g` moves
more points, which is expected: a `g` with one five-cycle is nearly the identity and many
others mimic it.

**The body's top-1% profile is [0, 0, 2, 22, 36], which is the k = 5 control's
[0, 1, 2, 23, 34] to within counting noise.**

## The conclusion

**g has five five-cycles: it fixes 4 of the 29 runes and moves the other 25.**

The reason is visible in the table. The body's d-values at lags 2, 3, 4, 6 and 7 sit much
closer to chance than the plaintext's do (prose reads 0.0368, 0.0582, 0.0539, 0.0684,
0.0699 at those lags), so `g` has to move enough points to destroy the plaintext's lag-k
structure. A `g` with one five-cycle leaves most of it intact and predicts values far too
high.

This upgrades `g-has-more-than-one-cycle.md` from "at least two" to "five", and it
confirms as a measurement what `doublet_dodge_walk.order5_fixing(…, 4)` has assumed by
construction since it was written.

## Scope and small biases

- **Prose stands in for the body's plaintext.** The register agrees where it can be
  checked: at lag 5 the sixteen-page LP register gives 0.0733 ± 0.0133 against prose's
  0.0589 ± 0.0008, z = 1.1.
- **The preventer perturbs about 2.8% of runes**, so a lag-k pair is touched about 5.5%
  of the time and every d_k is diluted toward chance by that much. Undoing it moves d6
  from 0.0245 to 0.0239 — negligible against ±0.0043.
- The pool is uniform over cycle counts 1…5, which is a prior, not a fact. The controls
  show the filter recovers the truth from that prior at k = 1, 3 and 5 alike.

## Falsification

- If `g` does not have order 5 the derivation collapses; `period5-is-confirmed`
  establishes the order independently.
- If the body's plaintext has a materially different lag-k structure from prose, the
  predictions shift. Lags 6 and 7 are the most register-sensitive and also the noisiest.
- A pool built from a different prior over cycle structure would change the posterior.
  Re-running with a pool uniform over *permutations* rather than over cycle counts is the
  direct check, and the k = 1 control shows the filter does not simply prefer high k.

## Scripts

- `experiments/d_profile_constrains_g.py`

## Related

- `g-has-more-than-one-cycle.md` — the weaker version this replaces.
- `d5-bounds-the-clock-perturbation.md` — the one lag that carries no g.
- `g_fixed_points.py`, `g_graph_mass.py` — earlier measurements of the same object.
