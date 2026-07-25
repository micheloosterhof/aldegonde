---
type: observation
---
# The Ciphertext Yields One Cross-Word Constraint (DJU-BEI); the Wiring is Starved

## Status

**Status**: confirmed (characterization) for the repeat census itself. The
`(g, σ)` framing and the attack consequences are conditional on the
length-clocked-walk model, which is plausible, not confirmed.

## Claim

A systematic hunt for repeated ciphertext structures in sections 0-9 finds
**exactly one genuine cross-word state-return: DJU-BEI**. Every other repeat is
at chance. So the ciphertext contains essentially **one** constraint on the
`(g, σ)` wiring, which is far too little to recover two 29-permutations — the
cipher destroyed cross-word alphabet correlations almost completely.

## Evidence

`experiments/ciphertext_collisions.py`, clean corpus (12,956 runes, 2,928 words):

- Maximal repeated substrings length ≥ 6: **one** — DJU-BEI (`ᛞᛄᚢᛒᛖᛁ`), at word
  1477 phase 0 and word 2926 phase 0, both word-initial. Chance expectation at
  length 6 is 0.14, so it is genuine. It gives `base_1477 = base_2926`:
  σ-count 1449, Σ(L−1) mod 5 = 1 over the interval (product of steps = identity).
- Length-5 repeats: 5 classes, versus ~4.1 expected by chance — noise as a
  count. One of the five (ᛁ-ᛗᛝᚣᚪ) is boundary-consistent and word-aligned
  (`repeated-phrase-dju-bei.md`, count-level P = 0.075) — suggestive, but
  not significant enough to admit as a second wiring constraint.
- Identical ciphertext words (len ≥ 3) recurring: 15, versus ~11 expected among
  726 three-rune words — noise, and 3 runes is too short to tell genuine from
  chance or to yield a usable constraint.

## Why this matters

Both candidate attacks depend on cross-word signal and are starved by this:

- **Collision/constraint attack:** one equation cannot pin two permutations.
- **IoC-scored `(g, σ)` hillclimb:** the *within-word* coincidence (the d5 echo)
  is invariant to g's wiring — it only fixes ord(g)=5 — so it gives no gradient
  on the wiring. The wiring information is entirely cross-word, i.e. DJU-BEI
  alone. No gradient exists to climb.

## Consequence: enumeration, not search

Ciphertext-only key recovery by search is infeasible on this corpus. The only
remaining path is to **enumerate structured `(g, σ)` candidates** (number-
theoretic / keyword / gematria grids, low-diagonal) and *verify* each:

1. DJU-BEI filter — require `∏ g^((L−1) mod 5) ∘ σ = id` over `[1477, 2926)`.
2. Solve `base_0` as a monoalphabetic (IoC is blind to it; a quadgram solve
   recovers it in seconds once `(g, σ)` are fixed).
3. Score the full decryption on quadgrams.

This bets everything on the true key being drawn from a small structured set. If
`(g, σ)` are arbitrary mixed permutations, the ciphertext does not contain enough
to recover them and 0-9 is unbreakable by these methods.

## Enumeration built and run (July 2026)

The verify-not-search program of this note is now implemented:
`experiments/walk_verifier.py` (self-tested: exact round-trip decryption
with the true key, random-key rejection) runs the cascade — DJU-BEI state
return, g/sigma doublet diagonals, quadgram `base_0` solve —
and `experiments/enumerate_keys.py` drives structured keyword-grid `g` x
keyword `sigma` through it. First pass (24 keywords x 2 orientations x
24 sigmas): **0 of 480 parity-valid pairs achieve a state return, and the
best keyword grid-`g` diagonal in that scan was 0.023 vs the required
0.0063**. **The diagonal half is RETRACTED** (July 2026): that scan held
the four fixed runes at the keyword order's last four and rotated every
column by one; freeing those two free parameters lets every ordering
reach the band. The 0/480 state-return result inherits the same defect —
it covered the defaults-only slice, a vanishing fraction of the family —
and must be re-run before it means anything. See `g-from-5x5-grid.md`.

## Related

- `repeated-phrase-dju-bei.md` — the one constraint, in detail.
- `no-known-plaintext-foothold.md` — no KP shortcut either.
- `length-clocked-walk.md` — the candidate model and key `(base_0, g, σ)`
  (plausible, not confirmed).
