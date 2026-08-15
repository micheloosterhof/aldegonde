---
type: hypothesis
---
# Hypothesis: Word-Level Autokey

## Claim

The cipher uses autokey feedback at the WORD level rather than the rune level.
Each word's encryption depends on the previous word (or some function of it),
not the previous rune.

## Status

**Status**: disproved

## Mechanism

Possible forms:
- The key for encrypting word W[i] is derived from the ciphertext of W[i-1]
  (e.g., sum of runes, length, first rune, hash)
- Each word is encrypted with a different shift/permutation determined by
  the previous word
- Within each word, a standard cipher is applied with a per-word key

## Evidence for

- Word boundaries are preserved — the cipher is clearly word-aware
- Defeats the rune-level split test because the key changes per word, not
  per rune
- The 6-gram repeat spans aligned word boundaries, suggesting word-level
  structure (now fully characterized in `repeated-phrase-dju-bei.md`:
  p < 0.001, word-initial both times, plus a second aligned repeat
  candidate ᛁ-ᛗᛝᚣᚪ that does not clear chance on its own. The words *preceding* the two occurrences are ᛒᚠ and
  ᚳᛠᛁᛗ|ᚳᛉ — if the line-wrapped word is merged they differ in length,
  weighing against key = previous plaintext word; if line breaks are word
  boundaries, both preceding fragments are 2 runes, which this model would
  predict)
- ~~Cross-word doublets are more suppressed than within-word doublets~~ —
  corrected: measured properly, the within/cross-word doublet split is
  proportional to opportunity — the within-word rate (0.0063) and the seam
  rate (0.0079) are statistically one rate (z=0.87, p=0.38; pooled 0.0066).
  The suppression is boundary-blind (see
  `cryptodiagnostics-page0-58.md`, `length-clocked-walk.md`)

## Evidence against

- **Additive/affine per-word variants are disproved** by the word transform
  census (`word-transform-census.md`): a constant shift, Beaufort, affine,
  reversal, rotation, or transposition per word would turn the plaintext's
  ~8,000 repeated word pairs into pairs of its transform class; every class
  sits at the doublet-corrected random baseline. Whatever the key schedule,
  the per-word transform cannot be a constant additive/affine map.
- **The general-substitution-per-word survivor is also disproved** by the
  pattern-preservation test in `word-transform-census.md`: any fixed
  per-word substitution, however the key is derived, preserves the
  plaintext's within-word adjacent letter repeats — predicting ~244
  within-word doublets vs 63 observed, an 11.6 sigma deficit. Only
  position-varying keys WITHIN words survive, which is no longer a
  word-level scheme. (The rune-level split test is uninformative here: it
  groups runes by C[i-1], which does not fix a key that varies per word,
  so its random IOC is expected under this variant and disconfirms
  nothing.)
- **Doublet fingerprint** (`experiments/mechanism_fingerprint.py`):
  letterwise variants (previous plaintext word or previous ciphertext word
  cycled as running key) simulated on Markov runeglish with the real LP
  word-length sequence give doublet rates of 3.5-3.8% and 12-21 triplets,
  vs observed 0.66% and 0. No ADDITIVE word-level key schedule can suppress
  doublets, because the key is fixed before the word is emitted and an
  additive key cannot bias which plaintext bigrams collide: suppression
  then requires per-rune feedback from the just-emitted ciphertext (see
  `stream-cipher-no-repeat.md`). The additive form of the
  position-dependent loophole (`position-within-word.md`) fails the same
  constraint. The one feedback-free escape — mixed alphabets whose
  adjacent-alphabet relation is tuned to rare plaintext bigrams — is not a
  per-word-constant key and is tracked in `length-clocked-walk.md`.

- **The keyed BASE is now closed for every simple tap (August 2026,
  `experiments/word_key_tap_battery.py`).** Everything above kills schemes
  where one substitution covers a whole word. It does not reach the variant
  that survives inside the walk: the key still varies by position through
  `g^k`, and only the per-word **base** is autokeyed on some function of the
  preceding text. That variant is untouched by the transform census (the
  per-word transform is not constant) and by the pattern-preservation test
  (within-word repeats are broken by `g^k`, not by the base).

  It has its own signature. Compare two words at the same position `k`: since
  `c_k = base_w(g^k(p_k))`, two words sharing a base agree exactly when their
  plaintext runes agree, so agreement jumps from the flat 1/29 = 0.0345 to the
  runeglish plaintext coincidence rate of about 0.06. Conditioning on the seam
  rune matching therefore predicts a lift of **+0.0255**.

  The tap is unconstrained, so a battery was run. Fourteen candidates, each
  against a null that shuffles its values across words:

  | tap | classes | matched pairs | matches | differs | gap | z | max share |
  |---|---|---|---|---|---|---|---|
  | prev last rune | 29 | 450,048 | 0.0348 | 0.0344 | +0.0004 | +1.33 | 3.8% |
  | prev first rune | 29 | 449,622 | 0.0345 | 0.0344 | +0.0001 | +0.29 | 2.5% |
  | prev sum mod 29 | 29 | 450,127 | 0.0341 | 0.0344 | −0.0003 | −0.94 | 1.1% |
  | prev product mod 29 | 29 | 593,497 | 0.0340 | 0.0344 | −0.0004 | −1.73 | 0.2% |
  | prev GP sum mod 29 | 29 | 449,088 | 0.0345 | 0.0344 | +0.0001 | +0.25 | 2.5% |
  | prev GP product mod 29 | 29 | 625,617 | 0.0348 | 0.0344 | +0.0004 | +1.70 | 3.4% |
  | prev alternating sum | 29 | 449,290 | 0.0344 | 0.0344 | −0.0000 | −0.10 | 2.1% |
  | prev length | 14 | 1,918,715 | 0.0345 | 0.0344 | +0.0001 | +1.01 | 1.7% |
  | prev length mod 5 | 5 | 2,892,700 | 0.0344 | 0.0344 | +0.0000 | +0.39 | 1.1% |
  | prev two words summed | 29 | 449,335 | 0.0346 | 0.0344 | +0.0002 | +0.80 | 3.0% |
  | accumulated rune sum | 29 | 451,460 | 0.0344 | 0.0344 | −0.0000 | −0.03 | 2.3% |
  | rune offset mod 29 | 29 | 448,642 | 0.0342 | 0.0344 | −0.0002 | −0.56 | 1.5% |
  | word index mod 29 | 29 | 445,626 | 0.0343 | 0.0344 | −0.0001 | −0.43 | 1.5% |
  | **random (control)** | 29 | 449,673 | 0.0347 | 0.0344 | +0.0003 | +1.00 | 3.2% |

  A tap that actually keyed the alphabet would sit at **z ≈ 85**. The largest
  |z| in the battery is 1.73, against the 2.7 needed to clear a 14-way scan.

  The negative control is the calibration that matters: a **random** tap scores
  z = +1.00 and a 3.2% share, the same range as the best real tap. The +1.33 on
  the seam rune is the harness's noise floor, not a lean.

  The test degrades gracefully, so each row also bounds *partial* keying: the
  final column is the tap's maximum contribution to alphabet selection, from
  the 2-sigma upper edge of its gap. **No tap can supply more than 3.8%**, and
  that ceiling is set by the noise floor rather than by any signal.

  This is a much more direct measurement than the arguments above — it uses
  every word pair rather than repeated words only, and conditioning on the tap
  concentrates the signal 29-fold. It does not test taps that depend on the
  *plaintext* of the previous word, which is unobservable — those are the base
  keyed on the previous word's plaintext identity, closed directly below.

- **The base keyed on the previous word's PLAINTEXT is now closed directly
  (August 2026, `experiments/word_base_plaintext_closure.py`).** This is the
  one variant neither the tap battery (observable taps only) nor
  `plaintext-autokey.md`'s fixed-lag rune-stream closure reaches: a per-word
  base `base_w = f(previous plaintext word)` for an injective `f`. It has a
  direct signature. With `c = base_w(g^j(p))`, two occurrences of the same
  current plaintext word `Q` that share the same previous plaintext word `P`
  get the same base and the same within-word phases, so `Q` enciphers
  identically — a forced repeated ciphertext WORD. So the forced repeats are
  exactly the recurrences of the plaintext adjacent word-bigram `(P, Q)`,
  independent of `g` and `f`; a non-injective `f` only adds collisions, so the
  injective case is the hardest to kill.

  Measured on the same-author register (recovered solved sections,
  position-preserving systems only so word boundaries are exact: 486 words) and
  scaled to the corpus as pair counts scale — quadratically, the
  `plaintext-autokey.md` convention, here ×36.3 — the recurring plaintext
  word-bigrams predict **~2,500 forced ciphertext word-repeats at current-word
  length ≥ 4, against 0 observed** (`word_repeat_census.py`: length ≥ 4 repeats
  are 0, null ~0). The recurring long-word bigrams are ordinary same-author
  prose — THE MASTER, BE RIGHT, YOUR TRUTH, THE LOSS, OF DIVINITY, BE STRONG,
  WE HAVE — not one header artifact; discarding the instructional refrain
  entirely still leaves ~650 predicted against 0. The kill is register-shape
  independent: any multi-page prose recurs word-bigrams ending in long words.
  Extends to a base keyed on the previous *k* words (forces repeats on
  word-(k+1)-gram recurrence — rarer, but the refrain's trigrams still recur,
  so still killed at length ≥ 4).

## Predictions

~~If word-level autokey with position-within-word dependence: group runes by
(word_key, position_in_word) and check IOC.~~ Mooted: the
pattern-preservation census excludes every fixed per-word substitution
regardless of key derivation, and the additive position-dependent form
fails the doublet constraint, so no variant survives for this grouping to
test.

## Scripts

- `experiments/word_key_tap_battery.py` — conditions word-pair agreement on
  each candidate tap, closing the keyed-base variant for all fourteen.

## Verdict

Disproved. Additive/affine per-word variants fail the word transform
census, and the general-substitution-per-word survivor fails its
pattern-preservation test (11.6 sigma);
letterwise running-key variants fail the doublet fingerprint by 5x;
and the doublet argument holds for any ADDITIVE word-level key schedule:
the key for a word is fixed before its runes are emitted, so it cannot
avoid ciphertext doublets without per-rune output feedback. (Mixed-alphabet
schedules with a bigram-tuned step evade that argument, but those vary the
alphabet per RUNE, not per word — see `length-clocked-walk.md`.)
