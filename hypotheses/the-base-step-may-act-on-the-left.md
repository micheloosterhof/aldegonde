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

## Where that leaves the three readings

One is now closed outright and one is answered elsewhere, which leaves the left action as
the reading that fits everything:

- **the base changes at a larger unit** — closed below, at 8.5 sigma;
- **there is no chain at a seam** — `word-repeat-accounting.md` argues there is, on two
  counts that must give one pool: the chain's interval [153, 22,369] contains the 2,752
  that `identical` implies and the chainless 53 [28, 334] misses it by eight times, and
  holding the corpus's 17 repeats fixed while shuffling only word order puts two of them
  adjacent once in 20,000 draws;
- **a left action** — nothing contradicts it.

Each leg is worth about p = 0.04 on its own except the first, which is decisive. The
synthesis is the most consistent reading of three independent measurements, not a proof
of any one of them.

## Three readings that survive this

Stated so the lean is not over-read.

1. **The base may change at some unit other than the block.** If it changes per line or
   per sentence, most "seams" are not base changes and the cross-seam pairs are ordinary
   within-base pairs, which would also flatten the table.

   *Tested twice, and closed.* Running the identical statistic with the base changing at
   line boundaries gives **−0.23** on 594 lines of 21.8 runes, against the block-level
   −0.05 and a right-acting walk's +1.84 ± 0.92.

   The direct test is better. `g` has order 5, so two runes five apart share a power of
   `g`; if they also share a base they coincide at the plaintext rate and otherwise at
   chance. The cross-block lag-5 rate therefore reads out how often the base survives an
   edge, with no key at all:

   | corpus | across a block edge |
   |---|---|
   | planted walk, base steps every block | 0.0363 ± 0.0018 |
   | planted walk, base never steps | **0.0595 ± 0.0023** |
   | **the body** | **0.0347 ± 0.0018** |

   The body sits on the stepping walk (z = −0.64) and **8.5 sigma** from the fixed one.
   A surviving base leaks 0.0232 of coincidence, so the fraction of edges carrying an
   unchanged base is −0.07 ± 0.11, with a 95% upper bound of **0.15**. A rule stepping
   the base every second block would leave half the edges unchanged and is excluded many
   times over.

   **The base changes at essentially every block edge.** Any unit larger than the block —
   a phrase ending in a heavier mark, a line, a page — is out.
2. **There may be no chain at a seam at all** — bases drawn independently per block. The
   chain evidence is `word-repeat-accounting.md`'s consistency argument, which rests on
   one repeated phrase.
3. **The clock convention may differ** in a way the phase labelling does not capture.

   *Tested, same tick, and this one is now closed.* Scanning the whole affine family
   `phase = (α · cumulative runes + β · block index) mod 5` — 25 conventions covering
   both quantities the scribe could have been counting — the body's best excess is
   **+0.48**, at z = +0.23 against a max-of-scan null. A planted right-acting walk at the
   same corpus size reaches **+2.26 at z = +6.07**, and lights up its whole β = 0 column,
   since any invertible α is a relabelling of the true convention.

   Even α = 0, which drops the rune count entirely and leaves only the offset-into-block
   structure, gives the planted walk +1.59 and the body −0.51. The body lacks not just
   the phase structure but the positional structure a right action produces.

   A constant offset cannot matter either way, since it relabels cells without changing
   homogeneity.

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
