# Characterization: Full Cryptodiagnostic Battery on page0-58.txt (2026-06)

## Claim

A comprehensive diagnostic battery (`experiments/lp_cryptodiagnostics.py`)
re-verified the known statistical profile, found that the corpus is
**contaminated with solved/plaintext material**, corrected the word count,
added several new **rule-outs** (reverse-direction autokey, prime-shift at any
offset, key reuse at any alignment, running keys from available texts,
word-keyed determinism), and surfaced two **positive leads**: a word-aligned
repeated two-word phrase, and a within-word distance-5 coincidence excess
concentrated in length-10 words.

## Status

**Status**: confirmed (characterization)

## Corpus corrections (affect every other hypothesis file)

1. **Contamination.** `data/page0-58.txt` is not all unsolved ciphertext.
   Splitting on `$` (12 rune-bearing sections, lengths
   729, 1145, 1729, 9, 1894, 1021, 1524, 1589, 3008, 308, 85, 95):
   - **Section 10 (85 runes) is the solved AN END page**: it decrypts with
     `P = C - (p_n - 1) mod 29` (primes 2, 3, 5, ... starting fresh at the
     section) to "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES
     TO ..." — confirmed by direct decryption.
   - **Section 11 (95 runes) is the unencrypted Parable**: "PARABLE. LIKE THE
     INSTAR, TUNNELING TO THE SURFACE ..." readable as-is.
   - Section 3 is a 9-rune title above the number grid, not running text.
   - The **clean unsolved cipher corpus is sections 0-9 = 12,956 runes**.
     Headline stats on the clean corpus: flatness chi-sq p=0.553,
     IOC=0.03448, H=4.8565 bits, **86 doublets** (expected 447,
     x5.19 suppressed), 0 triplets. The previously documented "89 doublets"
     includes 3 from solved/plaintext pages (e.g. the NN in "tunneling").
2. **Word count.** The README's "3,367 words" treats `/` (line wrap) as a
   word boundary. It is not: in the readable master-transcription section,
   words demonstrably span `/` ("ᛋᚪᚳ/ᚱᛖᛞ" = SAC/RED, "ᛖᚾᚳᚱᚣ/ᛈᛏᛖᛞ" =
   ENCRY/PTED). The correct tokenization (boundaries `- . % & $`, continuation
   `/` and newline) gives **2,973 words, mean length 4.42** (length
   distribution 1:100, 2:478, 3:734, 4:524, 5:321, 6:256, 7:218, 8:160, 9:77,
   10:51, 11:28, 12:18, 13:4, 14:4).
3. The unsolved corpus begins at rune offset 2,797 of the master
   transcription (15,933 runes total).

## Verified profile (clean corpus)

| Property | Value |
|----------|-------|
| Unigram flatness | chi-sq p = 0.55, min/max count 400/493 |
| Entropy | H1 = 4.8565 of 4.8580 bits; H(X2\|X1) = 4.786 |
| IOC mono/di/tri | 0.03448 / 0.00122 / 0.0000427 — all at random |
| Doublets | 86 (x5.19 suppressed); 0 triplets |
| Kappa skips 2-60 | all normal (skip 11 z = -2.8, isolated, noise-level) |
| Bigram asymmetry count(a,b) vs count(b,a) | chi-sq p = 0.21 |
| Compression (zlib/bz2/lzma) vs shuffled | z = +0.2 / -0.1 / -0.6 — zero redundancy |
| Mutual information at lags 1-58 | only lag 1 elevated (the doublet deficit) |
| Sliding-window IOC / doublet rate | homogeneous across all sections 0-9 |

The doublet suppression is the **only** detectable deviation from uniform
randomness at the rune level. The delta-1 stream restricted to nonzero values
is marginally non-flat (chi-sq p = 0.026, df 27) — weak, worth one re-check on
new data, not load-bearing.

## New negative results (rule-outs)

1. **Reverse-direction ciphertext autokey**: splitting C[i] by the *following*
   rune C[i+1] gives mean group IOC 0.0354 (max 0.0364) — random. The forward
   split disproof (`ciphertext-autokey.md`) now holds in both directions.
   Splits by C[i±L] for L = 1..12 are all random too: no lagged autokey.
2. **Prime/totient shift at any starting offset**: decrypting every section
   with `C ∓ (p_{n+k} - 1)` for all offsets k = 0..15,999 and both signs never
   beats IOC 0.0365 (a hit would be ~0.06). The page-56 cipher does **not**
   extend to any unsolved section with a shifted prime index.
3. **Keystream reuse at any alignment**: difference IOC (Vigenere-style) and
   sum IOC (Beaufort-style) of the corpus against itself at every lag
   1..11,956, properly per-lag normalized, show nothing beyond the expected
   noise maximum (|z| 4.5-5.3 over 24k tests); the isolated near-threshold
   blips do not reproduce as coherent alignments in focused per-section
   re-scans. Cross-section diff/sum IOC at offset 0: nothing. The key, if
   any, is never reused — within or across sections.
4. **Running key from available texts**: the Parable (forward and reversed)
   and the entire master transcription, slid across the clean corpus at every
   alignment in both Vigenere and Beaufort sense: max |z| 6.2, but
   shuffled-key null scans reach 5.2-8.4, so this is noise (and the best-hit
   "decrypt" is gibberish).
5. **Word-keyed determinism**: repeated ciphertext words match the
   shuffled-rune null at every length (e.g. len 3: 16 obs vs 11.1±2.9 null);
   **zero** repeated words of length ≥ 4 in 2,973 words. Any cipher in which
   the same plaintext word in the same key state reproduces the same
   ciphertext word would show an excess; none exists.
6. **Position-in-word structure**: rune distribution and IOC grouped by
   position from word start and from word end (positions 0-5): all flat
   (p = 0.19-0.95, IOC 0.0342-0.0348). IOC per (word length, position) cell:
   0 of ~60 cells flagged at |z| > 3. First-rune and last-rune distributions
   flat. Word sums mod 29 flat (p = 0.65). Gematria-Primus word sums show no
   excess primality vs null (z = -0.06). Single-rune words: 100 of them take
   all 29 values, IOC 0.0311.
7. **Word-feedback keying**: grouping runes by (previous word's sum mod 29,
   position) and by (previous word's last rune, position): all cell IOCs at
   random. Column streams (all first runes, all last runes, all second runes)
   are individually uniform with no adjacent-coincidence anomaly.
8. **Interleaving**: streams taken at index mod k (k = 2..5) each show normal
   doublet rates — the cipher is not an interleave of differently-behaved
   streams.

## Positive leads

### Lead 1: the word-aligned repeated phrase ᛞᛄᚢ-ᛒᛖᛁ

The corpus's single longest repeat is a **7-gram** that is exactly **two
complete words plus the first rune of the next word**, identically aligned in
both copies:

```
... ᛒᚠ      | ᛞᛄᚢ ᛒᛖᛁ | ᚫᚠ ...      position 6555, section 6, words 1477-78
... ᚳᛠᛁᛗᚳᛉ | ᛞᛄᚢ ᛒᛖᛁ | ᚫᛄ ...      position 12950, section 9, words 2926-27
```

- Both copies are word-initial, with the same 3+3 word-length split, and the
  following word starts with the same rune (ᚫ) both times.
- Distance: 6,395 runes = 5 × 1279 (1279 prime); 1,449 words apart.
- The second copy is the **last two words of section 9**, immediately before
  the section break that precedes the solved AN END page.
- Chance expectation for any repeated 6-gram in 13k runes is ~0.1 pairs
  (observed repeated 6/7-grams are all inside this one phrase); the word
  alignment makes it rarer still. This is a p ≈ 0.005-level event.
- Under any continuous stream/running-key model this requires the keystream
  to repeat exactly when the plaintext repeats — i.e. it favors mechanisms
  with **word-level state that can coincide** (the same two plaintext words
  encrypted under a recurring word-level key state), and disfavors pure
  position-keyed streams.

### Lead 2: within-word distance-5 coincidence excess

Coincidence rate at distance d between runes **of the same word**:

| d | hits/trials | z |
|---|-------------|---|
| 1 | 65/10163 | -15.5 (doublet suppression) |
| 2 | 256/7290 | +0.3 |
| 3 | 182/4895 | +1.0 |
| 4 | 132/3234 | +2.0 |
| 5 | **104/2097** | **+3.8** |
| 6 | 32/1281 | -1.9 |

Cross-word pairs at distance 5 are *exactly* random (377/10,878 = 3.466%);
the excess lives only inside words. By word length it concentrates in
**length-10 words: 21/255 = 8.2%, exact P = 2.4e-4**. The clean
half-length-key prediction (excess at d = L/2 for all even L) **fails** —
L=6/d=3, L=8/d=4, L=12/d=6 are normal — so the mechanism, if real, is
specific to d=5.

**Update (verified)**: this lead survived rigorous re-verification —
decontamination, a boundary-permutation null that preserves the entire rune
stream (p = 0.0014, only d=5 fires among d=1..8), per-section consistency
(8 of 9 sections positive), spread over 91 distinct words, and a sharper
sub-statistic: nine words repeat a bigram/trigram at distance exactly 5
(`XY···XY`), vs 2.8 ± 1.6 under the permutation null (p = 0.0019) and 1.5
under uniform randomness. Full writeup with all numbers:
`within-word-d5-coincidence.md`; reproduction:
`experiments/within_word_d5.py`.

### Minor notes

- One identical adjacent word pair exists ("ᛞᛝ ᛞᛝ" at word 399); expected
  ~0.1 by chance — mildly notable, consistent with Lead 1's flavor.
- Doublet micro-structure is featureless: doublet rune values uniform over
  the alphabet (p = 0.47), context runes uniform, within/cross-word split
  proportional to opportunity, gaps exponential (KS p = 0.74) — all
  consistent with `doublet-spacing-poisson.md`.

## Implications for open hypotheses

- `ciphertext-autokey.md`: now also disproved in the reverse direction and
  at lags up to 12.
- `running-key-text.md`: parable and master transcription ruled out as key
  texts at all alignments; solved-section *plaintexts* other than these
  remain untested.
- `gematria-primus-arithmetic.md` / prime-shift extensions: the AN END
  mechanism exhaustively fails on all unsolved sections for any prime-index
  offset.
- `word-level-autokey.md` / `position-within-word.md`: no positional or
  word-feedback statistic deviates — but Lead 1 (repeated phrase) is exactly
  the kind of event a word-level-state cipher would occasionally produce,
  and is very hard for continuous-stream models. These two leads point the
  same direction: **word-scoped key state**.
- `stream-cipher-no-repeat.md`: survives everything here at the rune level,
  but offers no account of Lead 1 or Lead 2.

## Scripts

- `experiments/lp_cryptodiagnostics.py` — reproduces every number above
  (sections A-G fast; H runs the heavy offset/lag/running-key scans).

## Related

- `doublet-spacing-poisson.md`, `ciphertext-autokey.md`,
  `running-key-text.md`, `word-level-autokey.md`,
  `position-within-word.md`, `running-key-math-sequence.md`.

## Verdict

Confirmed characterization. The clean unsolved corpus (sections 0-9,
12,956 runes) is statistically indistinguishable from uniform randomness
except for (a) the x5.19 doublet suppression with zero triplets, (b) one
word-aligned repeated two-word phrase 6,395 runes apart, and (c) a
within-word d=5 coincidence excess centered on 10-rune words. Every tested
periodic, autokey (both directions, lags 1-12), prime-shift (all offsets),
key-reuse (all alignments), running-key (available texts), positional,
word-feedback, and interleave mechanism is ruled out. The surviving
hypothesis space is narrow: a non-repeating keystream or word-state cipher
whose only leaks are the doublet deficit and rare word-level key-state
coincidences.
