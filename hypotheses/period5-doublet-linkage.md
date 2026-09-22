---
type: hypothesis
---
# Hypothesis: The Doublet Suppression and the d5 Leak Are One Order-5 Walk

## Claim

The 5.2× adjacent-doublet suppression and the distance-5 same-alphabet leak are
not two independent features of a periodic substitution, but two faces of a
single stateful cipher driven by one permutation *g* of order 5 — a rotor or
autokey "walk", not a tableau.

## Status

**Status**: unresolved. The linkage is motivated, but the simplest mechanism for
it (phase-gating of doublets) is refuted by the data below. How one order-5 *g*
would set a rune-flat, phase-flat 5× suppression is not answered.

## Mechanism

- *g* has order 5 (g⁵ = identity), already established
  ([d5-partial-alphabet-leak.md](d5-partial-alphabet-leak.md)).
- A stateful walk advances the effective alphabet by *g* each position. g⁵ = id
  returns the alphabet every 5 steps → positions 5 apart share it → the d5 leak
  (at whatever duty cycle the interruptors allow, ~0.54).
- Because the state moves every step, a ciphertext doublet cannot come from the
  cipher standing still; it needs a coincidence the *g*-relation makes rare →
  doublet suppression. A per-position substitution decouples the two, so their
  co-occurrence is itself the argument for a walk.
- Within a word a distance-*d* ciphertext coincidence requires
  P_i = g^d(P_{i+d}). So d1 and d6 both test **g¹** (the designed relation), d4
  tests **g⁻¹** (= g⁴), and d5 tests **g⁰ = identity** (the leak). One *g* ties
  the whole d1–d6 profile together.

## Evidence for

- **The doublet suppression is the cipher's, not inherited.** Runeglish plaintext
  carries 2.1–3.7% adjacent doublets (solved LP 2.3%, lexicon 3.65%); the
  ciphertext is at 0.66% — the cipher pushes doublets 3–5× below the plaintext,
  so it is a design feature to be explained, not a language artifact.
- **Per-position substitution reproduces the d5 leak but not the suppression.**
  A periodic tableau (Vigenère, Beaufort, Quagmire) leaves doublets at chance;
  sub-chance doublets force a tuned adjacent-alphabet relation
  ([doublet-suppression-requires-design.md](doublet-suppression-requires-design.md)).
  A single order-5 *g* is one structure that could supply both.
- **The whole d1–d6 profile follows the powers of one g.** Measured within-word
  same-rune rates (page0-56, z vs Σf²=0.0346): d1 (g¹) 0.18×, z=−15.5; d2 (g²)
  1.01×, z=+0.1; d3 (g³) 1.07×, z=+0.9; d4 (g⁻¹) 1.19×, z=+2.0; d5 (id) 1.42×,
  z=+3.7; d6 (g¹) 0.71×, z=−2.0. **d1 and d6, both g¹, are the two suppressed
  distances**, and d4 (g⁻¹) is elevated — a chirality (g and g⁻¹ behave
  oppositely) that a single directional step produces and a tableau does not.
- **The suppression is language-tuned, not a rule-random *g*.** The ciphertext
  doublet rate 0.0063 equals the plaintext frequency of the bigrams (x, g⁻¹x). A
  random permutation — even one of cycle type 5⁵·1⁴ — gives 0.0345 ± 0.012; the
  observed rate is 2.4σ below that and **0 of 5000 random draws reach it**. So
  *g* is correlated with the bigram table (it avoids common bigrams), which is
  the "tuned relation" [doublet-suppression-requires-design.md] demands. It is
  not pushed to the achievable floor (~0 on the proxy), so it suppresses the
  common bigrams rather than being a maximal minimizer.
- **...but doublet-minimisation is not the design goal.** A direct search over
  the order-5 permutation space (QAP, 2-swap hill-climb, no grid assumption)
  drives the doublet rate to ~0.0001 — an order-5 *g* can nearly eliminate
  doublets by chaining rare bigrams through its 5-cycles. The cipher's 0.0063 is
  5.5× below random but ~66× *above* that floor. So the suppression is deliberate
  yet far from optimal: it reads as a byproduct of whatever rule fixed *g* (the
  period-5 structure, a keyed construction), not as an objective in itself.
- **The forced 4 fixed points read as a 5×5 grid.** 29 = 5·5 + 4, so a minimal
  order-5 *g* is exactly a 5×5 square of 25 runes (each row or column a 5-cycle)
  with 4 leftovers fixed — a keyed-square-plus-rotation, a classical construction.
  The plain Gematria-Primus-order square is *excluded* (doublet rate 0.036–0.061
  across the four rotations, ~6–10× the observed 0.0063), so if it is a grid it is
  keyed. And the GP-order leftovers AE/Y/IA/EA are low-frequency, matching the
  φ ≈ 0 measured below (Q1 consistency).

## Evidence against / complications

- ~~**Doublets are not phase-gated.**~~ **WITHDRAWN, September 2026 — the test has no
  power.** It asked whether doublets pile up at one *absolute* position mod 5
  ({0:21, 1:16, 2:11, 3:20, 4:18}, χ²(4) = 3.65) and read the flatness as a refutation.
  But under `quagmire-dodge.md` every dodge advances the clock an extra step, so the
  clock drifts off absolute position at about one step per 34 runes and the two
  decorrelate within a page. Simulating the gated model and applying its own test
  (`experiments/doublet_gaps_test_the_dodge.py`):

  | | doublets | χ²(4) |
  |---|---|---|
  | the body | 63 | 4.06 |
  | quagmire-dodge, one zero offset, 40 seeds | 67 | 3.45 ± 3.09 |

  P(χ² ≥ the body's | the gated model) = 0.30. The corpus is an ordinary draw from the
  mechanism this entry used it to reject, so the entry established nothing either way.

  **Replaced by a test that does have power** — see below.
- **Phase gating is disfavoured by the doublet GAPS, at about 70:1.** Gating constrains
  the *clock* advance between consecutive surviving doublets to 0 mod 5; the clock
  advance is the rune gap plus the dodges in between, so short gaps carry the signature.
  It lands on residue 4, not 0, because a surviving doublet advances the clock twice at
  its own position. Aligning each corpus on its own modal residue (which flatters
  concentration, so it favours the gated model):

  | | profile of gaps ≤ 40 runes |
  |---|---|
  | quagmire-dodge, one zero offset | [0.62, 0.05, 0.02, 0.08, 0.24] |
  | probabilistic preventer | [0.35, 0.17, 0.17, 0.16, 0.15] |
  | **the body**, 12 short gaps | **[0.42, 0.25, 0.17, 0.00, 0.17]** |

  **The 71:1 first published here is withdrawn** — it pooled gaps of very different
  sizes, whose predicted residues differ enormously, into one histogram. Conditioned on
  gap size with the key phase marginalised (`doublet_gaps_conditioned.py`), the 63
  within-block doublets give log LR **+0.09** — nothing — and the 23 seam doublets give
  **+5.33, about 200:1** for the preventer. The split survives smoothing and survives
  matching the body's block structure, and both tests classify known corpora at 93-97%.

  So phase gating is still disfavoured, and on evidence rather than on a test that could
  not see it — but the evidence lives entirely in the seam doublets, and why it should
  not also show in the larger within-block set is unexplained.

- **The suppression is rune-flat.** It is carried by 28 of 29 runes roughly in
  proportion, not by the ≥4 fixed points that an order-5 *g* on 29 letters must
  have (29 = 5·5 + 4). So *g*'s fixed-point structure is invisible in the doublets.
- The within-word doublet start-phase looks concentrated at j = 0,1, but that is
  confounded by word length (short words over-weight low positions); it needs an
  opportunity-normalized test before it counts.
- **The fixed points carry negligible text mass.** An order-5 *g* on 29 letters
  fixes ≥4 runes, and their self-coincidence would surface at d2/d3 (where the
  cycle relation g²/g³ is undesigned ≈ chance). The d2 excess is ≈ 0 (z=+0.1) and
  disagrees with d3 (+0.0025, z=+0.9), so there is no fixed-point signature:
  φ = Σ_{Fix} f(x)² ≈ 0. That means *g*'s fixed points are **low-frequency**
  runes, not the high-frequency non-doublers first guessed. (It also means d4's
  elevation is g⁻¹ cycle structure, not fixed-point mass.)
- **d4/d6 asymmetry needs plaintext correlation.** Under independence d4 and d6
  both reduce to Σf(x)f(g^{±1}x), which are equal; observed 1.19× vs 0.71× differ,
  so within-word plaintext structure (long words) rides on top of the clean g^d
  algebra. The d1 suppression and d5 leak are solid; d4/d6 are not pure-g effects.
- **No natural keyword lands the 5×5 grid.** A grid+rotation *can* reach 0.0063,
  but only ~0.03% of arbitrary grids do; and across 5,777 keyword-filled squares
  (common English + Cicada-thematic) *none* reach it — closest "meaning" 0.0065,
  and thematic words are far off (KOAN 0.0138, PRIMES 0.0199). So the keyed-square
  reading is viable but unidentified: if it is a grid, the key is not a common or
  thematic word. Redoing the hunt against Cicada's own runeglish (solved pages +
  register vocab) rather than the English lexicon does *not* change this — thematic
  keys stay at 0.013–0.026 (KOAN 0.013, PRIMES 0.021, TOTIENT 0.026); the only
  words that dip near target are unrelated English ones exploiting the sparse
  register table's zero cells (291/841 populated), i.e. artifact. So the keyed-square
  + single-rotation realization is looking unlikely; the order-5-walk picture is
  untouched, but this particular *g* construction is not supported.
- **"5.19 × 5 = 26" is a coincidence, not support.** There is no 26 in a 29-rune
  system, and the rune-flat suppression rules out a 26-scrambled + 3-special split.

## Predictions

- A concrete order-5 walk must reproduce, from **one** *g*: the d5 leak at ~0.54
  duty cycle **and** a ~5× doublet suppression that is flat across runes and flat
  across absolute phase. No such construction is demonstrated yet — building one
  (or proving none exists) is the test.
- If the linkage holds but is not phase-gated, the suppression is set by some
  other invariant of *g*'s cycle structure; that invariant is the thing to find.

## Scripts

- `experiments/doublet_period5_linkage.py` — plaintext-vs-ciphertext doublet
  rate, per-rune spread, and the phase-gating χ².
- `experiments/doublet_design_intensity.py` — the doublet rate against the random
  (and cycle-type 5⁵·1⁴) permutation distribution: *g* is 2.4σ below rule-random.
- `experiments/keyed_square_doublet.py` — the "keyed 5×5 square + rotation"
  reading of *g*: plain GP square excluded, random grids, keyword squares.
- `experiments/order5_permutation_search.py` — direct QAP search of the order-5
  permutation space: the doublet floor is ~0.0001, so 0.0063 is not minimised.
- `experiments/within_word_period_leak.py` — the d1–d6 profile and the d5 duty cycle.

## Related

- [doublet-suppression-requires-design.md](doublet-suppression-requires-design.md),
  [doublet-suppression.md](doublet-suppression.md) — why sub-chance doublets need design.
- [d5-partial-alphabet-leak.md](d5-partial-alphabet-leak.md),
  [within-word-repeated-rune-structure.md](within-word-repeated-rune-structure.md) — the d5 side.
- [position-within-word.md](position-within-word.md) — the mixed-alphabet walk model this would sit in.

## Verdict

Open, but sharper. The walk family fits the joint constraint better than any
tableau: the d1–d6 profile follows one *g*'s powers (d1/d6 = g¹ suppressed, d4 =
g⁻¹ elevated, d5 = identity leak), and *g* has low-frequency fixed points (φ ≈ 0).
On the suppression itself the search converged to a clear statement: *g* is
deliberately below chance (5.5×) but ~66× above the achievable doublet floor, so
doublet-minimisation is **not** its objective — 0.0063 is a byproduct of the rule
that fixed *g*. The two concrete realisations tried are out: phase-gating is
refuted, and no keyed 5×5 square (single rotation, any plausible key, lexicon or
register bigrams) reproduces it. What remains is to find the actual rule for *g*
that yields a rune-flat, phase-flat suppression at exactly this level alongside
the d5 leak.
