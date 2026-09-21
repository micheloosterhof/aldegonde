---
type: hypothesis
---
# The Cross-Seam Table Is Flat, Which Leans Against the Right-Acting Base Step

## Status

**Status**: a lean at about two sigma, not a conclusion. It is the first measurement that
bears on a choice every model in this directory has made by assumption.

## The two conventions make opposite predictions

`the-preventer-is-strictly-adjacent.md` derives, for a base that steps on the **right** —
`base_(w+1) = base_w ∘ g^a ∘ σ` —

    c(i) = c'(j)   ⟺   p_i = g^(a − c_i) ∘ σ ∘ g^(c'_j) (p'_j)

The base cancels because it is the outermost map on both sides. Step it on the **left**
instead — `base_(w+1) = g^a ∘ σ ∘ base_w` — and it does not: the second alphabet is
`g^a ∘ σ ∘ base_w ∘ g^(c'_j)` and no rearrangement removes `base_w` from the comparison.

So:

- **right action** — the cells `(u, v) = (di mod 5, (phase + 1 + j) mod 5)` each test a
  different permutation `g^u ∘ σ ∘ g^v`, sit at different rates, and the table is
  **overdispersed**;
- **left action** — the cells test nothing in particular and the table is **flat**.

## The measurement

`experiments/which_side_sigma_acts.py`. The statistic is the homogeneity χ² over the
cells per degree of freedom, minus the same quantity with the phases randomised — which
subtracts the structure that comes from `di` alone. Everything runs at the body's own
corpus size, since the effect scales with it.

| base step | excess overdispersion |
|---|---|
| `base ∘ (g^a ∘ σ)` — **right** | **+1.84 ± 0.92** (10 of 10 keys positive) |
| `(g^a ∘ σ) ∘ base` — **left** | +0.06 ± 0.36 (4 of 10 positive) |
| **the body** | **−0.10** |

- against the right-action simulations: **z = −2.10, below all ten**
- against the left-action simulations: z = −0.42, below six of ten

An earlier run at twelve other keys gave the same picture — 12 of 12 positive, mean
+1.80, body below all. Taken together the body falls below all twenty-two right-action
simulations, a nonparametric p of about 0.04.

## What it would mean

Under a left action the σ-chain permutes the **output** alphabet rather than its input.
Nothing inside a block changes, so every within-block result stands untouched — including
`d-profile-pins-g-to-five-cycles.md`, which uses only within-block pairs.

What does change is that **σ has no key-free channel at all**. The cross-seam identity
was the one measurement of σ that did not assume the chain
(`the-preventer-is-strictly-adjacent.md`), and it exists only for a right action. If the
step is on the left, every statement about σ in this directory is conditional on a model
and none of them is testable at a seam.

## Three readings that survive this

Stated so the lean is not over-read.

1. **The base may change at some unit other than the block.** If it changes per line or
   per sentence, most "seams" are not base changes and the cross-seam pairs are ordinary
   within-base pairs, which would also flatten the table.
2. **There may be no chain at a seam at all** — bases drawn independently per block. The
   chain evidence is `word-repeat-accounting.md`'s consistency argument, which rests on
   one repeated phrase.
3. **The clock convention may differ** in a way the phase labelling does not capture.
   Three conventions were tried — per rune, per rune plus separator, reset per block —
   and none produced an excess on the body. A constant offset cannot matter, since it
   relabels cells without changing homogeneity.

## Falsification

- More ciphertext settles it. The effect is +1.8 at 2,928 blocks with a spread of 0.9, so
  four times the corpus would put a right action at about four sigma from a flat table.
  There is no more corpus.
- If a different base-change unit is right, the same test run with boundaries at lines or
  pages should show the excess appear. That is a direct experiment and it is cheap.
- If someone proposes a specific `(g, σ)`, the right-action identity predicts fifteen
  numbers. A candidate that matches them would settle the side outright.

## Scripts

- `experiments/which_side_sigma_acts.py`
- `experiments/cross_seam_identity.py` — the identity, verified exactly for the right
  action.

## Related

- `the-preventer-is-strictly-adjacent.md` — where the identity comes from.
- `sigma-is-even.md`, `sigma-cycle-type-narrowed.md` — σ results that assume the chain and
  would keep their conditional status either way.
