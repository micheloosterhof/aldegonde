---
type: hypothesis
---
# The Cipher: A Length-Clocked Progressive Substitution (g per letter, σ per space)

## Claim

The unsolved Liber Primus ciphertext (sections 0-9 of `data/page0-58.txt`) is a
**progressive polyalphabetic substitution with a small fixed key**, not a
per-word one-time pad. The alphabet advances by a fixed **order-5 mixed
permutation `g`** on every letter, and by a second fixed **mixed permutation
`σ`** at every word boundary. Per word `w`, at within-word position `j`:

```
c[j] = base_w( g^(j mod 5)( p[j] ) )
base_{w+1} = base_w ∘ g^((L_w − 1) mod 5) ∘ σ      (L_w = length of word w)
```

The sequence of per-word bases is generated **deterministically** from the key
`(base_0, g, σ)` and the **public word-length sequence** — the word lengths are
visible in the ciphertext, so they are not secret. Total key: two mixed
29-permutations (one of order 5), **fixed, ~200 bits, not growing with the
text.** This is the load-bearing correction to the earlier `free base →
unbreakable` reading: the base is a keyed generator, so the cipher is breakable
in principle.

## Status

**Status**: plausible (comprehensive statistical fit; NOT confirmed by
decryption)

The model reproduces the base fingerprint (flat unigrams, doublet
suppression, no periodicity) and the d1/d5/d6 profile, and survives the null
battery (below). Two measured anomalies remain **unexplained by the walk**:
the cross-word d4 frame face and the rune-S concentration of the echo (see
"Evidence against / open"). It has **not** been verified by producing
plaintext — the two mixed permutations have not been recovered. Confidence
is high on the *shape* (period-5 mixed substitution + per-word mixed step,
small fixed key), lower on details flagged under "open".

## Mechanism

Two independent "clocks", forced to be independent (see "single permutation
refuted"):

- **`g` — the letter step.** Order 5 (`g⁵ = id`), a rich mixed permutation
  (~five 5-cycles + fixed points), tuned **rare-diagonal**: `g(y)` is a rune
  that rarely precedes `y` in plaintext, so the within-word doublet
  (`c[i]=c[i-1] ⟺ p[i-1]=g(p[i])`) is held to 0.0063. `g⁵=id` makes positions
  5 apart share the alphabet → the d5 echo. Non-arithmetic: GF(29)* has order
  28 and 5∤28, so no shift/multiply/affine map has order 5.
  **A tuned-diagonal-free reformulation is refuted** — advance-4/hold-1
  (`g4⁴=id`), where the hold exposes 1/5 of plaintext doublets, predicted
  the doublet rate parameter-free but is DISPROVED by the doublet
  position-profile test (July 2026): the doublets are positionally flat,
  not plaintext-double-shaped. The diagonal is genuinely tuned, and the
  profile adds a key constraint: the diagonal bigram class {(g(y), y)}
  must itself be positionally near-baseline in plaintext. See
  `stay-slot-hold.md`, `experiments/doublet_position_profile.py`.
- **`σ` — the space step.** A second mixed permutation **outside ⟨g⟩** (not a
  power of `g`), tuned rare-diagonal so the seam doublet is suppressed to
  0.0079. Being outside ⟨g⟩ is what breaks the walk out of the 5-alphabet
  cyclic cage and gives flat unigrams + aperiodicity. This is now
  quantitative (`sigma-power-step.md`): σ = g^k is disproved for every k
  (identity-census collapse, ~2,500 predicted identical cipher words vs 17
  observed; DJU-BEI arithmetic forbids k ≠ 1 and periodicity kills k = 1),
  near-powers fail too, ⟨g,σ⟩ must reach N ≳ 600 bases, and the seam
  algebra isolates σ exactly: a cross-word doublet ⟺ p_last = σ(p_first),
  the `g` and length factors cancelling.

The `g^((L−1) mod 5)` factor in the transition completes the period-5 cycle at
the boundary, so the letter-clock effectively runs continuously across the
space; that is why doublet suppression is boundary-blind. Note the
period-5-vs-continuous framing is a **reparametrization** (fold `g^(word_start
mod 5)` into the base), so "does the phase reset per word?" is not observable.

## Evidence for

Clean corpus: sections 0-9, 12,956 runes, words tokenized on `- . & %`; `/` and
newlines are line wraps (words flow across them).

- **Flat unigrams (IoC 1.00).** The non-abelian walk ⟨g,σ⟩ visits many
  alphabets → uniform marginal.
- **Doublet suppression, boundary-blind.** Within-word 0.0063, seam 0.0079 (not
  significantly different, z=+0.87). Plaintext d1 is itself flat (real prose
  IoC ~1.0), so the ~5× suppression is entirely cipher-induced — the g/σ
  rare-diagonals. It is sub-maximal (an order-5 g could reach ~0), i.e. a
  "mildly rare" wiring.
- **Period-5 confirmed twice.** d5 echo (elevated coincidence, IoC 1.43,
  +3.7σ above flat) AND d6 suppression (the phase-1 image of d1: `g⁶ = g¹`
  under period 5; permutation null p=0.016). d6 pins the period at exactly 5,
  independent of the fragile d10 (2/88 pairs). The d6 deficit is moreover
  a STRUCTURAL discriminator (July 2026, `mixed-cycle-progression.md`):
  no "returned-fraction" mechanism — mixed cycle lengths in g, the one
  classical construction whose correlation rises with distance — can push
  a cell BELOW background; only an inherited tuned relation (g⁶ = g)
  does. The sub-background d6 is positive evidence for order-5 with a
  tuned diagonal, not merely a consistency check.
- **Empty d2/d3/d4 (~chance).** `g²/g³/g⁴` diagonals sit at chance.
- **No periodicity.** No Kasiski, no periodic-IoC (periods ≤600), no period in
  absolute rune position (k≤40) or word index (k≤49, incl divisors of 1449).
  Consistent: the walk is clocked by aperiodic word lengths.
- **Not a rotor machine.** A physical wheel stepping 1/letter reuses its
  alphabet at the wheel period, but absolute-position coincidence at d=29 is
  flat (IoC 1.01) and d=20–45 averages 1.00 — no wheel-period echo. And period-5
  is impossible for a 29-symbol wheel (period is 29 for any step, 29 prime), so
  the d5 echo needs a *designed* order-5 permutation, not a rotation. Plus the
  phase resets at word boundaries, which continuous machine stepping cannot do.
  Enigma/Hebern out; Hagelin/Lorenz are additive (killed by the algebra battery).
  The model is rotor-*structured* (order-5 letter rotor + per-space rotor) but
  not a historical machine — a pencil-and-paper progressive substitution.
- **No algebraic structure anywhere.** Delta, sum, ratio, product, and all 28
  affine multipliers — within-word AND across the seam — are null beyond the
  coincidence. So `g` and `σ` are general mixed permutations, not
  affine/multiplicative/Beaufort. (Two scan "hits", d6-m27 and d5-per-word,
  survived permutation nulls but failed split-half → overfit, not signal.)
  **Confirmed constructively by diagonal floors** (July 2026,
  `experiments/sigma_algebraic_floor.py`): the observed doublet rates ARE
  the two diagonals, so each arithmetic family can be excluded by
  computing its minimum achievable diagonal on the relevant plaintext
  table. For `σ` on the cross-word (final × initial) table every family
  floors above the observed 0.0079 — additive 0.0207, Beaufort 0.0211,
  multiplicative and affine 0.0122, inverse `a/x+b` 0.0162 — against an
  unconstrained-permutation floor of 0.0048. For `g` on the within-word
  table the same holds (affine floor 0.0101 vs observed 0.0063), which
  is an independent second reason beyond the order argument. One family
  needed the order argument after all: the inverse maps DO reach the
  diagonal (best 0.0038) but the family contains **no element of order
  5** (orders present: 2, 6, 12, 20, 27, 28, 29, 30, 42, 90, 182, 210),
  so it cannot supply `g`. Both steps are also only *mildly* rare —
  0.0063 and 0.0079 sit above their achievable floors, not at them.
- **Not ciphertext-autokey.** Grouping each rune by its previous ciphertext rune
  (lag 1, 2, 5) gives within-group IoC 1.02/1.00/1.00 — flat, not the ~1.8 that a
  ciphertext-driven alphabet would leak (`autokey_test.py`). So the alphabet is
  not selected by the public ciphertext; the keystream is not public. (A
  plaintext-autokey with a hidden keystream is not excluded but gives no
  shortcut, and a plaintext-driven hold would be a small rule, not a keystream.)
- **No number-sequence running key.** 16 number-theoretic sequences (prime,
  totient, totient-summatory, Fibonacci, Lucas, tribonacci, triangular, square,
  cube, Möbius, divisor-sum, prime-gap, prime-count, index) × whole-text /
  per-word / per-section framings × Vigenère/Beaufort/add leave IoC flat to
  0.001 (`number_sequence_keys.py`). A pure-shift number key is excluded; this
  only tests *pure* shifts, so number theory can still live inside the mixed
  `g`/`σ` construction (e.g. a prime/totient-ordered grid) or the per-word step
  schedule — blind to ciphertext-only tests, a seed for the attack not a datum.
- **Single permutation refuted.** Doublet suppression needs a *rich* order-5
  `g` (~25 runes moving); flatness needs a *large-order* generator; one
  permutation on 29 runes can't be both. Forces two independent generators.
- **Base re-key is thorough.** No cross-word d5 echo at any (first-word-length,
  distance) cell; first letters of adjacent words are independent; the word
  boundary is a hard cut of the alphabet.
- **Long words add nothing but the echo** (`long-word-structure.md`). The
  1,124 words of length ≥ 5 are the only ones exercising `g³`, `g⁴` and
  the `g⁵ = id` return internally, so a length-dependent or
  state-accumulating mechanism would show there first. Measured against
  doublet-aware surrogates: doublet suppression is flat across length
  classes (0.0066 / 0.0055 / 0.0069), cross-word collisions among long
  words sit at chance through 4-rune prefixes and 4-rune substrings,
  positional rune distributions are uniform, and the in-word repeated-
  bigram excess decomposes ENTIRELY into separation 5 (z = +6.8 there,
  z = +0.6 excluding it). Nothing accumulates inside a word beyond the
  period-5 relation.
- **The first-order channel batteries verify the model's structural
  predictions at full power (July 2026).** The model makes three sharp
  claims about pairwise structure, and all three are confirmed:
  (a) WITHIN WORDS only distance matters — c[j] = base_w(g^(j mod 5)(p[j]))
  forces every position-pair relation to depend on k−j alone, and the
  full (j,k) grid is translation-invariant at every distance with no
  conditional structure (`word-position-pairs.md`); (b) at the SEAM the
  boundary factors cancel, so the previous word's last rune constrains
  the next word only through the σ-diagonal at reach 1 — measured: the
  suppression is confined to reach 1, reaches 2-6 are at chance, the
  diagonal rate is independent of word length, and the conditional
  channel is empty at depth 1 and 2 (`seam-channel-clean.md`); (c) the
  full ADJACENCY matrix is flat in every decomposition — off-diagonal,
  direction, within-vs-cross-word (identical distributions), and
  within-word phase (`bigram-ioc.md`, full battery). Every first-order
  channel of the corpus is closed, and each closure is a prediction of
  this model rather than a retrofit.
- **DJU-BEI (`ᛞᛄᚢ·ᛒᛖᛁ`).** A 6-rune, two-word (3+3) refrain that *closes*
  section 9 and recurs mid-section-6. Same ciphertext ⟹ `base_1477 =
  base_2926` — a state return of the deterministic walk. Both words length 3,
  so the step (`g²σ`) matched and the bases stayed synced across both words —
  which a random per-word key could not produce. Yields a key constraint:
  `Σ(L−1)=4946 ≡ 1 (mod 5)` over the interval, so `[g] = −1449·[σ]` in the
  abelianization of ⟨g,σ⟩.
  **What this constraint does and does not pin.** The two "5"s in this
  model are independent, and only one of them is at work here. The
  within-word phase `j mod 5` never reaches 5 in a short word — DJU and
  BEI are 3 runes each, so their ciphertext exercises only `g⁰, g¹, g²`
  and says nothing directly about `g³` or `g⁴`. The mod-5 arithmetic in
  the constraint comes instead from `g⁵ = id` making exponents matter
  only mod 5, applied to the exponent the BASE schedule accumulates
  across 1,449 word boundaries. So DJU-BEI constrains the base schedule
  (and hence a relation between g and σ), not g's internal structure.
  Identifiability gradient generally: `g¹` is exercised by 96.6% of
  words, `g²` by 80.7%, `g³` by 55.9%, `g⁴` by 38.4%, and the `g⁵ = id`
  echo only by the 27.5% of words with length ≥ 6 (806 words, 2,073
  pairs) — the higher powers rest on progressively less data.

## Evidence against / open

- **Partial-vs-full d5 leak is underpowered.** IoC 1.43 vs full-leak ~1.60;
  point estimate 72% same-alphabet, but the bootstrap CI [1.15,1.72] contains
  full leak. Position decomposition (`within_word_position_decomposition.py`)
  shows the echo is **flat over absolute position** (no intra-word drift), so
  the partial leak is *not* drift — the base is word-locked and the partiality
  is uniform (σ knocking the leak down by a constant factor). See
  `d5-partial-alphabet-leak.md`.
- **The d4/d6 asymmetry and the partial echo (July 2026).** Under g⁵ = id,
  g⁴ = g⁻¹ and g⁶ = g share the same leading-order diagonal algebra — so
  this model predicts d4 ≈ d6; observed is a ~2.7σ split in opposite
  directions (d4 = 0.0410 up, d6 = 0.0245 down). A language-orientation
  rescue tested negative. A cycle-census resolution was explored
  exhaustively (`mixed-cycle-progression.md`: scan of all 4,565
  partitions + full-battery simulation) and, after correcting two
  calibration flaws in the first pass, DID NOT resolve it: census
  rankings are calibration-fragile, the partial-echo evidence reverts to
  undecidable (corrected φ5 = 0.85 ± 0.26), and at realistic tuning
  depth no census — mixed or pure — reproduces the full d6 depth.
  Standing, calibration-free: **d6 is suppressed (−2.3σ,
  permutation-verified p = 0.016) and d4 leans high (+1.85σ,
  uncorrected), a d4−d6 split of ~2.7σ where this model predicts
  equality** — and neither cell has a mechanism. If the real g's
  d6-form is deliberately suppressed beyond what adjacent-diagonal
  tuning delivers, that is one more designed constraint on the key
  (alongside the g²-diagonal-near-background requirement the
  simulations surfaced); otherwise these are the model's open cells.
- **Order-5-g vs stay-slot: SEPARATED (July 2026).** Direct simulation
  on real runeglish words (`mechanism_discriminator.py`) could not separate
  them — both reproduce the d5 echo and d1≠d6, and the d1..d6 fit winner
  flips with the g-tuning seed. The doublet position-profile test now
  does: stay-slot forces the doublets to be plaintext double letters
  (start-forbidden, end-heavy), and the observed doublets are positionally
  flat — stay-slot disproved, tuned order-5-g survives with the new
  diagonal-class constraint above. What's real beyond period-5 is the
  **damped rising shoulder** — LP's d2→d5 tracks a half-damped copy of the
  plaintext's own within-word profile with extra phase-1 suppression, i.e. a
  partial plaintext leak under the period-5 envelope. See
  `d5-partial-alphabet-leak.md`.
- **Continuous-vs-per-section walk: weak.** Page-seam doublets 0/47 favour
  "continuous" ~3.4:1; DJU-BEI's differing section-offsets argue against
  per-section reset. But only 9 section boundaries — not provable.
- **The d4 frame face is not produced by the walk.** Of the lag-5 paired
  matches, the d1 face (`XY···XY`) is plaintext morphology passing through
  the `g⁵=id` echo — accounted for. The d4 face ((1st,5th)-of-5 frame,
  largely cross-word) is BELOW chance in real runeglish plaintext, so the
  echo cannot pass it through. The July 2026 anatomy
  (`experiments/d4_frame_anatomy.py`) found no walk-compatible structure
  in it either (most legs cross one boundary, where alphabet coincidence
  is impossible given σ ∉ ⟨g⟩; no σ-relation geometry cell enriched), so
  it stands as a count excess compatible with scan noise rather than
  as evidence against the model. See `lag5-digraph-structure.md`.
- **The rune-S echo — resolved, no tension (July 2026).** 11 of the 102
  within-word d5 pairs echo the single rune S (p=2.4e-6 against a
  frequency-weighted null). That null is wrong for this model: under the
  walk the echoed rune is base-scrambled per word, identities are
  near-uniform and cluster by word, and simulation gives
  P(max ≥ 11) = 0.08-0.15 (`experiments/rune_s_walk_test.py`) — a
  1-in-12 event, not a strike. The concentration still refutes
  identity-preserving mechanisms; the fixed-channel variant is excluded
  by unigram arithmetic. See `rune-s-lag5-echo.md`.
- **Keyword-grid keys are excluded.** `experiments/enumerate_keys.py` drove
  keyword-grid `g` × keyword `σ` through the DJU-BEI/diagonal cascade
  (`experiments/walk_verifier.py`): 0/480 parity-valid pairs give a state
  return, and the best keyword-grid `g` diagonal in that scan was 0.023 vs
  the required 0.0063 — **the diagonal exclusion is RETRACTED** (July 2026,
  `experiments/g_construction_survey.py`): the scan fixed the four fixed
  runes as the last four of the keyword order and rotated every column by
  one; freeing those two parameters lets every ordering and fill tested
  reach the required band (~2x10⁵ in-band candidates from a single
  keyword), so the state-return result must be re-run over the corrected
  family. The retraction is of the letter, not the spirit: a grid-derived
  `g` has the diagonal distribution of a random order-5 permutation
  (mean 0.0345 vs 0.0346; 0.17% vs 0.07% at or below 0.0063), so the
  construction supplies no low diagonal — the family merely contains
  in-band members at a ~1-in-600 rate because it is large. **Open problem, now inverted**: the structured family is not
  too poor to supply `g`, it is too RICH to enumerate — ~10⁹-10¹⁰ in-band
  `g` candidates across plausible keywords and fills, before `σ`, which
  has no construction proposal and cannot be hill-climbed. The diagonal
  band is too weak a filter on its own; progress needs the constraints
  applied JOINTLY (g² near background, positional profile, σ's
  cross-word diagonal, parity, DJU-BEI) or a principle that pins the
  fixed-rune choice and the column rotations. See `g-from-5x5-grid.md`.
- **Is `g` provably FIXED? No — but the alternatives cost key material
  without buying anything (July 2026).** What the ciphertext actually
  requires is local: the composition of the five steps spanning positions
  j and j+5 *inside one word* must be the identity, and the step relation
  must be rare-diagonal. Nothing tests whether the same `g` is in force
  from word to word — the echo is within-word, the seam algebra cancels
  `g` entirely (a seam doublet is `p_last = σ(p_first)`, no `g` in it),
  and the base schedule is unobservable. A per-word family `g_w` would
  be invisible to every battery run here, PROVIDED each `g_w` has order 5
  and a rare diagonal. What excludes it is design economy rather than
  statistics: selecting from that family per word is a schedule, i.e. key
  material growing with the text, which slides the cipher toward an OTP
  and destroys the small-fixed-key property that makes it readable at all.
  The natural middle case — a CYCLIC SCHEDULE of five distinct steps
  `a₁…a₅` with `a₁a₂a₃a₄a₅ = id`, applied in rotation (fixed `g` is the
  special case `a_i = g`) — preserves the echo exactly at every phase
  (cyclic rotations of an identity product are conjugates of the
  identity), but simulation shows it neither helps nor is free: the d1-d8
  profile matches the fixed-`g` model (d4 0.034 vs LP 0.041, d6 0.031 vs
  LP 0.025 — the same two failures), and the product constraint leaves
  only FOUR steps free, forcing the fifth as the inverse of the others'
  product with an untuned diagonal (~0.013 in the run) that drags the
  doublet rate up. Fixed `g` tunes one diagonal once and uses it five
  times. So `g` is fixed by parsimony and tuning economy, not by proof.
- **`σ`: one or a small keyed set?** Seam suppression proves the space step is
  a rare-diagonal permutation (not a random re-key) but does not prove there is
  only *one* `σ`. A small keyed family fits equally; the fully-deterministic
  single-`σ` version is the simplest, not the confirmed, form.
- **Not confirmed by decryption.** All of the above is statistical shape.

## Predictions

- The key `(base_0, g, σ)` is small and fixed; decryption is a deterministic
  function of it and the observable word lengths. A **contiguous crib** of a
  few words would pin `g` and `σ` and then propagate to the whole corpus —
  unlike a free-base model, where a crib dies at its own word.
- Any candidate key must satisfy the DJU-BEI abelianization constraint above.
- A single guessed word (e.g. DJU-BEI = a [3,3] phrase such as "OUR OWN") is
  **not** verifiable — 6 runes under two unknown bases + g is underdetermined.
- **The 2-rune words are the sharpest available key discriminator
  (July 2026).** In runeglish `THE` is exactly two runes (`ᚦᛖ`), and
  2-rune words are a dense, highly concentrated class: in the register
  corpus they are 22.8% of all tokens and their content is dominated by
  a handful of function words — THE 16%, TO 15%, OF 13%, IN 7%, IT 5%,
  HE 5%, BE 4%, AS 4% (top eight = 69%). The LP has **465** 2-rune
  words, so an English-like plaintext puts roughly **75-108 instances of
  THE** among them (75 if the 2-rune class has register composition, 108
  if THE keeps its 3.7% token rate). A 2-rune word needs only `base_w`
  and `g` to decrypt (`p₀ = base_w⁻¹(c₀)`, `p₁ = g⁻¹(base_w⁻¹(c₁))`), so
  every candidate key can be scored by decrypting all 465 and counting
  `ᚦᛖ`: **~75-108 hits for a correct key against 465/812 ≈ 0.6 by
  chance** — a discriminator of order 100x, far sharper than quadgram
  fitness. For hill-climbing, the count alone is too peaked to give a
  gradient; the usable objective is the log-likelihood of the decrypted
  2-rune words against the whole register distribution above, which
  awards partial credit for TO, OF, IN … while the key is still wrong.
  Caveat and cross-check: the LP's 2-rune share is 15.9%, well below the
  register's 22.8% — the documented short-word deficit
  (`word-length-keystream-and-boundaries.md`) — so either the plaintext
  register is unusually short-word-poor, or the boundary question bears
  on it; the expected-hit range above already spans that uncertainty.
  **Validated on planted keys** (`experiments/two_rune_gradient.py`):
  the objective recovers `base_0` exactly and instantly once `g` and `σ`
  are known, but the landscape over `(g, σ)` is a delta function — one
  transposition in `σ` scores like a random key. So this is a verifier,
  not a search gradient, and `base_0` should be treated as free rather
  than as part of the key search. See `no-known-plaintext-foothold.md`.

## Scripts

- `experiments/phase_absorbing_walk.py` — the model: `base_{w+1} = base_w ∘
  g^((len−1) mod5) ∘ σ`, hits the full battery.
- `experiments/final_orbit_walk.py` — rate-targeted variant.
- `experiments/within_word_phase_profile.py` — d1-d10 permutation null (d5
  echo p=0.001, d6 suppression p=0.016).
- `experiments/d5_partial_leak.py` — the partial-leak measurement and its
  underpowered CI.
- `experiments/stay_slot_cipher.py` — plaintext generator, cipher batteries,
  permutation tooling.

## Related

- `per-word-related-alphabets.md` — the predecessor model; this note supersedes
  its "free per-word base" pessimism with the length-clocked deterministic walk.
- `sigma-power-step.md` — σ is not a power (or near-power) of g; the
  surviving σ constraints (seam diagonal, parity, group-size floor).
- `d5-partial-alphabet-leak.md`, `within-word-d5-coincidence.md`,
  `rune-s-lag5-echo.md` — the d5/d6 structure.
- `repeated-phrase-dju-bei.md`, `cryptodiagnostics-page0-58.md` — DJU-BEI and
  the full diagnostic battery.

## Verdict

The mechanism is characterized: a **length-clocked progressive substitution** —
step `g` (order-5 mixed) per letter, step `σ` (mixed, outside ⟨g⟩) per space,
base = the running product clocked by the public word lengths. Both steps are
non-arithmetic mixed permutations, which would be a first for Cicada and
explains why value-based attacks fail. The key is **small and fixed**, so the
cipher is breakable in principle — but the barrier is recovering two mixed
29-permutations, against which every statistical and algebraic shortcut
tried so far is null. The model does not account for the d4 frame face or
the rune-S echo; either could falsify or refine it. The realistic paths to
plaintext are a length-clocked hillclimb on `(base_0, g, σ)` or a
contiguous crib — noting keyword-grid key fills are already excluded — and
a short guessed phrase alone cannot verify. Everything here is statistical
shape, not a confirmed decryption.
