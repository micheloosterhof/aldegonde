# The Ciphertext Yields One Cross-Word Constraint (DJU-BEI); the Wiring is Starved

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
- Length-5 repeats: 5 classes, versus ~4.1 expected by chance — noise.
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

## Related

- `repeated-phrase-dju-bei.md` — the one constraint, in detail.
- `no-known-plaintext-foothold.md` — no KP shortcut either.
- `length-clocked-walk.md` — the model and key `(base_0, g, σ)`.
