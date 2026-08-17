---
type: hypothesis
---
# The Space Step σ is Affine (a·x + b mod 29)

## Claim

The walk's space step σ (`length-clocked-walk.md`) is an affine map on the
rune index: σ(x) = a·x + b mod 29, one of 812 candidates. Cicada's arithmetic
idiom (the solved pages shift by primes and totients mod 29), and the first
enumerable σ construction after the keyword-disk family was exhausted
(`mixed-alphabet-vigenere.md`). Note the same family cannot supply g: no
affine map mod 29 has order 5 (orders divide 28, or 29 for translations), so
the design would be grid-built g + arithmetic σ.

## Status

**Status**: unresolved (state-return filter run, Aug 2026: no enrichment, no
full return; 28 chance-level candidates await the base₀ verifier). One prior
strike stands against the family.

## Prior strike (register-dependent)

`sigma_algebraic_floor.py` (July 2026): the seam algebra makes the cross-word
doublet rate σ's diagonal, observed 23/2927 = 0.0079. On the reference
cross-word table the affine family floors at **0.0122** — the single best
member sits ~2σ above the observation (Poisson P(≤23 | 35.7) ≈ 0.02), and the
bulk of the 812 sits far higher (typical ~1/29 → ~100 expected events). This
disfavors the family but rests on the reference register's (final × initial)
table; it is not airtight.

## The state-return filter (register-free)

`experiments/affine_sigma_state_return.py`. Identical ciphertext at words
1477/2926 forces the interval product Q = ∏ g^((L−1) mod 5)∘σ over the 1,449
intervening words to fix ≥ 6 points (the full-identity reading is the
retracted too-strict filter, `repeated-phrase-dju-bei.md`). Q depends only on
(g, σ, word lengths) — no base₀, no register.

Swept: the magic-square g pool at 3.5σ (46 candidates, retains a true family
g with probability 1.00) × all 812 affine σ = 37,352 pairs.

- Empirical null: P(fix ≥ 6) = 1.01e-3 over 300 random order-5 g × the same
  σ set — 1.7× the Poisson(1) reference 5.9e-4, so the matched null matters.
- **Result: 28 pairs pass vs 37.6 expected by chance** — no enrichment
  (z ≈ −1.6). Max fixed points 7 (twice); nothing near a full return (29).

Since fix ≥ 6 is a *necessary* condition for a true key, those 28 pairs are
the complete surviving candidate set for this (g-pool × σ-family) universe.
They are individually indistinguishable from chance and need the decisive
stage: the base₀ quadgram solve of `walk_verifier.py` (the walk makes base₀
an outer monoalphabetic once (g, σ) is fixed — a correct pair must yield
readable runeglish).

## Scope

A negative here decides only "g ∈ magic-square 3.5σ pool × σ affine". The
pool is the canonical-tie-break family (190,008 members, 2^17.5 of g's
2^79.7 space), so this is a bet on the designer's construction, per
`magic-square-grid-key.md`. The filter machinery is generic and reusable for
any future (g-pool, σ-family) pairing.

## Scripts

- `experiments/affine_sigma_state_return.py` — the filter (self-test
  cross-validates the vectorized fold against `walk_verifier.step_products`).
- `experiments/sigma_algebraic_floor.py` — the prior seam-floor strike.

## Related

- `length-clocked-walk.md` — the model whose σ this constructs.
- `sigma-power-step.md` — the other σ construction, disproved.
- `magic-square-grid-key.md` — the g pool and why σ's absence blocked it.
- `repeated-phrase-dju-bei.md` — the 6-point return condition.

## Verdict

Open. The register-free filter shows no enrichment and no full return —
affine σ gets no positive support — but 28 necessary-condition survivors
remain unkilled. Next step: base₀ quadgram solve on the 28; all-flat would
close the family within this g pool, any hit reads plaintext.
