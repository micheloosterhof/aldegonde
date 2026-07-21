# Constructing the Order-5 Step `g` from a 5×5 Grid

## Claim

The order-5 letter step `g` (see `length-clocked-walk.md`) is built by arranging
**25 of the 29 runes in a 5×5 grid and rotating each column by one** — giving
**five 5-cycles + 4 fixed runes**, which is exactly the richest order-5
permutation on 29 symbols. This is the natural, **non-arithmetic** way to
construct an order-5 permutation on 29 runes (decimation/multiplication cannot:
GF(29)* has order 28 and 5∤28, so multiply-by-k has order in {1,2,4,7,14,28},
never 5). Crucially, if the grid is filled from a **keyword or the gematria
order**, then `g`'s key collapses from an arbitrary order-5 permutation
(~10^20 of them) to a **grid arrangement (keyword-sized)** — the search-space
reduction that could make enumeration feasible.

## Status

**Status**: hypothesis (construction proposal; the actual arrangement is
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

## Group composition (candidate default)

Filling the grid in **Gematria Primus order, row-major**, with the last 4 runes
fixed (this is the *default guess*, not established — see "open"):

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

## Predictions

- `g` has **exactly five 5-cycles + 4 fixed** (not one 29-cycle, not fewer
  5-cycles) — a hard structural constraint any correct `g` must satisfy.
- The 4 fixed runes are the doublet-leakers; the within-word doublet rate
  carries a component = (plaintext doublet rate of those 4 runes).
- If the grid is keyword-derived, enumerating candidate keywords + verifying
  with the doublet-consistency check (`stay-slot-hold.md`) + quadgrams is a
  feasible attack — unlike blind permutation search.

## Related

- `length-clocked-walk.md` — the model; this proposes a construction for its
  `g`. The same grid/keyword idea could apply to `σ` (the space step).
- `stay-slot-hold.md` — the doublet mechanism; the fixed-point leakage above
  is the same "plaintext doublets show through" effect.

## Verdict

A concrete, non-arithmetic, Cicada-idiomatic construction for the order-5 step:
25 runes in a 5×5 grid, columns rotated into five 5-cycles, 4 leftover fixed.
It matches every structural constraint (order-5 richness, 29=25+4, no
decimation) and — most importantly — makes `g`'s key **keyword-sized**, turning
the hopeless 29!-permutation search into a plausibly-enumerable one. The
construction family is well-motivated; the specific arrangement is unknown and
is exactly what a crack would recover.
