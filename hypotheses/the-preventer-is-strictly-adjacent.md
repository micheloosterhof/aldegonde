---
type: observation
---
# The Base Cancels Across a Seam Too, and the Preventer Sees Only One Rune Back

## Status

**Status**: confirmed. The identity is verified exactly against a synthetic walk — 7,208
agreements, 0 disagreements — before anything is read from it.

## The cross-seam identity

Inside a block the base cancels from a lag-k coincidence
(`d-profile-pins-g-to-five-cycles.md`). Across a boundary the base *changes*, since
`base_(w+1) = base_w ∘ g^a ∘ σ` with `a` the clock at the last rune of block w — and it
cancels anyway:

    c(i) = c'(j)   ⟺   p_i = g^(a − c_i) ∘ σ ∘ g^(c'_j) (p'_j)

Writing `u = (a − c_i) mod 5`, which is simply the distance from the end of block w, and
`v = c'_j mod 5`, every cross-seam pair tests the permutation

    h(u,v) = g^u ∘ σ ∘ g^v

**So the cross-seam coincidence rate, split by (u, v), is a key-free measurement of σ.**
Every other statement about σ in this directory is conditional on the chain model; this
one is not.

The clock convention is unknown (`clock-convention-is-out-of-reach.md`), which shifts
every `v` by the same constant — five relabelings, all enumerable. `u` is a distance and
carries no offset.

## The preventer is strictly adjacent

The same table answers a second question outright. Coincidence by distance from the end
of block w and offset into block w+1, chance 0.0345:

| | j=0 | j=1 | j=2 | j=3 |
|---|---|---|---|---|
| **di=0** | **0.0079 (−16.3)** | 0.0318 (−0.8) | 0.0305 (−1.1) | 0.0360 (+0.3) |
| di=1 | 0.0350 (+0.2) | 0.0293 (−1.6) | 0.0328 (−0.4) | 0.0284 (−1.4) |
| di=2 | 0.0351 (+0.2) | 0.0359 (+0.4) | 0.0372 (+0.6) | 0.0375 (+0.6) |
| di=3 | 0.0385 (+0.8) | 0.0316 (−0.7) | 0.0337 (−0.2) | 0.0308 (−0.7) |

**Exactly one cell of the sixteen is suppressed** — the adjacent one — and every other
sits at chance with |z| at most 1.6.

Inside a block the picture is the same: d1 is 0.0063 and d2 through d7 are at chance
(`d5-bounds-the-clock-perturbation.md`).

**The preventer inspects the immediately preceding emission and nothing else.** That
excludes a rule refusing to repeat within a window of two or more, and any rule carrying
memory beyond one rune. It also confirms from the other side that block boundaries are
invisible to it, which `doublet-deficit-is-global.md` shows for the rate and this shows
for the *reach*.

## What the σ channel is worth

| quantity | value |
|---|---|
| usable cross-seam pairs | 19,590 |
| (u, v) cells | 15 |
| median pairs per cell | 1,300 |
| error per cell | 0.0051 |
| graph mass of a random permutation on the cross-word table | 0.0344 ± 0.0062 |
| **signal to noise per cell** | **1.22** |

Real but small. Fifteen cells at SNR 1.2 carry under ten bits, about what the
within-block profile carries about `g`. But `σ` lives in a space of roughly a hundred
bits rather than `g`'s conjugacy class, so a pool filter is meaningless here in a way it
was not for `g` — and `g-can-be-filtered-not-found.md` already shows that even for `g`
the channel ranks rather than confirms.

**What it is good for is verification.** Given a proposed `(g, σ)` the identity predicts
fifteen numbers at no cost. That is the first check on σ that does not assume the chain,
and any future candidate should be run through it.

## Falsification

- The identity is exact or it is wrong; the synthetic check is the test and it passes
  with zero disagreements. If the base-step convention in `doublet_dodge_walk.encipher`
  is not the author's, the exponent `a` changes and the cells relabel, but the form
  survives.
- If the preventer were window-based, cells at di=0, j=1 and di=1, j=0 would be
  suppressed too. They read −0.8 and +0.2.
- The σ channel's SNR is measured against prose's cross-word table. A body register with
  much flatter cross-word structure would lower it further; a sharper one would raise it.

## Scripts

- `experiments/cross_seam_identity.py`

## Related

- `d-profile-pins-g-to-five-cycles.md` — the within-block identity this extends.
- `g-can-be-filtered-not-found.md` — why ten bits filters but does not find.
- `doublet-deficit-is-global.md` — the rate is boundary-blind; this says the reach is too.
