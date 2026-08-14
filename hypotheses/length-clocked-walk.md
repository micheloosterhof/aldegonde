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
battery (below). As of 2026-08-14 one fitted key reproduces the ENTIRE hard
profile in corpus-sized simulation — every cell within noise
(`experiments/walk_full_profile.py`, "Full-profile simulation" under
Evidence for). Two measured anomalies remain **unexplained by the walk**:
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
  **Nor can the period-5 step be a 5-letter VIGENERE** — the obvious
  simplest reading, and it fails on the doublet rate rather than on
  order (July 2026, `experiments/sigma_algebraic_floor.py`). Under a
  shift schedule the alphabet at position j is `base_w ∘ (add s_j)` with
  s periodic mod 5, so a ciphertext doublet occurs exactly when the
  plaintext adjacent delta equals one phase-specific value. The rarest
  adjacent delta in runeglish is **0.0119** (delta = 18), the best
  5-shift schedule closing to identity (Σs ≡ 0 mod 29, phase-weighted by
  the real adjacency counts) gives **0.0135**, and even granting all
  five phases the single rarest delta the floor is 0.0119 — against an
  observed 0.0063, i.e. **1.9-2.2x too high**. A shift can only dodge
  doublets by exploiting a rare plaintext delta and English has none
  rare enough; a mixed permutation dodges per-rune, routing each image
  to its own rare partner, which is exactly why the cipher needs mixed
  alphabets rather than a keyword. **A MIXED-alphabet (Quagmire)
  Vigenere is a different matter and is NOT excluded**: conjugated
  shifts `K∘(add δ)∘K⁻¹` put the doublet condition on deltas of the
  transformed plaintext `K⁻¹(p)`, which a free `K` reshapes — jointly
  optimising `K` and five offsets reaches 0.0017. The 12-keyword sample
  that once closed the keyword version was superseded by the
  full-dictionary exhaustion: **12,064 keyword alphabets clear the
  within-word diagonal** (best 0.0010), so the enumerable-key version
  is LIVE — see `mixed-alphabet-vigenere.md`. What stands of the tuning
  rule is narrower: the two exhaustive floor computations (plain
  shifts, the arithmetic families) show the relation cannot be
  arithmetic; a merely-mixed alphabet is not excluded — ~1.5% of
  random mixed alphabets clear the target — it is merely atypical.
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

**No closed form for the base (probably).** Four words in, the base is
the raw alternating word `base_0 g^{a₀} σ g^{a₁} σ g^{a₂} σ g^{a₃} σ`,
which does not simplify. It would if σ normalised ⟨g⟩ (σgσ⁻¹ = g^r),
giving `base_w = base_0 ∘ g^(Σ aᵢ rⁱ mod 5) ∘ σ^w` — but that caps the
state at 5·ord(σ), and exhaustive enumeration of the normalizer bounds
that at 300 bases for a twisted σ (comfortably under the ~600 the
identity census wants) and 500 for a commuting one (marginal: the
census figure is itself a 2σ bound, and at 3σ it falls to ~490). So the
twisted cases are excluded and the commuting case is disfavoured rather
than dead. See `sigma-power-step.md`.

The `g^((L−1) mod 5)` factor in the transition completes the period-5 cycle at
the boundary, so the letter-clock effectively runs continuously across the
space. Note the period-5-vs-continuous framing is a **reparametrization** (fold
`g^(word_start mod 5)` into the base), so "does the phase reset per word?" is
not observable.

**Phase continuity is NOT why doublet suppression is boundary-blind** (August
2026). That explanation was stated here and is wrong on the model's own algebra:
the seam doublet condition is `p_last = σ(p_first)` with **no `g` in it at all**
(the `g^e` and `base_w` factors cancel — see the σ bullet above, verified
exactly against a planted key, 2927/2927, alongside the within-word form
10028/10028). So the two rates are diagonals of *different permutations* on
*different plaintext tables*: `g` on the within-word adjacent table, σ on the
(final × initial) table. The model does not force them to agree, and their
agreement to z = −0.92 is a consequence of both steps having been tuned
rare-diagonal, not of the letter-clock running through the space. This does not
damage the model — both diagonals sit well above their floors (0.0063 vs 0.0000
for `g`; 0.0079 vs 0.0048 for σ), so "both mildly rare" is an unremarkable
design choice — but boundary-blindness should be read as *compatible with* the
walk rather than as *evidence for* it, since the walk makes no prediction here.

## Evidence for

Clean corpus: sections 0-9, 12,956 runes, words tokenized on `- . & %`; `/` and
newlines are line wraps (words flow across them).

- **Full-profile corpus-sized simulation (2026-08-14,
  `experiments/walk_full_profile.py`).** One (g, σ₁, σ₂) fitted at
  table level — g to the observed d1-d4+d6 on consecutive-prose pair
  tables (inverse-variance weighted), σ to the seam 0.0079 on the
  cross-word table — then run through `encipher()` over 100 corpora of
  2,928 consecutive prose words. Every hard cell lands within noise of
  the LP (LP error carried): d1w −0.06, seam −0.00, d2w +0.00, d3w
  −0.04, d4w −0.17, d5x −0.13, d6w +0.06; d5w −0.82 is the known
  untuned register residual (g⁵=id fixes that cell at the plaintext's
  own lag-5 rate, 0.0569 sim vs 0.0492 LP). This upgrades
  `d4_d6_prediction.py`'s table-level reachability to a full generative
  run. The REGISTER is load-bearing in both directions: a Markov-2
  trigram generator cannot reach d4/d6 (fit floors 0.0368/0.0319 vs
  0.0410/0.0245), and independently-drawn dictionary words cannot reach
  the seam (product cross table, σ floor ~0.0154 vs 0.0079) — only
  running text supplies both. Soft observables stay untargeted as
  documented (sim min doublet gap 4 vs LP 6; delta chi2 30.4 vs 41.4).
  Same caveat as the table-level result: reachability is weak evidence
  FOR; the force is that no profile cell is evidence against. The run
  is self-validating (round-trip decipher; within/seam match ⟺
  plaintext algebra checked exactly) and writes
  `experiments/walk_reference.json` — key + plaintext/ciphertext pair,
  the standing validation target for crib propagation and key-search
  machinery.
- **Flat unigrams (IoC 1.00).** The non-abelian walk ⟨g,σ⟩ visits many
  alphabets → uniform marginal.
- **Doublet suppression** (but NOT its boundary-blindness — see Mechanism).
  Within-word 0.0063, seam 0.0079. Plaintext d1 is itself flat (real prose
  IoC ~1.0), so the ~5× suppression is entirely cipher-induced — the g/σ
  rare-diagonals. It is sub-maximal (an order-5 g could reach ~0), i.e. a
  "mildly rare" wiring. That the two rates *match* (z = −0.92) is not predicted
  by the model and is not evidence for it: they are diagonals of two unrelated
  permutations on two different tables.
- **Period-5 confirmed twice.** d5 echo (elevated coincidence, IoC 1.43,
  +3.7σ above flat) AND d6 suppression (the phase-1 image of d1: `g⁶ = g¹`
  under period 5; permutation null p=0.016). d6 pins the period at exactly 5,
  independent of the fragile d10 (2/88 pairs). The d6 deficit is moreover
  a STRUCTURAL discriminator (July 2026, `mixed-cycle-progression.md`):
  no "returned-fraction" mechanism — mixed cycle lengths in g, the one
  classical construction whose correlation rises with distance — can push
  a cell BELOW background; only an inherited tuned relation (g⁶ = g)
  does. So d6 is a real structural exclusion of the entire
  returned-fraction family — but NOT a confirmation of this one: at the
  LP-implied tuning depth no model reproduces its *depth*, pure order-5
  included (simulated d6 = 0.0397 vs LP 0.0245, `census_corrected.py`).
  It discriminates against a family without selecting a member.
- **d2/d3 at chance; d4 is NOT.** `g²/g³` diagonals sit at chance. d4
  was originally binned with them but is +1.85σ high and is one of the
  model's two open cells (see Evidence against).
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
  **Refinement (July 2026) — a TWO-WHEEL device does work, provided the
  letter wheel has 5 positions, not 29.** The obstruction above is
  specific: anything built from rotations of 29-position wheels has
  period dividing 29 (prime), hence never 5. But nothing forbids a
  5-state letter wheel — five pre-wired alphabets `base ∘ g⁰…g⁴`
  selected in rotation, mechanically "a wheel with five turns". And the
  space step CAN be an ordinary rotating 29-position mixed disk:
  simulated with the real length sequence, a mixed-alphabet disk turned
  a fixed amount per word gives **2,928 distinct bases** (full
  diversity, far above the ~600 the census wants), has order 29, and
  does not normalise ⟨g⟩ (even parity is automatic for a 29-cycle, so
  the once-cited parity condition constrains nothing here). So the architecture is buildable as *5-position letter selector +
  29-position space disk*, which is a considerably more concrete device
  than "two arbitrary mixed permutations".
  **And the wheels CAN be keyword-set.** The full-dictionary exhaustion
  (`mixed-alphabet-vigenere.md`) finds 12,064 keyword alphabets for the
  letter wheel inside the required diagonal band and ~130 keyword disks
  for the space wheel inside the seam rate's 95% CI — so the two-wheel
  device is compatible with a keyword key, the only enumerable
  formulation on the table. (Keywords are not special — they clear the
  band at the same rate random alphabets do — but the family is
  enumerable, which random permutations are not.)
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
- **The five adjacent relations must be IDENTICAL — a positive argument for one
  `g` over any schedule (August 2026, `experiments/five_relation_test.py`).** Any
  five-alphabet rotation has five adjacent relations `R_j = A_j⁻¹A_{j+1}`, and
  closure forces `R_0R_1R_2R_3R_4 = id`, leaving four tunable and the fifth forced
  as the inverse of the others' product — hence untuned, diagonal ≈ 1/29. That
  phase would carry a ~5× higher doublet rate. Measured by phase (position mod 5),
  the rates are 0.528 / 0.812 / 0.494 / 0.651 / 0.698%, equal at χ² = 2.59 on 4 df
  (p ≈ 0.63), and every placement of an untuned step is excluded — 30–118 doublets
  predicted against 6–22 observed, **z = −4.3 to −9.2**. So all five relations share
  one low diagonal, which is exactly what `A_j = base ∘ g^j` gives and what no
  multi-step schedule can. This generalises the repo's use of mod-5 uniformity,
  which previously excluded only schedules containing an identity step
  (`stay-slot-hold.md`); the argument covers any schedule whose relations differ.
- **A 5-ring cylinder explains `g`'s ORDER, and cannot supply σ (August 2026,
  Michel's proposal).** Read a Jefferson-style cylinder at a FIXED offset of one row,
  with consecutive rings related by `ρ_{j+1} = ρ_j g`. Then
  `c_j = ρ_j(p_j) = ρ_0 g^j(p_j)` — exactly the walk's form with `base = ρ_0` — and a
  doublet is exactly `p_j = g(p_{j+1})`. Crucially, if the cylinder closes after five
  rings then `ρ_5 = ρ_0` forces **`g⁵ = id`**: the order-5 property becomes a
  consequence of having five rings rather than an unexplained design choice, which is
  the best mechanical account of the period on offer. Three things it cannot do.
  Identical rings are impossible (every power of a 29-cycle has order 29, since 29 is
  prime). A VARYING offset breaks it: `R_j(k) = ρ_j^{-k}ρ_{j+1}^{k}` equals `g` only
  at k = 1 (checked: k = 2 gives order 105, k = 3 gives 26), so the five relations
  would differ and one phase would carry an untuned diagonal — excluded at z = −4.3 to
  −9.2 by the phase-flatness above. And cyclically shifting the ring order preserves
  all five relations but yields only 5 distinct bases against the ≥300 required. So
  the cylinder accounts for the letter step and stalls at σ, which is the same place
  every mechanical story stops (`key-local-channel-is-empty.md` §5).
- **Why no construction for `g` can help (August 2026).** Order 5 on 29 points
  forces cycle type 5⁵1⁴, and all such permutations are **conjugate**: `g = K σ₀ K⁻¹`
  for a canonical σ₀ and arbitrary `K`. So there is no algebraic subfamily to
  enumerate — every "construction" is a parameterisation of `K`, which is why
  keyword grids (`g-from-5x5-grid.md`) and the magic square
  (`magic-square-grid-key.md`) buy nothing. And no affine map qualifies at all,
  since 5 ∤ |AGL(1,29)| = 812. Five *does* divide |GF(29²)*| = 840, so an order-5
  multiplier exists on a DIGRAPH unit — disfavoured by flat parity at periods 2–6 —
  and |Z/31*| = 30 and |Z/11*| = 10, which need 31 symbols and a many-to-one map
  respectively.
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
  which a random per-word key could not produce. Formally
  `Σ(L−1)=4946 ≡ 1 (mod 5)` over the interval gives `[g] = −1449·[σ]` in the
  abelianization of ⟨g,σ⟩ — **but this is not a usable filter on concrete
  permutations.** It is a relation in the abelianization of the *free* group;
  the real ⟨g,σ⟩ is A₂₉/S₂₉ or a point stabilizer thereof, with |G/G′|
  measured at 1 or 2 across sampled order-5 `g` and both random and 29-cycle
  σ. It therefore collapses into the parity condition, and for a Quagmire σ
  (a 29-cycle, hence even) even that is automatic. See
  `mixed-alphabet-vigenere.md`. The relation retains force only where the
  group really is abelian — i.e. under the σ = g^k assumption of
  `sigma-power-step.md`, where it correctly forces k = 1. The testable
  content of DJU-BEI for a general key is the state return itself.
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

- **Partial-vs-full d5 leak: RESOLVED, and period-5 is now CONFIRMED (August
  2026, `experiments/period5_confirmation.py`).** Against real prose resampled to
  the LP's word-length histogram, d5 matches PLAINTEXT (4.92% vs 5.51%, z = −1.2)
  while d3 and d4 sit at CHANCE (3.70% and 4.10% against plaintext 5.30% and 5.38%,
  z = −5.9 and −3.7). That is the `g⁵ = id` signature: only distance 5 leaks
  directly. **One-alphabet-per-word is REFUTED** — it predicts plaintext-level
  coincidence at d3/d4 as well, and φ3 = 0.13 ± 0.14 sits 6.4σ below full leak
  (φ4 = 0.37 ± 0.20 is 1.9σ above chance, the known d4 lean, not clean) — so the order-5 step is measured, not merely
  plausible. The d3/d4 cells work as an internal reference for "scrambled", which is
  why this succeeds where the echo's magnitude alone is underpowered.
  **φ5 itself is NOT resolved**: the point estimate is 0.64–0.71 depending on the
  runeglish convention for the Ing rune (valued NG or ING, both legitimate),
  consistent with full leak at z = −1.2 to −1.8 but below it — the same standing as
  the 0.85 ± 0.26 below. An earlier version of this bullet claimed φ5 ≈ 1 by reading
  "within 1.2σ of plaintext" as an estimate rather than a consistency check.
- **Superseded — the underpowered version.** IoC 1.43 vs full-leak ~1.60;
  point estimate 72% same-alphabet, but the bootstrap CI [1.15,1.72] contains
  full leak. Position decomposition (`within_word_position_decomposition.py`)
  shows the echo is **flat over absolute position** (no intra-word drift), so
  the partial leak is *not* drift — the base is word-locked and the partiality
  is uniform (σ knocking the leak down by a constant factor). See
  `d5-partial-alphabet-leak.md`.
- **The d4/d6 asymmetry: CLOSED (August 2026), it was never an anomaly.**
  This model does **not** predict d4 ≈ d6. The old argument — g⁴ = g⁻¹ and
  g⁶ = g "share the same leading-order diagonal algebra" — is the
  independence approximation (rate depends only on the unigram
  distribution). The real rate is the g^d diagonal on the *distance-d
  within-word pair table*, and P₄ ≠ P₆. This is the identical error already
  retracted for d1 vs d6 in `d5-partial-alphabet-leak.md`; it survived at
  d4 vs d6 and drove a year of census work.

  Measured on real runeglish word pair-tables
  (`experiments/d4_d6_prediction.py`), an order-5 g fitted to d1..d4
  predicts **d4/d6 = 1.25 ± 0.18** (observed 1.67) and **d6 = 0.0333 ±
  0.0051** (observed 0.0245). Carrying the LP's binomial error — d6 is 31
  events — that is **z = +1.12 and +1.32**. Nothing.

  Stronger: fitted jointly to d1, d2, d3, d4 **and** d6, a single order-5 g
  reaches every cell (0.0064 / 0.0345 / 0.0369 / 0.0408 / 0.0247 against
  0.0064 / 0.0347 / 0.0370 / 0.0410 / 0.0245), stable across seeds. **The
  d6 depth is reachable.** The earlier "no census reproduces the d6 depth"
  came from tuning objectives that *minimise* the d1 diagonal
  (`mechanism_discriminator.tune_g`) rather than match the observed
  profile, so the matching region of the g-family was never sampled.

  Caveat on what this does and does not establish: a 29-permutation against
  five scalar cells has ample freedom, so reachability is weak evidence
  *for* the model. Its whole force is negative — d4/d6 is not evidence
  against it, and d6 is not an unexplained cell. The g²-diagonal-near-
  background requirement the simulations surfaced is unaffected. The
  partial-echo question is untouched and still undecidable (corrected
  φ5 = 0.85 ± 0.26); d5 remains predicted 0.0565 against observed 0.0492,
  which is the register/leak question, not a d6 question.
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
  cross-word diagonal, the DJU-BEI state return — the parity and
  abelianization shortcuts are vacuous, `mixed-alphabet-vigenere.md`)
  or a principle that pins the
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
- Any candidate key must satisfy the DJU-BEI **state return** `base_1477 =
  base_2926`. This is the full 1,449-step composition and is expensive; the
  abelianization relation below is NOT a cheap stand-in for it.
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
  register's 22.8% — the short-word deficit, now `two-rune-deficit.md` —
  so either the plaintext register is unusually short-word-poor, or the
  boundary question bears on it.
  **The expected-hit range does NOT span that uncertainty (August 2026),
  and the class searched is too narrow.** The deficit is z ≈ −10 on two
  independent references and confined to the 2-rune bucket, so 75-108 is
  an over-estimate for STANDALONE 2-rune words on any reading. Worse, if
  the deficit is short words attached to a neighbour rather than absent,
  `ᚦᛖ` sits inside longer words and the 465-word class misses those
  instances entirely. The fix is free, because the within-word phase does
  not depend on word length: `c₀ = base_w(p₀)` and `c₁ = base_w(g(p₁))`
  hold for ANY word, so score word-initial digraphs across all 2,928
  words rather than only the 465 short ones. Under the attach-to-previous
  variant `ᚦᛖ` lands word-finally at phase `g^((L−2) mod 5)`,
  `g^((L−1) mod 5)` — computable, just length-dependent. Direction is
  unsettled, so score both. Chance rises from 0.6 to ~3.5 hits, which
  the count still dwarfs.
  **Validated on planted keys** (`experiments/two_rune_gradient.py`):
  the objective recovers `base_0` exactly and instantly once `g` and `σ`
  are known, but the landscape over `(g, σ)` fails from both ends —
  short prefixes keep a wide basin but cannot pin a 29-permutation,
  long ones discriminate but the basin collapses. So this is a verifier,
  not a search gradient, and `base_0` should be treated as free rather
  than as part of the key search. See `no-known-plaintext-foothold.md`.

## Scripts

- `experiments/phase_absorbing_walk.py` — the model: `base_{w+1} = base_w ∘
  g^((len−1) mod5) ∘ σ`, hits the full battery.
- `experiments/walk_full_profile.py` — the full-profile corpus-sized
  simulation (joint-fit key, replicate bands, register comparison);
  writes `walk_reference.json`, the known-key validation corpus.
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
  surviving σ constraints (seam diagonal, group-size floor).
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
the rune-S echo; either could falsify or refine it. No hillclimb over
`(g, σ)` can work — the two-rune objective proved the landscape is a
delta function (`no-known-plaintext-foothold.md`) — so the realistic
paths to plaintext are enumeration of structured candidates verified
per key (the keyword Quagmire family of `mixed-alphabet-vigenere.md`
is the one enumerable set) or a contiguous crib; a short guessed
phrase alone cannot verify. Everything here is statistical
shape, not a confirmed decryption.

**Two August 2026 updates.** The period-5 architecture is now CONFIRMED rather than
plausible: d5 leaks plaintext while d3/d4 sit at chance, which refutes
one-alphabet-per-word (see Evidence against, first bullet). φ5 itself stays open at
0.64–0.71. And
the "no hillclimb can work" claim is true in substance but wrong in letter — it
holds for objectives needing the coupled base schedule, not for the isomorph channel,
which is local in `g` and does yield a gradient. That gradient plateaus at chance
agreement, for a reason now measured rather than guessed:
`key-local-channel-is-empty.md` shows the isomorph pattern is the COMPLETE
within-word invariant, reduces to six per-distance scalars (p ≈ 0.36), and is worth
~4 bits about `g`. So every informative observable is cross-word and hence
key-global, which is where the delta function comes from. The two surviving routes
are unchanged, and now bounded: enumerate a structured family
(`magic-square-grid-key.md`), or supply ~63 contiguous crib runes.
