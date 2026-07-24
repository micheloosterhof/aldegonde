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

This proves the cipher's **key state recurs exactly**, and that the
recurrence is **word-aligned**. The encryption is a deterministic function
of plaintext and a state that can return to a previous value — it is not a
position-unique running key.

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
| local kappa profile at shift 6395 around the match | flat outside the 7 runes — the depth is exactly 7, keystreams do NOT stay aligned |
| structural coordinates | unrelated: section 8+28 vs 14+302, page offset 28 vs 70, line offset 8 vs 2 — no restart alignment |
| preceding words | ambiguous: the word before the second occurrence wraps across a line (ᚳᛠᛁᛗ\|ᚳᛉ). Merging the wrap, the preceding words differ (2 vs 6 runes), arguing against key = f(previous plaintext word). Treating the line break as a boundary, both preceding fragments are 2 runes (ᛒᚠ vs ᚳᛉ) — which a word-keyed model would predict |
| shifted key reuse (repeats in the delta stream, len >= 6) | only this same phrase (shift 0) — no Vigenere-style reuse at a nonzero additive offset |
| reversed / atbash / atbash-reversed common substrings (len >= 6) | none (0 observed, 0.29 expected each) |
| global identical-word pairs | 289 observed vs 317 expected from chance — word repetition is otherwise at the random rate, so this is NOT a codebook |
| keystream-restart alignment of sections/pages/lines/words | no coincidence excess (the small line-aligned excess is the layout artifact, column 0 only) |

## Implications

1. **The keystream is not position-unique.** A true running key / OTP over
   the whole book would make this event pure chance (p < 1e-3). Any viable
   hypothesis must let the internal state return to an earlier value.
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
- **Curiosity, not a finding**: four further 3-rune words begin with the
  same digraph ᛞᛄ (ᛞᛄᚩ, ᛞᛄᚳ, ᛞᛄᚷ, ᛞᛄᛝ), so six of the 726 three-rune
  words share that prefix where 0.86 is expected. But the prefix
  distribution as a whole is normal — two cells reach 6 (ᚾᚷ as well)
  against 0.23 expected, nominal p ≈ 0.02 for the max-statistic, and the
  restriction to 3-rune words was chosen *because* DJU is 3 runes. Over
  all word lengths the ᛞᛄ prefix count (9) is unremarkable against a
  maximum of 10. Under the walk a shared 2-rune prefix needs only two
  base values to agree, so these are cheap coincidences, not partial
  state returns.

## What the constraint pins (and what it does not)

Both words are 3 runes, so the within-word phase reaches only `g⁰, g¹,
g²`: the six agreeing runes say nothing directly about `g³` or `g⁴`. The
mod-5 arithmetic in the abelianization constraint comes from `g⁵ = id`
(exponents matter only mod 5) applied to the exponent accumulated by the
BASE schedule over the 1,449 intervening word boundaries — not from any
word reaching length 5. The constraint therefore binds the base schedule
and the g/σ relation, not g's internal structure. See
`length-clocked-walk.md`.

## Scripts

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

Confirmed characterization. The ciphertext contains one word-aligned exact
repeat that random chance cannot reasonably explain (plus a second,
boundary-consistent candidate that does not clear chance on its own).
The cipher's key state recurs, recurrences are word-aligned, and the depth
dies within one rune of the phrase end. Hypotheses that make identical
ciphertext for identical plaintext impossible (position-unique running
keys) are disfavored; hypotheses where state is derived from bounded local
context (plaintext-driven state machines, word-keyed schemes with a finite
state pool) are favored.
