# Characterization: The Repeated Phrase ᛞᛄᚢ-ᛒᛖᛁ (Key-State Recurrence)

## Claim

The unsolved ciphertext contains a repeated 7-rune sequence **ᛞᛄᚢᛒᛖᛁᚫ**
("DJU BEI AE") at rune offsets **6555 and 12950** of `data/page0-58.txt`
(distance 6395), with **identical word boundaries** in both occurrences
(ᛞᛄᚢ-ᛒᛖᛁ-ᚫ…, word-initial both times). Under a doublet-corrected random
model this has p < 0.001. A second, weaker boundary-consistent repeat
**ᛁ-ᛗᛝᚣᚪ** occurs at offsets 10671/12764 (distance 2093).

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
  in both places (word indices 1477/2926 of 2953).
- The second occurrence is the **final two words of its section**, ending
  with a sentence stop. The 7th matching rune ᚫ is then the *first rune of
  the next section* — if sections are independent units this last rune is a
  1/29 bonus coincidence; if the stream is continuous the depth is 7.
- The secondary repeat: `...ᛝᛉᛞᛁ-ᛗᛝᚣᚪᛝᚠᛉᛁᛟᚷᛚ...` vs
  `...ᛏᛝᛁ-ᛗᛝᚣᚪᚫ-ᛝ...` — the word boundary after ᛁ aligns, ᛗᛝᚣᚪ is
  word-initial in both, and the match diverges where the two words would
  diverge (consistent with two plaintext words sharing a 4-rune prefix
  encrypted from the same state).

## Significance

- Expected repeated 7-grams in 13,041 random runes: 0.005. Expected
  repeated 6-grams: 0.14 (observed: only this one, plus its sub-grams).
- Monte Carlo with the real word-length structure and the doublet-corrected
  Markov null (`experiments/anchored_repeats.py`, 1000 samples): a
  word-anchored, boundary-consistent repeated run of length >= 7 appeared in
  **0 of 1000** samples (length >= 6: 1.0%). Counting both observed runs,
  P(count >= 2 of length >= 5) = 0.075; the joint configuration (one len-7 +
  one len-5) is < 1e-3.
- The trigraphic-kappa scan over all 6,517 shifts flags shift 6395 at ~9
  sigma; it is the only shift whose excess survives multiple-comparison
  correction, and all of its hits come from this single repeat.

## Negative results that bound the mechanism

All measured on the 13,041-rune cipher stream (parable excluded):

| probe | result |
|-------|--------|
| local kappa profile at shift 6395 around the match | flat outside the 7 runes — the depth is exactly 7, keystreams do NOT stay aligned |
| structural coordinates | unrelated: section 8+28 vs 14+302, page offset 28 vs 70, line offset 8 vs 2 — no restart alignment |
| preceding words | differ in length (2 vs 6 runes) — key state is not simply f(previous plaintext word) |
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

Confirmed characterization. The ciphertext contains one (probably two)
word-aligned exact repeats that random chance cannot reasonably explain.
The cipher's key state recurs, recurrences are word-aligned, and the depth
dies within one rune of the phrase end. Hypotheses that make identical
ciphertext for identical plaintext impossible (position-unique running
keys) are disfavored; hypotheses where state is derived from bounded local
context (plaintext-driven state machines, word-keyed schemes with a finite
state pool) are favored.
