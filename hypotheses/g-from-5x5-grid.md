---
type: hypothesis
---
# Constructing the Order-5 Step `g` from a 5×5 Grid

## Claim

The order-5 letter step `g` (see `length-clocked-walk.md`) is built by arranging
**25 of the 29 runes in a 5×5 grid and rotating each column by one** — giving
**five 5-cycles + 4 fixed runes**, which is exactly the richest order-5
permutation on 29 symbols. This is the natural, **non-arithmetic** way to
construct an order-5 permutation on 29 runes (decimation/multiplication cannot:
GF(29)* has order 28 and 5∤28, so multiply-by-k has order in {1,2,4,7,14,28},
never 5). A grid layout could shrink `g`'s key from an arbitrary order-5
permutation toward a keyword-sized space — BUT only if the layout is *also*
low-diagonal (see "layout constraint"): a plain keyword fill gives chance
doublets, so the reduction is weaker than it first appears.

## Status

**Status**: unresolved (construction proposal; the actual arrangement is
unknown and unverified)

## Mechanism

- 25 runes go into a 5×5 grid; the remaining 4 are **fixed points** (forced:
  29 ≡ 4 mod 5, so an order-5 permutation on 29 has at least 4 fixed runes).
- `g` = "shift each column down by one" → each **column is a 5-cycle**; the
  5 columns are 5 disjoint groups; the 4 leftover runes map to themselves.
- `g⁵ = id` (five shifts return each column to start) → the d5 echo.
- Applying `g` per letter and its powers `g⁰…g⁴` gives the 5 within-word
  alphabets; a rune only ever maps to the other four runes **in its own
  column-group**.

## The layout constraint (naive order is REFUTED)

A doublet needs `p[i-1] = g(p[i]) = below(p[i])`, so the plaintext bigram is
**(below(x), x)**: the doublet rate is the sum of the bigram probabilities of
every **vertically-adjacent column pair**. Low doublets therefore demand that
**column-neighbors be rare bigrams** — common runeglish pairs must not sit
above/below each other.

The **naive Gematria-order grid FAILS this**: measured on real runeglish
bigrams it gives a doublet rate of **0.0319 ≈ chance (0.0345)**, not the
observed 0.0063 (random grids: mean 0.034; an *arranged* grid can reach 0.000).
So the layout is neither the natural order nor arbitrary — it is a **deliberate
low-diagonal arrangement**, and a *plain* keyword fill would also fail (it would
be ~chance too). The keyword-search must therefore keep only low-diagonal fills;
the low-doublet constraint alone does not uniquely pin the grid (many
low-diagonal arrangements exist).

The stay-slot reading (grid advance driven to ~0, doublets from the hold)
is disproved by the doublet position-profile test — see `stay-slot-hold.md`.
The live reading is order-5-g: the grid is tuned to 0.0063 directly, its
columns avoid common bigrams, and (new constraint) the diagonal bigram
class must be positionally near-baseline in plaintext.

## Group composition (illustrative only — this grid gives CHANCE doublets)

The Gematria Primus order, row-major, last 4 fixed — shown only to make the
construction concrete. **It is refuted as the actual grid** (doublet rate 0.032,
see above); the real grid is a low-diagonal arrangement, unknown.

```
grid (row-major):
  ᚠ(F)  ᚢ(U)  ᚦ(TH) ᚩ(O)  ᚱ(R)
  ᚳ(C)  ᚷ(G)  ᚹ(W)  ᚻ(H)  ᚾ(N)
  ᛁ(I)  ᛄ(J)  ᛇ(EO) ᛈ(P)  ᛉ(X)
  ᛋ(S)  ᛏ(T)  ᛒ(B)  ᛖ(E)  ᛗ(M)
  ᛚ(L)  ᛝ(NG) ᛟ(OE) ᛞ(D)  ᚪ(A)
  fixed: ᚫ(AE) ᚣ(Y) ᛡ(IA) ᛠ(EA)

the five 5-cycles (columns):
  group 0: (ᚠ ᚳ ᛁ ᛋ ᛚ)   F C I S L
  group 1: (ᚢ ᚷ ᛄ ᛏ ᛝ)   U G J T NG
  group 2: (ᚦ ᚹ ᛇ ᛒ ᛟ)   TH W EO B OE
  group 3: (ᚩ ᚻ ᛈ ᛖ ᛞ)   O H P E D
  group 4: (ᚱ ᚾ ᛉ ᛗ ᚪ)   R N X M A
```

## Evidence for

- **Order-5 forces this shape.** Order 5 (prime) ⇒ every cycle length divides
  5 ⇒ 5-cycles + fixed points. The richest on 29 is five 5-cycles + 4 fixed —
  and richness is what the doublet suppression needs (`g` must move most runes).
- **29 = 25 + 4** fits a 5×5 grid with exactly 4 leftover — a clean match to
  the forced fixed-point count.
- **Decimation is excluded** (5∤28), so `g` must be a non-arithmetic
  arrangement; a grid/keyword layout is the natural one and is idiomatic for
  Cicada (keys derived from words/gematria).
- **Key reduction.** A grid layout makes `g` keyword-fillable → its key space
  shrinks from ~29! to dictionary size, which is the missing ingredient for an
  **enumeration** attack (blind search over 29! is hopeless; over keywords is
  not). Pairs with the doublet-consistency verifier as a fast pruner.

## Evidence against / open

- **The arrangement is unknown — it IS the key.** The Gematria-row-major grid
  above is the default guess; column-major, row-shift instead of column-shift,
  a keyword-mixed fill, or a different choice of the 4 fixed runes are all
  equally admissible. This note proposes the *construction family*, not the
  instance.
- **The 4 fixed runes leak plaintext doublets.** A fixed rune `Y` (g(Y)=Y)
  passes plaintext `YY` through as a ciphertext doublet. So the fixed set should
  be low-doubling runes; in the candidate above the fixed set is AE/Y/IA/EA
  (digraph-ish runes that rarely double) — consistent, but not a test.
- **Not verified.** No decryption confirms any grid.

## Enumeration result (July 2026)

`experiments/enumerate_keys.py` built the grid-`g` family for 24
Cicada-relevant keywords x {row-major, column-major} (48 order-5 grids)
and paired each with keyword-mixed `sigma`, pushing all 1,152 pairs
through `experiments/walk_verifier.py`. Two findings, both negative and
both sharpening this note:

1. ~~**The doublet diagonal kills keyword fills outright.**~~ The best
   keyword grid-`g` in that scan had within-word diagonal **0.0229**
   (CIRCUMFERENCE, row-major) with the rest 0.027-0.035, 3.6x-5.5x above
   the required 0.0063. **RETRACTED (July 2026,
   `experiments/g_construction_survey.py`)**: that scan held two free
   parameters of the construction at their defaults — the four fixed
   runes were taken as the *last four* of the keyword order, and every
   column was rotated by *one*. Freeing them (any 4 of 29 fixed, any
   rotation 1-4 per column, which the diagonal decomposes over
   independently) spans the whole range: the same DIUINITY row-major
   family reaches 0.0003, CIRCUMFERENCE 0.0019, and EVERY ordering and
   fill tested — gematria, prime-value, reversed, English-alphabetical,
   and ten keywords — clears the required band. Concretely, the defaults
   give DIUINITY 0.0469 / CIRCUMFERENCE 0.0418 / PRIMES 0.0218 /
   WISDOM 0.0274, but one keyword with free fixed-runes and rotations
   yields **~2 x 10⁵ candidates inside the 0.004-0.009 band**. Keyword
   grid fills are therefore not excluded as a *family*.

   **But the structure supplies nothing** (same script, distribution
   check — the minimisation above searches ~24M variants per
   ordering/fill, and the minimum of any large permutation family is
   near zero, so reaching the band is not by itself evidence that the
   construction helps). Comparing 6,000 random members of the DIUINITY
   grid family against 6,000 random order-5 permutations: mean diagonal
   **0.0345 vs 0.0346**, sd 0.0149 vs 0.0121, fraction at or below
   0.0063 **0.17% vs 0.07%** (KS D = 0.077, p < 0.001 — marginally
   heavier tails, identical centre). A grid-derived `g` is
   statistically an ordinary order-5 permutation. So the ORIGINAL
   claim's spirit stands — keyword order does not *supply* a low
   diagonal — while its letter (that the family cannot reach the band)
   was an artifact of the defaults. Reaching the band inside the family
   costs a ~1-in-600 search, which is a search, not a construction.
2. **No state return.** Of 480 (g, sigma) pairs passing the parity
   necessary condition, **zero** produce a DJU-BEI full state return
   (`M_1477 = M_2926`). Under the full-return reading, the true key is not
   a keyword-grid `g` with a keyword `sigma` from this set.

The enumeration harness is reusable: better `g` families (annealed
low-diagonal grids, gematria/prime-ordered fills) drop straight into it.

**The open problem, restated after the retraction.** It is not "can a
structured construction be low-diagonal" — the family contains such
members (about 1 in 600 of them), and the DJU-BEI state-return result
above must be re-run over the corrected family before it means
anything. But the family reaches the band by size, not by design: its
diagonal distribution is that of random order-5 permutations, so the
grid parameterisation offers no search advantage over annealing. The
problem is the opposite of the one recorded: the family is too RICH to
enumerate. One keyword and
one fill already yield ~2 x 10⁵ in-band `g` candidates; across ~10⁴
plausible keywords and three fills that is ~10⁹-10¹⁰ for `g` alone,
before `σ` — which has no construction proposal at all and cannot be
hill-climbed (`no-known-plaintext-foothold.md`: the (g, σ) landscape is
a delta function). The diagonal band is simply too weak a filter. What
the attack needs is either much stronger *joint* constraints on (g, σ)
— the g²-near-background condition, the positional-profile condition,
the σ cross-word diagonal, parity, and the DJU-BEI relation applied
together — or a construction principle that pins the fixed-rune choice
and rotations rather than leaving them free.

## Predictions

- ~~`g` has **exactly five 5-cycles + 4 fixed**~~ — **fewer 5-cycles are
  not excluded** (July 2026, `experiments/sigma_algebraic_floor.py` and
  the fixed-point census). Order 5 forces the cycle type to be `k`
  5-loops plus `29 − 5k` fixed runes, `k ≤ 5` — no long cycles are
  possible at all, so "small loops" is a theorem, not a design choice.
  Counts: k=5 gives 9.82e23 permutations (4 fixed), k=4 gives 1.62e21
  (9 fixed), k=3 gives 1.35e17, and the whole order-5 population is
  9.84e23 of 29! ≈ 8.8e30 — about one permutation in ten million.
  The old argument for k=5 was that fixed runes leak plaintext doublets,
  so few are affordable; but choosing the leakers among runes that never
  double in English (ᛠ, ᚦ, ᚣ, ᚫ, ᚹ, ᚻ, ᛟ, ᛄ all have zero self-repetition
  in the register table) makes up to 21 fixed points affordable on the
  d1 channel alone. Only k=1 (24 fixed) is excluded there.
- **The d2/d3/d4 cells are a direct measurement of `g`'s fixed-point
  count.** Under strict `g⁵ = id`, letters on a 5-loop return only at
  distance 5, so at d2, d3 and d4 the ONLY leak is the fixed runes:
  the returned fraction φ_d at those distances should equal `f/29` and
  be equal across them. Measured (`mixed-cycle-progression.md`):
  φ3 = 0.17 ± 0.14 → f ≈ 5 ± 4, φ4 = 0.38 ± 0.19 → f ≈ 11 ± 5.5 (φ2 is
  powerless — plaintext barely repeats at distance 2). Both are
  consistent with k=5 (f=4) and with k=4 (f=9); the cells cannot yet
  separate them, and their mutual disagreement (5 vs 11) is the d3/d4
  tension in another guise. A better plaintext reference would turn this
  into a genuine parameter estimate for `k`.
- If the grid is keyword-derived, enumerating candidate keywords + verifying
  with the doublet-diagonal check (now including the positional-baseline
  constraint from `experiments/doublet_position_profile.py`) + quadgrams is
  a feasible attack — unlike blind permutation search.

## Related

- `length-clocked-walk.md` — the model; this proposes a construction for its
  `g`. The same grid/keyword idea could apply to `σ` (the space step).
- `stay-slot-hold.md` — the disproved hold reading of the doublets; the
  fixed-point leakage above was the same "plaintext doublets show through"
  effect, now excluded by the position profile.

## Verdict

A concrete, non-arithmetic, Cicada-idiomatic construction for the order-5 step:
25 runes in a 5×5 grid, columns rotated into five 5-cycles, 4 leftover fixed.
It matches the structural constraints (order-5 richness, 29=25+4, no
decimation). The hoped-for payoff — a keyword-sized key — is **weaker than
first stated**: the low-doublet requirement forces a *deliberate low-diagonal*
layout (the naive Gematria grid gives chance doublets, measured 0.032), so a
plain keyword fill won't do, and the low-doublet constraint alone doesn't
uniquely pin the grid. The construction family is well-motivated; the specific
low-diagonal arrangement is unknown and is what a crack would recover.
