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

**Status**: disproved for the magic-square g pool (Aug 2026) — the 6-point
state-return filter left 28 chance-level candidates and the base₀ verifier
killed all 28 with full demonstrated power. Not excluded for g outside that
pool; the register-dependent seam-floor strike disfavors the family
generally.

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

## The base₀ verifier (`--verify`, Aug 2026): all 28 killed

With (g, σ) fixed the walk makes base₀ an outer monoalphabetic, so each pair
is decided by hill-climbing base₀ on quadgram fitness of the full decryption
(vectorized re-implementation of `walk_verifier.solve_base0`, value-identical
by self-test).

- **Power demonstrated, not assumed**: on the known-key reference corpus
  (`walk_reference.json`) the true key round-trips exactly, and the solve
  with the true (g, σ) recovers the true-base₀ fitness to three decimals
  (−4.312) from random restarts. A wrong σ on the same corpus lands at
  −8.951.
- **LP null band** (6 random order-5 g × random affine σ): −8.980..−8.971.
- **All 28 survivors: −8.981..−8.908** — inside the null band, 4.6 log₁₀
  units below the readable level, previews quadgram-flavored gibberish.

A correct pair would have surfaced at ~−4.3. The 28 were accidents of the
Poisson tail, as their count (28 vs 37.6 expected) already suggested.

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

## Correction and re-run (September 2026)

`dju-bei-gate-validity.md`. The state-return filter above is a necessary condition
only if DJU-BEI is a genuine state return, which the walk model makes a ~1×10⁻⁶
event; a true key passes it at the chance rate, so the 28 survivors were never the
complete candidate set. The g pool was also cut to 46 of 190,008 by register-derived
bands that keep a true g about half the time.

`experiments/grid_affine_ungated.py` scored the whole family directly — all 190,008
magic-square g × all 812 affine σ = 154,096,488 keys, no gate, no g pool, base₀
free. No key reached the candidate floor (0.85 nats/rune on a 200-word window; a
true key scores ~1.2) and the best whole-section score is 0.45. The family is
excluded, now without either cut.

## Verdict

Disproved within the swept universe: no (magic-square-pool g, affine σ) pair
decrypts the corpus, established with a verifier whose power was demonstrated
on a planted key at full corpus size. The affine σ idea itself survives only
outside this g pool, where it remains disfavored by the seam floor. The
reusable yield: the two-stage machinery (6-point state-return filter → base₀
solve) now closes any enumerable (g-pool × σ-family) pairing in minutes, so
future construction proposals for either permutation are cheap to test
jointly.
