---
type: observation
---
# Characterization: The Repeated Phrase ᛞᛄᚢ-ᛒᛖᛁ (Key-State Recurrence)

## Claim

The unsolved ciphertext contains a repeated 6-rune, two-word sequence
**ᛞᛄᚢ-ᛒᛖᛁ** ("DJU BEI") at rune offsets **6555 and 12950** of
`data/page0-58.txt` (distance 6395), with **identical word boundaries** in
both occurrences (word-initial 3+3 both times). (An earlier 7-gram framing
**ᛞᛄᚢᛒᛖᛁᚫ** is retracted as contamination: the second occurrence is the
last six runes of section 9, and its "7th rune" ᚫ is the FIRST rune of the
solved AN END page — a differently-enciphered system that cannot share key
state with the unsolved stream. The trailing-ᚫ agreement is a 1/29
cross-boundary coincidence; only the 6-gram is a cipher-stream repeat.
Found in the July 2026 clean-corpus re-run of `anchored_repeats.py`.) A second, weaker boundary-consistent repeat
**ᛁ-ᛗᛝᚣᚪ** occurs at offsets 10671/12764 (distance 2093). The second
repeat is NOT individually significant: the corpus has 5 repeated
length-5 classes vs ~4.1 expected by chance
(`collision-hunt-single-constraint.md`), so only its boundary-consistent
configuration is suggestive (count-level P = 0.058, clean re-run); treat it
as a candidate, not an established second state-return.

The repeat is **weak-to-moderate evidence** that the cipher's key state recurs,
and that the recurrence is word-aligned. It is not proof. See "How much does
this repeat actually weigh" below: the likelihood ratio against a plain walk is
4 to 28, because a walk produces such a repeat by chance collision in 1.0% of
surrogate corpora — the figure this file already reports under Significance.

An earlier version of this paragraph said the repeat "proves the key state
recurs exactly". That does not follow from a 1-in-100 event.

## Status

**Status**: confirmed (characterization)

The repeat itself was previously known to the community (listed on the
Uncovering Cicada wiki as the longest repetition, on pages 27.jpg and
55.jpg). This note adds the significance quantification, the
boundary-consistency analysis, the second aligned repeat, and the negative
results that bound what the recurrence can be.

## The observations

Contexts (`-` word, `.` sentence, `|` line, `$` section break):

```
offset  6555:  ...ᚾ|ᚻᚷᚢᛡᚻᚢ-ᛒᚠ-ᛞᛄᚢ-ᛒᛖᛁ-ᚫᚠ-ᛈ-ᚫᛈᚦ-ᚱᛗᛚᚳ-...
offset 12950:  ...ᚦᛟ-ᚳᛠᛁᛗ|ᚳᛉ-ᛞᛄᚢ-ᛒᛖᛁ. $ ᚫᛄ-ᛟᛋᚱ....
```

- Both occurrences of ᛞᛄᚢ and ᛒᛖᛁ are full words (3+3 runes), word-initial
  in both places (word indices 1477/2926 of the 2,928 clean-corpus words).
- The second occurrence is the **final two words of its section**, ending
  with a sentence stop. The 7th matching rune ᚫ is then the *first rune of
  the next section* — if sections are independent units this last rune is a
  1/29 bonus coincidence; if the stream is continuous the depth is 7.
- The third word continues the pattern: ᚫᚠ (occ 1) vs ᚫᛄ (occ 2) — both
  2 runes, sharing the first rune and diverging at the second. The
  word-length pattern of the match is 3,3,2 in both places. Under an
  aligned additive state, ciphertext diverges exactly where plaintext
  diverges — consistent with third words sharing their first letter
  (e.g. AN vs AD).
- The secondary repeat: `...ᛝᛉᛞᛁ-ᛗᛝᚣᚪᛝᚠᛉᛁᛟᚷᛚ...` vs
  `...ᛏᛝᛁ-ᛗᛝᚣᚪᚫ-ᛝ...` — the word boundary after ᛁ aligns, ᛗᛝᚣᚪ is
  word-initial in both, and the match diverges where the two words would
  diverge (consistent with two plaintext words sharing a 4-rune prefix
  encrypted from the same state).
- The ciphertext *before* the phrase differs in both occurrences, so the
  matching key state arose from different recent history: the state is
  either a short-memory function of local plaintext or a draw from a
  finite pool that collided. It is not a long-window hash of everything
  preceding.

## Significance

- Expected repeated 6-grams in 12,956 random runes: 0.14 (observed: only
  this one, plus its sub-grams). The earlier 7-gram expectation (0.005) is
  retired with the 7-gram framing — see the Claim.
- Monte Carlo with the real word-length structure and the doublet-corrected
  Markov null (`experiments/anchored_repeats.py`, clean corpus): a
  word-anchored, boundary-consistent repeated run of length >= 6 appears in
  ~1.0% of samples. Counting both observed runs,
  P(count >= 2 of length >= 5) = 0.058.
- A trigraphic-kappa scan over all shifts flags shift 6395 as the
  strongest outlier (4 hits vs 0.3 expected, z = +7.2); all 4 hits are the
  consecutive trigrams of this single 6-gram, so the kappa scan is only the
  detector — the significance figures above come from the maximal-repeat
  framing, which correctly treats the 6-gram as one event.

## Negative results that bound the mechanism

The event-local probes below were measured on the 13,041-rune stream
(parable excluded, solved AN END page still included); the 85 extra runes
sit far from both occurrences and cannot affect them. The corpus-wide
batteries under "Additional negative space" were re-run on the clean
12,956-rune stream (July 2026) with unchanged conclusions:

| probe | result |
|-------|--------|
| local kappa profile at shift 6395 around the match | flat outside the matched runes — the alignment dies with the 6-gram (plus the 1/29 boundary coincidence); keystreams do NOT stay aligned |
| structural coordinates | unrelated: section 8+28 vs 14+302, page offset 28 vs 70, line offset 8 vs 2 — no restart alignment |
| preceding words | ambiguous: the word before the second occurrence wraps across a line (ᚳᛠᛁᛗ\|ᚳᛉ). Merging the wrap, the preceding words differ (2 vs 6 runes), arguing against key = f(previous plaintext word). Treating the line break as a boundary, both preceding fragments are 2 runes (ᛒᚠ vs ᚳᛉ) — which a word-keyed model would predict |
| shifted key reuse (repeats in the delta stream, len >= 6) | only this same phrase (shift 0) — no Vigenere-style reuse at a nonzero additive offset |
| reversed / atbash / atbash-reversed common substrings (len >= 6) | none (0 observed, 0.29 expected each) |
| global identical-word pairs | 289 observed vs 317 expected from chance — word repetition is otherwise at the random rate, so this is NOT a codebook |
| keystream-restart alignment of sections/pages/lines/words | no coincidence excess (the small line-aligned excess is the layout artifact, column 0 only) |

## How much does this repeat actually weigh? (September 2026)

The two readings must be priced against the DATA, not against each other's
mechanisms. Under a plain walk the observed repeat is far more likely to be a
chance collision of two DIFFERENT plaintext phrases than a genuine base return:
the Monte Carlo above gives 1.0% for the collision, while a genuine six-point
return in a walk group of ~4×10³⁰ runs at 1.4×10⁻⁶. So P(data | walk) = 0.010.
Under a cipher whose base takes N values, genuine returns add ≈ 529/N, the
repeated-two-word-phrase pressure of an LP-sized prose corpus:

| N | P(genuine return) | P(data \| compact) | P(data \| walk) | likelihood ratio |
|---|---|---|---|---|
| 2,000 | 0.265 | 0.275 | 0.010 | 27.5 |
| 4,205 | 0.126 | 0.136 | 0.010 | 13.6 |
| 20,000 | 0.026 | 0.036 | 0.010 | 3.6 |

**4 to 28, not the 10⁴ once claimed** (`dju-bei-gate-validity.md`, which made and
then corrected that error). The end-of-text position of the second occurrence
adds 3 to 10 more — a prior about whether closing words are formulaic, not the
~100 its raw rarity suggests. Against that, the architecture a recurring state
would need spends 88 of the 103 bits available in a base (below). The event is
suggestive and does not settle anything.

## What a recurring state would have to look like

`dju-bei-gate-validity.md`, `experiments/compact_base_cycle.py`. If the state does
recur, the base takes a few thousand values, and three constraints bite at once:

- **Consecutive bases cannot be independent.** An unrelated base per state puts the
  cross-word doublet at 0.0355, the chance rate, against the observed 0.0079 —
  101 predicted, 23 observed, z = −7.8. The difference between consecutive bases
  must be a rare-diagonal permutation.
- **The branching factor is about two.** A random permutation's seam diagonal lands
  in the observed interval with probability 1.14×10⁻³, so a tuned relation costs 9.8
  bits against the 102.8 in one base. The transition must depend on the word's length
  class to keep the base well defined, giving 5d relations per state, so d ≤ 2: the
  plaintext feature driving the state carries about one bit per word.
- **The bases cannot be powers of one permutation.** That is the only cheap way to
  tune every edge at once, and it fails: `π^h` and `π^h'` agree wherever `h − h'` is
  divisible by a cycle length, so two states share ~4 of 29 images where independent
  permutations share 1. Measured — identical cipher words 144 against 17, long
  repeats 34 against 0, unigram IoC 1.033 against 1.000.

## Implications

1. **A position-unique keystream is disfavoured, at 4-28 to 1.** A true running key
   or OTP over the whole book leaves this event the ~1% accident measured above.
   That is evidence against, not a refutation, and the earlier wording here
   ("any viable hypothesis must let the internal state return") was too strong.
2. **Recurrence is word-aligned.** Both anchored repeats begin at word
   starts and their divergence points sit at plausible plaintext word
   divergences. This favors mechanisms where state interacts with word
   structure (word-influenced autokey, finite per-word key states) over
   pure rune-stream mechanisms.
3. **The depth is short and isolated.** The state must diverge again
   immediately after the phrase (within 1 rune) — consistent with
   plaintext-driven state (the plaintexts diverge after the phrase) and
   inconsistent with long reused key blocks.
4. Combined with the flat global statistics, the cipher behaves like a
   deterministic, plaintext-and-state-driven stream whose state space is
   large enough to look random everywhere except (a) adjacent repeats
   (doublet suppression) and (b) rare exact state collisions on repeated
   plaintext phrases.

## Additional negative space (deep scans, June 2026)

Later batteries widened the search and came back flat, which tightens the
constraint set further (`experiments/deep_scan.py`,
`experiments/covert_channels.py`):

- **Word-length channel**: word lengths are cipher-independent plaintext
  evidence. The longest repeated word-length run is 7 words — exactly the
  shuffled-null expectation. The plaintext repeats no passage of >= 8
  words; the DJU-BEI repeat is a short phrase, not part of a repeated
  paragraph.
- **Doublet covert channel**: the 86 doubled runes are uniform
  (nIoC 0.976), their gaps mod 29 uniform, and no shift/flip maps their
  frequencies onto runeglish (P=0.30 vs uniform-random baseline). The
  doublets do not carry a direct hidden message.
- No cross-correlation with the solved pages' rune stream at any of
  15,354 alignments (no pad/keystream sharing with solved sections).
- No affine-class key reuse (length >= 8), no Beaufort-style reuse
  (delta vs negated/reversed delta), no bigram antisymmetry, no
  word-counter periodicity of word-initial/final runes (k <= 60), no
  positional drift per rune (KS), sections statistically homogeneous,
  no embedded all-29 key table window, sentence-initial/final runes
  uniform, word-length sequence spectrum white.

## Is there another DJU? (uniqueness census, July 2026)

`experiments/dju_uniqueness.py`:

- **ᛞᛄᚢ occurs exactly twice in the clean corpus, and is followed by
  ᛒᛖᛁ both times**; ᛒᛖᛁ likewise occurs exactly twice, always after
  ᛞᛄᚢ. Neither word appears anywhere else.
- **No graded family of near-collisions.** Comparing all 16,653 pairs of
  adjacent 3+3 word blocks by positional agreement gives
  {0: 13516, 1: 2845, 2: 274, 3: 17, 4: 0, 5: 0, 6: 1} against chance
  expectations {3: 12.3, 4: 0.33, 5: 0.005, 6: 3e-5}. Everything below
  4 sits at chance and there is nothing at 4 or 5: the state return is
  an isolated all-or-nothing event, not the tip of a family of
  near-returns. (This also re-derives the event's rarity — ~1 in 35,000
  — from a fresh, 3+3-restricted angle.)
- **Word repetition generally is at chance**: 15 repeated words of
  length ≥ 3 (one of them thrice, ᛠᚱᛇ), against ~11-12 expected pairs.
  Consistent with `word-transform-census.md`.
- **The ᛞᛄ prefix cluster — catalogued, and it is chance.** Four further
  3-rune words begin with the same digraph (ᛞᛄᚩ, ᛞᛄᚳ, ᛞᛄᚷ, ᛞᛄᛝ), so six
  of the 726 three-rune words share that prefix where 0.86 is expected.
  The full catalog (script section D) scores the prefix distribution
  against **doublet-aware surrogates** — necessarily, since a prefix is
  an adjacent within-word pair, so the 29 diagonal cells are suppressed
  (the corpus has 3 doublet-prefixes where a uniform 841-cell null
  expects 25, pushing ~22 words onto the other 812 cells; a uniform null
  here is the fifth instance of the doublet-suppression trap). Against
  2,000 surrogates with the real word structure: distinct prefixes 485
  vs 482.6 ± 8.7 (z = +0.3), prefix-sharing pairs 342 vs 320 ± 18
  (z = +1.2), **max cell 6 vs 5.1 ± 0.7 (z = +1.3, p = 0.22)** — a
  six-word prefix is entirely ordinary — and doublet-prefixes 3 vs
  5.0 ± 2.2. Only the tail count leans: five cells hold ≥ 5 words
  against 1.8 ± 1.3 (p = 0.033), post-hoc. ᛞᛄ is not alone at the top
  either: ᚾᚷ also has six. The restriction to 3-rune words was chosen
  *because* DJU is 3 runes; over all lengths ᛞᛄ's count (9) is
  unremarkable against a maximum of 10. Under the walk a shared 2-rune prefix needs only two
  base values to agree, so these are cheap coincidences, not partial
  state returns — confirmed by the third runes inside each group, which
  collide at chance (the one exception being the corpus's only
  thrice-repeated word, ᛠᚱᛇ, in the ᛠᚱ group).

## What the constraint pins (and what it does not)

Both words are 3 runes, so the within-word phase reaches only `g⁰, g¹,
g²`: the six agreeing runes say nothing directly about `g³` or `g⁴`. The
mod-5 arithmetic in the abelianization constraint comes from `g⁵ = id`
(exponents matter only mod 5) applied to the exponent accumulated by the
BASE schedule over the 1,449 intervening word boundaries — not from any
word reaching length 5. The constraint therefore binds the base schedule
and the g/σ relation, not g's internal structure. See
`length-clocked-walk.md`.

**And it binds far less than that phrasing suggests.** `[g] = −1449·[σ]`
holds in the abelianization of the *free* group on two generators. For
concrete permutations it says something only if ⟨g,σ⟩ has a matching
abelian quotient, and it does not: |G/G′| measures 1 or 2 across sampled
order-5 `g` with random and 29-cycle σ, because these groups are A₂₉/S₂₉
or point stabilizers thereof. The relation collapses to the parity
condition, and for a 29-cycle (Quagmire) σ parity is automatic. It is a
valid constraint only where the group is genuinely abelian — under the
σ = g^k assumption of `sigma-power-step.md`. For a general key the only
testable content of this repeat is the **state return** `base_1477 =
base_2926`, which requires the full 1,449-step composition. See
`mixed-alphabet-vigenere.md` for the measurements.

## What is upstream of each occurrence? (August 2026, Michel's question)

`experiments/djubei_context.py`. The "preceding words differ" note above was
ambiguous under the line wrap; asked properly, on the channel that drives the
walk, the answer is clean.

**Nothing is shared right before.** The walk is clocked by word lengths, so a
matching recent `(L−1) mod 5` run would mean the state agreement was inherited
rather than coincidental. It is not:

| channel | occ1 | occ2 | shared suffix |
|---|---|---|---|
| preceding word length | 2 | 6 | 0 words |
| preceding `(L−1) mod 5` | 1 | 0 | 0 words |
| preceding last rune | ᚠ | ᛉ | 0 words |

The running exponent sum mod 5 disagrees at every depth tested (1, 2, 3, 5, 10,
20 words back). So the two states arrived at the same value along genuinely
different clocks — the return is a true collision of the walk, not a locally
inherited agreement. This is the word-level confirmation of the "differing
recent history" row in the table above.

**But both occurrences are 13-dot adjacent, in complementary positions.**
Under the `[rubricated title][13-dot][body]` section model:

- **occ1 opens a section body** — 2 words after the 13-dot that closes a title
  (`… ᛚᛋᚳᛈ ⑬ ᚾᚻᚷᚢᛡᚻᚢ ᛒᚠ ᛞᛄᚢ ᛒᛖᛁ …`), itself 5 words after the `&$%` break.
- **occ2 closes a section body** — ᛒᛖᛁ is immediately followed by a 13-dot and
  the `&$%` break, then the next title (`… ᚳᛉ ᛞᛄᚢ ᛒᛖᛁ ⑬ &$% ᚫᛄ ᛟᛋᚱ ⑬ …`).

Calibration against the corpus's other repeats: 4.7% of words sit within 3 of a
body start or end, so a random pair is doubly-adjacent 0.2% of the time. Of the
13 other repeated-word classes (length ≥ 3), **zero** have all occurrences
boundary-adjacent, at every window from 0 to 6 — DJU-BEI is the only one, and
its adjacency is stable across that whole window range.

**Post-hoc caveat**: the boundary definition and window were chosen after
reading the two contexts, so the ~p = 0.03 this implies is optimistic. The 13
other classes are calibration, not pre-registration.

Two consequences:

1. **It sharpens the anti-per-section-reset argument.** occ1's base sits ~2
   word-steps from a section start and occ2's ~300 steps into its section; a
   per-section reset would have to make those coincide by accident. The
   "differing structural coordinates" row said this loosely — the section-model
   reading makes it specific.
2. **It is crib-shaped.** A 3+3 refrain that opens one section body and closes
   another is formulaic placement, which is exactly the register the ~31 title
   slots draw on (`rubrication-crib-candidates.md`). DJU-BEI was previously
   unguessable because a short phrase cannot be verified
   (`length-clocked-walk.md`); a *positional* constraint on what kind of phrase
   it is narrows the candidate list independently of the cipher.

## Index manipulations of the preceding runes, and why they must fail

`experiments/djubei_delta_context.py` (August 2026, Michel's question). The
looser question: are the two preceding rune streams related by *some*
transformation of the indices, even though they are not equal?

Battery over the 25 runes before each occurrence, each statistic being the
longest suffix on which the relation holds, calibrated against the same
statistic over 40,000 random word-start pairs:

| relation | observed | null mean | P(≥obs) |
|---|---|---|---|
| identity | 0 | 0.03 | 1.000 |
| constant offset (= delta-stream match) | 1 | 1.04 | 1.000 |
| constant sum (Beaufort) | 1 | 1.04 | 1.000 |
| affine `a·x+b` (all 812) | 2 | 2.02 | 0.987 |
| reversed | 0 | 0.03 | 1.000 |

**Family-blind P = 0.987.** Every cell sits at or below its null mean — the
preceding streams are not related by any of these. Gematria-style summaries
(sum and product of the last 3/5/10/20 runes mod 29) likewise disagree in
every cell. Note delta-stream agreement over a window *is* constant-offset
over that window, so those are one test; the global version of this search is
already in `alignment_scan.py`.

**And the model explains why, exactly.** From `base_{w+1} = base_w ∘ g^{a_w} ∘
σ` we get `base_w = base_{w+1} ∘ σ^{-1} ∘ g^{-a_w}` (verified numerically for
arbitrary keys against `step_products`). Stepping back k words from each
occurrence multiplies by `σ^{-1}g^{-a}` down the two `a = (L−1) mod 5`
sequences. These agree up to a power of `g` only while the sequences agree,
except in the oldest term — a mismatch earlier leaves a `g`-power sandwiched
between `σ`'s, which generically does not simplify.

The two sequences are `[1,1,3,1,2,…]` and `[0,1,1,1,1,…]`: **they differ
immediately**, so the state return reaches exactly **one word** backward, as

```
base_1476 = base_2925 ∘ g^(-1)
```

which yields precisely three key-free comparisons — `c1[j]` vs `c2[j']` with
`(j−1) mod 5 = j' mod 5` is an equality iff the plaintext letters are equal:
ᛒ vs ᚳ, ᚠ vs ᚳ, ᚠ vs ᛉ, all three saying only *"these plaintext letters
differ"*.

So the preceding ciphertext carries three bits of weak plaintext information
and nothing else, and no index arithmetic could have related the streams: the
walk's bases are mixed permutations, so a constant-offset or affine relation
would have required an additive cipher, which the algebra battery already
excludes globally (`length-clocked-walk.md`, "No algebraic structure
anywhere"). The negative is a prediction of the model, not a surprise.

(The forward direction is where the retracted 7-gram framing lives — occ2's
continuation crosses a section break into differently-enciphered material —
so it is deliberately not analysed here. See the Claim.)

## Scripts

- `experiments/djubei_delta_context.py` — the index battery and the
  backward-reach derivation.
- `experiments/djubei_context.py` — the upstream/boundary comparison above.
- `experiments/anchored_repeats.py` — boundary-consistent anchored repeat
  census + Monte Carlo null (the headline p-value).
- `experiments/phrase_repeats.py` — adjacent-word-pair repeat census.
- `experiments/residual_tests.py` — trigraphic kappa scan that flags shift
  6395.
- `experiments/alignment_scan.py` — restart-alignment and delta-stream
  probes.

## Related

- `word-level-autokey.md` — word-aligned recurrence is weak positive
  evidence for this class (but key != previous word verbatim).
- `stream-cipher-no-repeat.md` — any stream model must now allow exact
  state recurrence.
- `running-key-text.md` / `running-key-math-sequence.md` — a non-repeating
  running key is disfavored by this observation.
- `doublet-spacing-poisson.md` — the other confirmed characterization.

## Verdict

Confirmed characterization of the repeat itself: the ciphertext contains one
word-aligned exact repeat of 6 runes, in boundary-consistent positions, plus a
second candidate that does not clear chance on its own. The depth dies within one
rune of the phrase end and the two occurrences arrive along different clocks.

**What it implies is weaker than this file used to say.** Chance explains it in 1.0%
of surrogate corpora, so a recurring key state is favoured by 4 to 28, and the
end-of-text position by 3 to 10 more. Position-unique keystreams are disfavoured at
those odds rather than excluded; plaintext-driven state machines with a finite state
pool are favoured at them, and must additionally branch about two ways with
near-independent bases, which no known construction supplies.

## Does 1449's factorisation help? (August 2026 — no, and here is the scope)

1449 = 3² · 7 · 23, and unlike 31 (a candidate raised and dropped the same day, prime
and > 29 so unachievable) both 7 and 23 ARE achievable permutation orders on 29
points. So `ord(σ) | 1449`, which would make `σ^1449 = id`, is not absurd.

It buys nothing, for two reasons of different strength.

**Outside the normaliser branch it is simply irrelevant.** The 1449 steps are
`g^{e_i} σ` and do not commute, so they never collect into `g^k σ^1449`; the
divisibility of the step count says nothing about the product.

**Inside the normaliser branch it is refuted.** If `σ g σ⁻¹ = g^r`, the product does
collect and the constraint becomes `g^k σ^1449` with `k = Σ aᵢ rⁱ mod 5`. But σ's
image in Aut(Z/5) ≅ Z/4 has order dividing both ord(σ) and 4, and every divisor of
1449 is ODD — so gcd(ord(σ), 4) = 1, the image is trivial, and **r = 1 is forced**.
The commuting case gives k = Σ aᵢ = 4946 ≡ 1 mod 5, so the residue is `g¹`, which
fixes exactly 4 points (cycle type 5⁵1⁴) — fewer than the **6** this repeat requires.

Note the constraint being tested is the PARTIAL one (agreement on 6 plaintext image
points), not a full return; the full-return reading was the 10²²-too-strict filter
retracted elsewhere in this file. A first pass at this compared against the full
return and then argued from a register-dependent base count, both of which the
group-theoretic argument supersedes.
