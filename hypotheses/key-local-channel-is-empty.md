---
type: observation
---
# Observation: The Only Key-Local Channel is Empty (why no filter or gradient exists)

## Feature

Every statistical attack on this corpus has failed, and it is not luck. The cipher
has exactly one channel that is **local in the key**, that channel reduces to a
handful of scalars worth ~16 bits, and everything else about the corpus is **key-global** — reachable
only by committing to the whole key at once. Key-global means no partial credit, and
no partial credit is what a delta-function landscape *is*.

## Measurement

### 1. The information is present (this is not an information-theoretic barrier)

Unicity distance with runeglish redundancy `log2(29) − H_lang` against a ~178-bit
key (`g` 79.7 bits + σ 97.9; `base_0` is free, recoverable exactly once the other
two are known):

| H_lang | redundancy | unicity distance |
|---|---|---|
| 1.5 b/rune | 3.36 | 53 runes |
| 2.0 b/rune | 2.86 | 62 runes |
| 2.5 b/rune | 2.36 | 75 runes |

The corpus is 12,956 runes — about **209× the unicity distance**. The key is
uniquely determined many times over, and a correct key verifies instantly. Calling
the key "unidentifiable" is wrong; it is identifiable and hard to identify.

### 2. The within-word channel is the isomorph pattern, and nothing else

Within a word `base_w` is ONE unknown bijection applied elementwise, and the
complete invariant of a sequence under an unknown elementwise bijection is its
**equality pattern**. So the isomorph pattern is not one within-word observable
among many — it is the only one. Anything else requires comparing across words,
where `base_w` and `base_w'` differ by the step product over the intervening word
lengths.

### 3. That pattern reduces to six scalars

`experiments/isomorph_census.py`. P(a word holds ≥1 repeat), predicted from the
measured per-distance rates alone with position pairs treated as independent:

| L | words | observed | from rates | z |
|---|---|---|---|---|
| 3 | 726 | 5.8% | 4.7% | +1.4 |
| 4 | 514 | 11.9% | 12.0% | −0.1 |
| 5 | 318 | 24.5% | 22.0% | +1.1 |
| 6 | 252 | 39.3% | 34.3% | +1.7 |
| 7 | 214 | 44.9% | 46.0% | −0.3 |
| 8 | 159 | 60.4% | 57.5% | +0.7 |

Summed z² = 6.6 on 6 df, p ≈ 0.36. Per pattern, 49 single-collision cells tested,
largest deviation L=6 `ABCDCE` at z = +2.5 against a Bonferroni threshold of 3.3 —
nothing survives. **No higher-order structure.**

### 4. Those scalars are worth ~16 bits about `g` — not 4

The doublet count alone pins `theta = Σ_b P(g(b), b)` from a prior spread of 0.0125
to a Poisson precision of 0.00079 — a 15.8× narrowing, **4.0 bits**. But `g` has
order 5, so distance `d` tests `g^(d mod 5)` on the distance-`d` plaintext table, and
d1…d7 are therefore **seven** g-only constraints. Measured directly
(`magic_square_sweep.py`, plaintext tables weighted to the LP's word-length
histogram): 46 of 3,000,000 random order-5 permutations pass all seven at 2σ, a
65,000× cut = **16.0 bits** against `g`'s 79.7. The seam count gives σ 2.2 bits of
97.9. The constraints are jointly satisfiable — optimisation reaches all six tunable
cells to |z| ≤ 0.07 — so the tightness reflects a filter admitting only a tuned `g`,
not a contradiction.

Two figures were wrong before: 4.0 bits counted the doublet alone, and a later 16.3
came from tables that were not length-matched. Length-matching by RESAMPLING is also
unsafe — table noise from ~23k drawn words swings survivor counts with the seed — so
the tables are now weighted deterministically over all 123k prose words.

That is four times what an earlier version of this note claimed, and the correction
matters for honesty rather than for the verdict: 16.0 bits leaves ~64 bits, about
1e19 candidates for `g` alone, with σ untouched.

### 5. No local constraint on σ is KNOWN, across the reach-≤3 family

At a seam the base cancels, so a whole family of cross-boundary comparisons is local
in the key: comparing the a-th-from-last rune of word `w` with the b-th of `w+1` is
an equality exactly when `p_{last−a} = g^a σ g^b (p_{first+b})`. Each `(a, b)` is
therefore a diagonal constraint on a different group element. The 16 with a, b ≤ 3
measured (`experiments/sigma_local_budget.py`) — **this is a family, not an
exhaustive account of local σ observables**: larger reaches exist up to the word
length, and non-diagonal local statistics are not covered:

| relation | rate | z vs chance |
|---|---|---|
| σ (the seam doublet) | 0.786% | −7.9 |
| the other 15 (σg, gσ, gσg, g²σ, …) | 2.8–3.9% | **−1.5 to +0.9** |

Only `(0,0)` departs — and `negative-control-battery.md` already retired it: its
apparent significance came from a word-order null that destroys the doublet
suppression, and against a doublet-PRESERVING surrogate it reads 23 against
19.7 ± 4.6, **z = +0.72**.

So the budget is starkly asymmetric:

| | entropy | local constraint measured |
|---|---|---|
| `g` | 79.7 bits | **16.0 bits** (d1–d7) |
| σ | 97.9 bits | **none found** (reach ≤ 3) |

**On the evidence available σ is the harder half — more entropy, and no local
constraint yet identified.** Stated at proper scope: the reach-≤3 diagonals are all
at chance and the seam diagonal is retired, so *no known* local statistic constrains
σ. That is weaker than "σ has zero local constraint", which the measurement does not
establish — an untested statistic could exist. Three consequences, correspondingly
hedged:

- **No σ construction can be scored against any statistic we have.** That is why
  every mechanical account — the two-wheel device, a 5-ring cylinder — explains `g`
  and stalls at σ, and why `magic-square-grid-key.md` ended UNDECIDED. Finding a
  local σ observable would reopen the route, and none of the 16 tested is one.
- Effort spent on `g` constructions is spent on the easier 45% of the problem.
- It independently reproduces the crib size: σ's 98 bits at log2(29) = 4.86 bits per
  rune needs ~20 runes of over-determination, `g`'s remaining ~64 bits ~13 more, and
  `base_0` absorbs the first 29 — about 62 contiguous runes, matching the estimate in
  `information_budget.py`.

### 6. sigma does not lie in the group generated by `g`

(August 2026, `experiments/base_step_in_g.py`.) If `sigma = g^t`, the base would only
ever move by powers of `g`, so `base_w = base_0 . g^(s_w)` and the **whole book would
use just 5 alphabets** — collapsing the key from ~178 bits to ~83 and explaining
boundary-blindness for free, since the seam diagonal would then be a `g`-power
diagonal like d1 and one tuning would suppress both.

It is testable with no key at all. If the alphabet depends only on a class index
computable from word lengths, two positions in the same class share an alphabet and
their coincidence is the plaintext's (~1.6), not flat — and `base_0` never enters,
because IoC is invariant under a permutation of the alphabet.

| hypothesis | within-class IoC |
|---|---|
| `sigma = g^t`, t = 0..4 | 0.9991 – 1.0007 |
| `sigma = h^(c_last)`, four maps of the last ciphertext rune | 0.9986 – 1.0028 |
| controls (phase only, absolute position, whole corpus) | 0.9976 – 1.0007 |

Flat everywhere against the ~1.6 a hit needs. **The 5-alphabet collapse is refuted,
and so is a ciphertext-driven base step inside ⟨g⟩.** `sigma` stays a free
permutation, and the asymmetry in the budget table above is unrelieved.

## Five extraction attempts, all consistent with the above

| attempt | script | result |
|---|---|---|
| doublet count → θ | `doublet_targeted_search.py` | 4.0 bits; the apparent +5.34σ lift was an artifact |
| isomorph score over `g` | `isomorph_g_score.py` | real gradient (true −3.71, 1 transposition −3.75, random −3.93) but hillclimbs plateau at **chance agreement, 0–3 of 29** |
| + quadgram sequence model | same | no measurable improvement — with ~20 candidates per word a wrong `g` still assembles into fluent text |
| hard rejection (impossible words) | same | median random `g` makes **zero** words impossible; 32% refuted at 3,000 words, a 1.5× cut |
| magic-square grid family | `magic_square_sweep.py` | 0 of 190,008 survive the 7 distance cuts against 1.4 expected by chance (p = 0.25) — no enrichment, and the filter admits only a tuned `g`, so any construction would fail |

The second deserves emphasis: it refutes the *letter* of "no hillclimb can work"
(`length-clocked-walk.md`), which holds for objectives needing the coupled base
schedule but not for this one. A gradient exists. It leads onto a plateau.

**Direct confirmation that the BASE, not `g`, is the obstruction (Aug 2026,
`experiments/hillclimb_single_g.py`).** Strip the base schedule entirely and
encipher with a single stepped permutation `c[i] = g^i(p[i])`, `g` tuned to a
low doublet diagonal (the "single permutation with low doublet diagonal"
model). This IS hillclimbable: a plain conjugation-swap hillclimb on the
decryption's trigram score **recovers `g` exactly, 29/29**, at orders 5, 28,
and a full 29-cycle (the last needs ~24 restarts), under both a
register-matched and a *generic* trigram model, true `g` the global maximum.
So a single `g` with no base falls out immediately. **Run on the REAL LP, the
same attack fails at every period** (`experiments/hillclimb_lp_sweep.py`,
full 8×4000 budget, FREE-choice `g` — random permutation starts, plain-swap
moves over all of S₂₉, no cycle constraint): hillclimbing a stepped `g` on
the LP ciphertext for periods `m = 2..50` gives a best decryption IoC of
**≤ 1.002 (random ~1.0, English ~1.7) at every single period** — no `m`
produces readable plaintext. The negative is real, not search weakness: a
built-in self-check shows the metric is *sensitive* — on a planted free `g`
the true key is the global maximum and even a PARTIAL recovery (~22/29)
yields a decryption IoC ~1.6, far above 1.0. A stepped-`g` LP would therefore
light up even under an incomplete search; the flat ~1.0 everywhere means no
solution. So the LP is not a single stepped `g` of any period ≤ 50, and the
delta-function landscape is bought entirely by the per-word base (each word a
fresh bijection, so even the correct `g` yields no readable consecutive text
until the base is also known). CONTROL: a monoalphabetic
`c[i]=g(p[i])` recovers the key too (27/29, the two holdouts the rarest,
weakly-constrained runes) but cannot suppress a doublet (a bijection
preserves the plaintext doublet rate), so the low diagonal *requires* the
stepping, and the stepping does not break the climb. (A first pass reported
the stepped cipher un-climbable; it was a decrypt bug — `gg.index(x) for x in
gg^k` computes `gg^(k-1)`, not `(gg^k)^{-1}` — caught by a
`dec(c,g)==plaintext` round-trip assertion.)

## The held-out cells are not a new channel either (September 2026)

`experiments/fingerprint_battery.py`. Scoring a walk on statistics it was NOT fitted
to — unigram IoC, entropy, off-diagonal bigram chi-square, the kappa maximum over
skips 2-40, the doublet position profile and minimum gap, identical-word counts, the
clock reading — those cells do move with the key, which looks at first like a channel
this file missed.

Measured, they are not. Over 30 keys fitted to the six diagonals and scored on 40
prose corpora each, the number of free cells failing at p <= 0.10 has median 2 against
1.2 expected by chance on 12 cells, and keys with at most one failure are 43% where
chance gives 66%. The whole set is worth **0.6 to 1.2 bits**, against `g`'s 64-bit
residual and sigma's 98.

The reason fits this file's thesis rather than denting it: those statistics are global
mixing properties, which any key visiting enough bases reproduces. They discriminate
between a walk and a non-walk, which is what `fingerprint_battery.py` is for, and
barely at all between two walks.

## Significance

```
within-word observables = the isomorph pattern        (complete invariant)
isomorph patterns       = the per-distance rates       (p ≈ 0.36)
per-distance rates      = ~16 bits about g (d1..d7, measured)
⟹ every informative observable is cross-word, hence key-global
⟹ key-global means right key or noise — the delta function
```

This is a property of the cipher, not of any search. It explains every failure
without appealing to bad luck, and it predicts that further objective-engineering
will fail.

## The base-free channel, mapped completely (2026-08-15)

The "within-word observable is the isomorph pattern" argument above extends to
the **whole** ciphertext, and closes it. Every coincidence cancels the base:
for two runes at (word w, phase j) and (word w′, phase j′),
`base_{w′} = base_w ∘ S` with S the step-product between them, so the shared
`base_w` cancels and

    p[i] = g^(−j) · S · g^(j′) · p[i′]   — base-free, whatever S is.

The seam is **not** special in cancelling the base — *every* coincidence does.
What varies is whether the exposed relation `g^(−j)·S·g^(j′)` is a clean
permutation or a long scrambled ⟨g,σ⟩ product:

| pair | S | exposed relation | corpus cell |
|---|---|---|---|
| same word, phase gap d | id | **g^d** | d1,d6 → g (low); d5,d10 → id (echo); d2,3,4 → g²,³,⁴ |
| adjacent words, **last→first** | g^a·σ | **σ** (last phase cancels the step's g^a) | the 23 seam doublets |
| **base return** (S = id over k words) | id | **identity**, cross-word | DJU-BEI repeat |
| any other pair | long word in ⟨g,σ⟩ | scrambled | chance |

This explains the STRUCTURE of the profile — *which* g-power each cell is: the
period-5 (d1,d6 both g; d5,d10 the echo via g⁵=id); the seam being σ (the
last-rune phase cancels the step's g^a); DJU-BEI being a base return. **It does
NOT explain the rates**, and that boundary matters. The rate in each cell is
the diagonal of g^(d mod 5) on the *distance-d* plaintext pair table — six
separate numbers = the ~16-bit local channel — and they are NOT cascaded from
the d1 tuning. Verified (2026-08-15): a g tuned on d1 alone gives d1 0.0001,
d4 **0.019 (low)**, d6 **0.038 (chance)** — the LP has d4 **0.041 (lean)** and
d6 **0.025 (low)**, i.e. the *opposite* at d4 and d6. (Also: minimizing d1
leaves diag(g)=0.0001 AND diag(g⁻¹)=0.0107, both low, so d4=g⁻¹ inherits low,
not a lean — an earlier "reverse-bigram inflation" story for the d4 lean was
wrong.) But my d1-only tuning is itself the wrong objective, and it does not
prove the d4/d6 rates are unexplained. The resolved statement
(`length-clocked-walk.md`, `mixed-cycle-progression.md`, August 2026): **all
six rates are the six diagonals of one order-5 g.** Fitted jointly to
d1,d2,d3,d4 and d6, a single g reaches every cell (0.0064 / 0.0345 / 0.0369 /
0.0408 / 0.0247 against the observed 0.0064 / 0.0347 / 0.0370 / 0.0410 /
0.0245). The apparent **d4–d6 split was retracted** — it assumed a g fitted to
d1..d4 predicts d4 ≈ d6, but the rate is the g^d diagonal on the *distance-d*
pair table and P₄ ≠ P₆, so the model predicts d4/d6 = 1.25, against which the
LP sits at z = +1.12. No anomaly. My d1-minimising test gives d4 low / d6
chance precisely because minimising d1 is not what the LP's g does; matching
all cells, not minimising one, is the right objective. So the map nails the
STRUCTURE (which g-power each cell is) and the rates are the diagonals of that
one g — d2,d3 land at chance (g²,g³ generic on their tables), d1/d6 low, d4 a
mild lean, d5 the echo, the seam σ. There is no fourth clean window — everything else is a long
⟨g,σ⟩ product, generic by measurement (σ² and the bridge relations `σ·g^b·σ`
sit at chance, see route 2's seam-doublet note).

Two conclusions:

- **The base-free channel is complete and fully measured.** The delta-function
  landscape is not a search-engineering failure; it is what "the base-free
  channel is exhausted" *looks like*. Any further information is necessarily
  key-global (the base schedule) — a crib or a structured (g, σ) enumeration.
- **⟨g,σ⟩ has no short relations.** Because no step-product beyond length 1 is
  clean, σ is not low-order, not an involution, not near a power of g — the walk
  is free. (Consistent with `sigma-power-step.md` and the ≥300-base depth.)

## Consequences

Two routes are known. (Two, not "exactly two" — this is a list of what has been
proposed, not a proof of exhaustiveness.)

1. **Shrink the key space until it is enumerable.** `magic-square-grid-key.md` is
   **UNDECIDED**, not refuted (`magic_square_sweep.py`): its 190,008 candidates give
   0 survivors of the seven distance cuts, but so does a random control at any
   threshold retaining a true `g`, because the cuts admit only a `g` tuned against
   the digraph tables. Separating a candidate from the ~32 false positives at 3σ
   needs the 2-rune verifier → the base schedule → σ, which has no construction. So
   **σ's absence blocks the evaluation, not only the attack**, and no construction
   family currently has a decidable test. Two families have been tried (keyword
   grids, the magic square) and neither shows enrichment; that is two negatives, not
   a general impossibility.
2. **Import external information.** About **63 contiguous crib runes, roughly 15
   consecutive words**, closes the gap. DIVINITY WITHIN is 13 runes and ~14 bits,
   consistent with its recorded 16,000× reduction and about a fifth of the way.

   **The crib route is now validated end-to-end on a known key** (2026-08-14,
   `experiments/crib_propagation.py` against `walk_reference.json`). Every crib
   rune is one `(input, output)` constraint on `base_0` under a candidate
   `(g, σ)`, because `base_w = base_0 ∘ prefix_w` with prefix clocked by the
   public word lengths. Measured over 400 trials: the true key never
   contradicts and pins `base_0` in a **median 80 contiguous runes** (min 47,
   max 182) — the empirical unicity length, ~27% above the 63-rune analytic
   lower bound, which is exactly the image-collision penalty `information_budget.py`
   flags but never measured. Wrong keys reject fast: random `(g, σ)` in a
   median 6 runes, cycle-type-preserving nearest neighbours in 13–14
   median. The nearest-σ rejection tail is HEAVY (max ~280 over thousands
   of trials), so a verifier crib should be a few hundred runes to guarantee
   the slowest neighbours reject. **Every distinct wrong key is rejected by
   one contiguous crib; no genuine near-neighbour degeneracy exists.** One caveat a real
   verifier must honour: reject on the bijection **contradiction**, not on
   `base_0` fill — a wrong key can fill `base_0` consistently before its
   error is exercised. This confirms the "a correct key verifies instantly"
   claim and turns ~63 into a measured ~80; it does not lift the ENUMERATION
   burden of route 1 — the crib is a verifier, not a search.

   `experiments/d5_crib_targets.py` supplies key-free plaintext constraints toward
   this: since d5 reads plaintext equality directly, 8 words carrying XY···XY are
   pruned to 4–152 dictionary candidates (word 1987 to **4**, word 2751 to **14**).
   Those are scattered rather than contiguous, so each carries its own unknown base
   and the crib is weaker per rune — but with `base_0` eliminated they still give
   injectivity constraints on `(g, σ)` alone.

   **The enumeration should admit two-word concatenations, not only dictionary
   words.** If scribal merging is real at the rate the 2-rune share fixes
   (`d5-partial-alphabet-leak.md`, CLOCK section), 18% of LP units of length ≥ 6 are
   two true words joined, rising to 27–39% at lengths 10–13. Every XY···XY target
   sits at length ≥ 7, the contaminated end, so a candidate list drawn from single
   dictionary words silently excludes the true answer for roughly a sixth to a third
   of them. Scribal merging is undecided, so this is a hedge rather than a
   correction — but the hedge is cheap and the crib route is the only one that does
   not pass through σ.

   **Seam doublets are base-free σ-readings, but under-determine σ and don't
   touch g (2026-08-15).** At a seam doublet `c_last(w)=c_first(w+1)`, the shared
   `base_w∘g^a` prefix cancels, leaving `p_last = σ(p_first)` — one point of σ,
   **g-free** (the phase absorber makes every seam a constant σ). So a crib on the
   two runes of each of the 23 seam doublets reads σ directly: 23 doublets →
   ~13–16 *distinct* `p_first` values (birthday over word-initials; the ciphertext
   count is NOT a proxy — different bases scramble it) → σ pinned to (29−k)! ≈
   13!–16! ≈ 6e9–2e13 (33–44 bits), down from 29! ≈ 1e30. A large cut, but NOT a
   solve, and it leaves **g entirely** — the seam is g-free, so g stays at its
   ~64 key-global bits (the 16-bit local channel is the only handle). So cribbing
   all 23 seam doublets gives σ to ~33–44 bits AND g to ~64 bits ≈ ~97 bits
   residual: partial σ, not a key. It also needs a *scattered* crib on 23 specific
   boundaries (~46 runes), harder to obtain than a contiguous phrase and strictly
   worse than the ~80-rune contiguous propagation, which yields the whole key at
   once. The BRIDGE extension (the base also cancels across a g-cancelling word,
   exposing σ² or σ·g^b·σ) adds nothing: those relations measure at chance —
   σ² is not low-diagonal — so there is no second suppressed diagonal beyond the
   seam. The g-identity / 5-rune-word structure that motivated this is real
   algebraically (a 5- or 10-rune word cancels g), but every ciphertext view of
   it — the g-identity bigram, seam-rate-by-length, W² across the bridge — comes
   back flat, because the per-word base scrambles each before it reaches the
   ciphertext. Net: elegant confirmation that the seam IS σ, but doublet-limited
   (23) and g-blind, so no shortcut past route 1.

## Falsifiable

The argument assumes `base_w` changes at every word and is otherwise free. If it
does not change per word, within-word invariants extend across words and the
isomorph channel stops being vacuous. `two-rune-depth-no-base-reuse.md` puts the
base at ≥~300 effective values, which is strong but not the same claim. A statistic
that is local in the key and NOT of the isomorph family would also break it; none is
known, and §2 argues none exists.

## Scripts

- `experiments/information_budget.py` — the budget, unicity distance, crib sizing.
- `experiments/crib_propagation.py` — the crib verifier run on the known-key
  reference corpus: measured unicity ~80 runes, wrong-key rejection speeds.
- `experiments/isomorph_census.py` — the pattern-to-rates reduction.
- `experiments/isomorph_g_score.py` — the gradient that plateaus (worked negative).
- `experiments/hillclimb_single_g.py` — a single stepped `g` (no base) IS
  hillclimbable; establishes the method and the synthetic recovery.
- `experiments/hillclimb_lp_sweep.py` — the full-budget free-`g` attack on the
  LP at every period 2..50 (all IoC ~1.0), with the sensitivity self-check.

## Related

- `length-clocked-walk.md` — the model this characterises.
- `no-known-plaintext-foothold.md` — the delta-function landscape, now explained.
- `magic-square-grid-key.md` — route 1.
- `two-rune-deficit.md` — where the plaintext's own structure is anomalous.

## RETRACTED: the seam "fixed-point" constraint was an algebra error (September 2026)

A previous revision of this file claimed the seam doublet rate measures the fixed-point
count of the seam relation, and derived from it a constraint on σ — "the five seam
relations carry ~1 fixed point where random permutations carry 5". **That is wrong and
is withdrawn.**

The error is one step. A seam doublet is `c_last = c_first`, so with `A` the alphabet
at each position,

    A_last(p_last) = A_first(p_first)   hence   p_first = R(p_last),  R = A_first⁻¹ ∘ A_last

The condition is that the plaintext pair lies on the **graph** of `R`, not that `R`
fixes a point. Fixed points would require `p_last = p_first`, which is not what a
ciphertext doublet says. So the seam rate is

    Σ_x P(p_last = x, p_first = R(x))

— the plaintext cross-word bigram mass that `R` happens to select. For a random `R`
that averages 1/29, which is why a random relation sits at chance, but it is a sum of
bigram probabilities and takes any real value. Nothing forces it to be a multiple of
1/29, so the integer argument evaporates, and with it the claim that a single fixed σ
is favoured over free per-word choice.

The per-class breakdown had no power either, which a homogeneity test would have shown
before the claim was made: the five classes hold 3 to 7 doublets each and are
consistent with a single rate, chi² = 3.10 on 4 df, p = 0.54.

**What survives** is only what was already known: the seam doublet rate is 23/2927 =
0.00786, 0.228x chance, so the relation `R` selects low-probability plaintext bigrams.
That is the tuned-relation argument of `doublet-suppression-requires-design.md`, not a
new handle on σ.

**This file's headline therefore stands unchanged: σ has no local constraint.**

## The local constraint on g, priced distance by distance (September 2026)

The validated identity in `doublet-suppression-requires-design.md` generalises: under
the walk the within-word relation between positions j and j+d is `g⁻ᵈ`, so the
distance-d coincidence rate is exactly `Σ_x P_d(x, g⁻ᵈ(x))` — the plaintext distance-d
bigram mass that `g⁻ᵈ` selects. That turns "how much does the corpus say about g" into
a counting question, answered against the author's own plaintext:

| d | body rate | relation | random order-5 g within 2σ | bits |
|---|---|---|---|---|
| 1 | 0.00628 ± 0.00079 | g⁻¹ | 0.0078 | **7.0** |
| 2 | 0.03473 ± 0.00216 | g⁻² | 0.2509 | 2.0 |
| 3 | 0.03702 ± 0.00272 | g⁻³ | 0.2940 | 1.8 |
| 4 | 0.04098 ± 0.00351 | g⁻⁴ | 0.3320 | 1.6 |
| **all four jointly** | | | **0.00013** | **13.0** |

Three things follow.

**The doublet rate is more than half the total.** d1 alone supplies 7.0 of the 13.0
bits; d2 through d4 add 6 between them. Any effort to constrain g locally is mostly an
effort about doublets.

**13 bits is cross-validated and nearly useless.** This file's independent figure is
16.0 bits from d1 through d7, and 13.0 from d1 through d4 is consistent with it. But
there are about 9.8e+23 order-5 permutations of cycle type 5⁵1⁴ — roughly 80 bits —
so 13 bits of constraint leaves about 67. The local channel narrows g by four orders of
magnitude out of twenty-four, which is why the search surface is flat: this is the
quantitative form of that observation.

**The d5 echo constrains g not at all.** Since g⁵ = id, *every* order-5 g predicts the
same distance-5 rate, namely the plaintext's own. So the corpus's most-studied anomaly
carries zero information about which g it is; it tests whether the walk frame is right.
On that it is consistent: the walk predicts the plaintext rate 0.0575 ± 0.0144 against
the body's 0.0492 ± 0.0048, a difference of z = −0.55, so φ5 = 1 is not rejected and
not confirmed — the underpowered verdict `d5-partial-alphabet-leak.md` already records.

## The seam is not empty — but only under the relational reading (September 2026)

This file's headline is that σ gets ~0 local constraint. That needs qualifying, and the
qualification is worth 28 bits.

The orbit theorem (`local-channel-is-exactly-coincidence.md`) applies across a word
boundary too: a pair `(last of w, first of w+1)` is `(β_w(u), β_w(σ^k(v)))`, so equality
is again the only invariant and the seam coincidence rate is a selected-bigram-mass
statistic — `Σ_x P_cross(x, R(x))` for the seam relation `R`.

**The cross-word plaintext is not uniform**, which is what decides whether that
statistic can say anything. English word-final and word-initial letters are each
strongly skewed, so `P_cross` is non-uniform from the marginals alone, even with no
dependence between adjacent words. Measured on the author's own plaintext, with the
sparsity artefact of a 485-pair table subtracted:

| channel | pairs | observed spread | noise floor | real signal |
|---|---|---|---|---|
| within-word d1 | 1,477 | 0.01469 | 0.00473 | 0.01391 |
| cross-word seam | 485 | 0.01321 | 0.00828 | **0.01029** |

The seam signal is 0.74× the within-word one — the same order, not negligible.

**So the seam rate is a strong constraint.** The body's seam coincidence is 23/2927 =
0.00786 against 0.0345 expected. Averaged over the five relations (one per word length
mod 5, which the corpus cannot separate — chi² 3.10 on 4 df) the spread is 0.00460, so
the observation sits **z = −5.79**, p = 3.6e−9, or **28 bits**.

**The fork that decides whether those bits exist.** All of the above assumes the
suppression is *relational* — that `R` was chosen to avoid common plaintext bigrams. If
instead a doublet **preventer** produces it, by re-emitting whenever a repeat would
occur, then `R` is unconstrained and the seam yields **zero** bits on σ.
`doublet-suppression-requires-design.md` leaves both readings open, and the same fork
applies to the 7.0 bits the within-word d1 channel gives g.

That makes the preventer question the most valuable open question here, and gives it a
price: under the relational reading the local channel yields ~13 bits on g plus ~28 on
the seam relations; under the preventer reading it yields ~6 on g and nothing on σ.

## The fork resolves toward the preventer, so the headline stands after all

The section above priced the preventer question at 28 bits and left it open. It does
not stay open long, because boundary-blindness decides it.

**The two rates are statistically equal.** Within words 63/10028 = 0.00628 ± 0.00079;
at the seam 23/2927 = 0.00786 ± 0.00163. The difference is +0.00158 ± 0.00181,
**z = +0.87** — the suppression does not care about the word boundary, which
`doublet-suppression.md` already records as "boundary-blind".

**A preventer predicts that for free.** One mechanism acting on adjacent ciphertext
runes gives one rate, and the boundary is irrelevant to it.

**The relational reading has to buy it.** The within-word rate and the seam rate come
from different relations acting on different plaintext distributions, so under that
reading they are independent draws:

| | z | P |
|---|---|---|
| within-word, relation g⁻¹ | −2.03 | 2.1e−2 |
| seam, one fixed relation | −2.59 | 4.8e−3 |
| seam, five relations averaged | −5.79 | 3.6e−9 |

Jointly with the within-word rate, the relational reading needs a coincidence of
**13 bits** if a single relation acts at the seam, or **34 bits** if five do — and then
needs the two independent results to land within 2σ of each other on top of that.

So the preventer explains with one mechanism what the relational reading must buy with
13 to 34 bits of tuning. That is a decisive parsimony argument, and it resolves the fork
in the direction that **removes** the 28 bits: if a preventer produces the suppression,
the seam relation is unconstrained and σ is not reachable through it.

**This file's headline therefore stands: σ gets ~0 local constraint.** The 28 bits were
real arithmetic about a reading that the boundary-blindness argues against.

What would overturn it is evidence that the suppression is *not* boundary-blind — a
measured difference between the within-word and seam rates — or a mechanism-level reason
the two relations should coincide. Neither exists at present.

## σ does get one constraint after all — from the alphabet count, not from a local relation

The retraction above withdrew a claimed local constraint on σ. A different one survives,
and it comes from a global count rather than a local relation, which is why the orbit
theorem does not forbid it.

Under a walk whose bases are generated by iterating a single σ, the alphabet at
within-word position k of word w is `base₀ ∘ σ^w ∘ g^k`, so the number of distinct
alphabets is at most **order(σ) × 5**. `flat-ioc.md` requires at least 949 effective
alphabets, and the bases are visited uniformly (each is used 2928/order(σ) times), so

    order(σ) × 5 ≥ 949      hence      **order(σ) ≥ 190**

Sampling 200,000 random permutations of 29 points, the order distribution has median
**84** — a typical σ *fails* this — and only **22.2%** reach 190, so the constraint is
worth **2.2 bits**.

Small, but it is the only constraint on σ in this directory, and it has two properties
that matter:

- **It is phase-independent.** A preventer changes which alphabet is used where, never
  how many exist, so no interrupt rate weakens it
  (`preventer-blinds-absolute-tests.md`).
- **It excludes the two most natural constructions.** Order 29 — a single 29-cycle
  rotating through all bases — is out, as is order 28, the order of the multiplicative
  group mod 29 and the natural home for an affine σ. Also excluded are the commonest
  random orders: 60, 24, 28, 29, 26, 84, 120, 90.

**Scope.** This assumes bases generated by iterating one σ. A two-dial odometer
(`quagmire-odometer.md`) reaches 29 × 29 × 5 = 4,205 alphabets and passes comfortably,
so the bound constrains the single-σ walk rather than the family as a whole.

## A stronger bound on σ from base reuse, worth 3 to 8 bits

The alphabet count above gives order(σ) ≥ 190. The depth data gives more.

If order(σ) = N, bases repeat every N words, so words w and w+N share one. Two such
words with the same plaintext then produce **identical ciphertext**, which is exactly
what `two-rune-depth-no-base-reuse.md` counts. Calibrating the plaintext word-repeat
rate on the author's own words (10.1% for 2-rune words, 6.8% for 3-rune), the expected
extra identical pairs scale as 1/N:

| N | extra identical 3-rune pairs |
|---|---|
| 29 | 615 |
| 190 | 94 |
| 500 | 36 |
| 1000 | 18 |
| 2928 | 6 |

The body shows **17** identical 3-rune ciphertext pairs against a chance expectation of
10.8 — an excess of 6.2 ± 3.3, whose 95% upper bound is 11.6. That bounds

    order(σ) ≥ 1,536

**but only under a per-word phase reset.** If the letter clock runs continuously across
words, two same-base words collide only when their starting phases also agree mod 5,
which divides the expected extra pairs by five and the bound with it:

| clock reading | order(σ) ≥ | fraction of S₂₉ | bits | surviving cycle types |
|---|---|---|---|---|
| per-word phase reset | 1,536 | 0.0041 | **7.9** | **9** |
| continuous clock | 307 | 0.115 | 3.1 | 329 |

**The strong reading is actionable.** Only nine cycle types of 29 points reach order
1,536, all built from long coprime cycles:

    (9,8,7,5) 2520 · (11,7,6,5) 2310 · (11,7,5,3,2)+1 2310 · (11,9,5,4) 1980
    (11,8,7,3) 1848 · (13,7,5,4) 1820 · (13,8,5,3) 1560 · (11,7,5,4,2) 1540
    (11,7,5,4)+2 1540

A σ search under that reading need enumerate only those nine, and σ must contain a cycle
of length 9, 11 or 13 in every case.

**The 2-rune channel is not used** for this bound. It shows 112 identical pairs against
128 expected — a *deficit* — because the doublet suppression removes 2-rune words with
equal runes, so that channel is contaminated and would give a spuriously strong answer.

## The convention cannot be settled here, and now that is priced (September 2026)

The two readings above differ by a factor of five, and the choice between them has been
left open. `clock-convention-is-out-of-reach.md` prices both channels the model exposes.

The first — reading adjacent blocks under each phase convention — fails outright: a
planted continuous clock scores +2.54 under the reset reading against a planted reset
clock's +2.86.

The second does discriminate. Under a continuous clock, matching position mod 5 across
adjacent blocks is correct exactly when the first block's length is divisible by 5, so the
signal concentrates in that class; under a reset clock it is flat. Planted at sigma fixing
5 runes the contrast is +0.0641 for reset against +0.1314 for continuous — a separation of
0.067 against the body's own noise of 0.125 on that statistic. **0.54 sigma**, needing
14x the corpus to reach 2.

So both bounds stand together permanently. Quote 307 and 1,536, not one of them.


## The d-profile filter omits the clock drift, and it does not matter

`experiments/the_g_filter_ignores_the_drift.py`

The 16.0-bit figure above comes from scoring a candidate `g` by comparing the body's
observed d_k against the undrifted plaintext mass m_k(g). That predictor is wrong: the
doublet preventer advances the clock by one step whenever it fires, so a distance-k pair
keeps its phase relation only if no firing falls between the two runes. With a firing rate
q per position the correct prediction is

    E[d_k] = (1−q)^k · m_k(g) + (1 − (1−q)^k) · (1/29)

The observed rate is pulled toward chance, by 6.7% at k = 2 and 21.5% at k = 7, so the
uncorrected filter prefers candidates whose masses are closer to 1/29 than the true key's.

**Measured, the bias is under half a standard error at every distance.** At q = 0.034 a
mass of 0.050 reads as 0.0467 at k = 7 — a shift of 0.0033 against that cell's standard
error of 0.0075.

Planting a known `g`, enciphering with a preventer, and ranking it in a pool of 4,000:

| preventer φ | firing rate | uncorrected rank | corrected |
|---|---|---|---|
| 0.0 | 0.0000 | 0.061 | 0.061 |
| 0.5 | 0.0164 | 0.072 | 0.066 |
| 0.9 | 0.0295 | 0.077 | 0.070 |
| 1.0 | 0.0328 | 0.079 | 0.072 |

The preventer costs the filter a little power and the correction recovers about half of
it. On the body the survivors of 4,000 at 2σ move from 29 to 30 to 35 as q goes from 0 to
0.034 to 0.050.

**No published number needs revising.** The correction is now available and costs nothing
to apply. What this settles is that a sweep costed against this filter is not searching a
biased region, which had not been checked.

## The local σ diagonal family is now complete, and still empty

`experiments/the_complete_local_sigma_family.py`

Section 5 above records "No local constraint on σ is KNOWN, across the reach-≤3 family"
and states its own limit: *"this is a family, not an exhaustive account of local σ
observables: larger reaches exist up to the word length"*. Two facts about `g` having
order 5 close that gap.

**The family is finite and 25 is all of it.** The relation at reach (a, b) is
`p_{last−a} = g^a σ g^b (p_{first+b})`, so only a mod 5 and b mod 5 matter. Reaches 0–4 in
each direction exhaust the elements `g^a σ g^b`; the nine cells with a = 4 or b = 4 were
missing.

**Reach a and reach a+5 constrain the same element**, so their pairs pool exactly rather
than approximately.

| | pairs | z |
|---|---|---|
| (0,0), the seam doublet | 4,884 | −5.99 |
| largest \|z\| over the other 24 | | **1.68** at (1,1) |
| the same maximum on 40 word-order shuffles | | 2.22 ± 0.41 |

(0,0) is the doublet preventer, not a σ signal, and `negative-control-battery.md` already
retires it as evidence about the key. Excluded, the largest departure in the whole family
is **1.68 against a shuffled maximum of 2.22 ± 0.41** — P = 0.90, below what 24 cells give
by chance.

Completing and pooling added nine cells with 10,263 pairs and raised the family to
**57,167 pairs**, roughly double the reach-≤3 enumeration. So the null is not for want of
data.

**The scope caveat is discharged for diagonals.** No further diagonal cell exists to test.

**CORRECTED.** This paragraph first said the remaining gap was "triples, not pairs". There
is no such gap. `base-family-is-the-symmetric-group.md` completes the classification — the
family is A₂₉ or S₂₉, and **both are 27-transitive** — so every ordered triple of distinct
runes lies in one orbit and triples carry nothing, as does every k-tuple up to 27. The
local channel is exactly the equality pattern **at every order**, not only at order two.

`experiments/do_triples_carry_anything.py` checks this against the corpus and also records
a statistic not to reuse: mutual information between the two differences of a triple has
no power here. A planted affine base — 2-transitive, not 3-transitive, exactly the case
such a test must catch — reads z = −0.33 against a general base's −0.40. Under
`x → a·x + b` both differences carry the same unknown multiplier, so only their *ratio*
survives, and MI measures independence rather than that ratio. The ratio test in
`base-is-not-affine.md` is the instrument that works.

So there is no order-k statistic left to try. The classification rests on measured
premises — transitive, not Frobenius, not affine — and attacking one of those is the only
route, not a higher-order local statistic.
