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
