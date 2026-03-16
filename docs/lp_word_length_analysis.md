# Liber Primus Word Length and Doublet Position Analysis

## Parsing Method

The Liber Primus transcription uses three delimiters:

| Delimiter | Meaning | Parsing Action |
|-----------|---------|----------------|
| `-` | Word boundary | Split into separate words |
| `.` | Sentence boundary | Split into separate words |
| `/` | Line break (visual only) | **Join** — does NOT break words |

**Naive parsing** treats every non-rune character (including `/` and `\n`) as a word
boundary. **Proper parsing** joins rune fragments across line breaks, only splitting
on `-` and `.`. This distinction matters because some words are split across lines in
the transcription.

## Impact on Word Count

| Parse Method | Word Count |
|-------------|------------|
| Naive       | 4,139      |
| Proper      | 3,671      |

The difference of 468 words comes from line-broken fragments that were incorrectly
counted as separate words under naive parsing.

## Word Length Distribution

### Full Corpus: Naive vs Proper Parse

| Length | Naive | % | Proper | % | Shift |
|--------|-------|------|--------|------|-------|
| 1 | 401 | 9.69% | 128 | 3.49% | -6.2pp |
| 2 | 828 | 20.00% | 645 | 17.57% | -2.4pp |
| 3 | 980 | 23.68% | 902 | 24.57% | +0.9pp |
| 4 | 689 | 16.65% | 646 | 17.60% | +1.0pp |
| 5 | 414 | 10.00% | 374 | 10.19% | +0.2pp |
| 6 | 302 | 7.30% | 317 | 8.64% | +1.3pp |
| 7 | 216 | 5.22% | 261 | 7.11% | +1.9pp |
| 8 | 155 | 3.74% | 184 | 5.01% | +1.3pp |
| 9 | 63 | 1.52% | 92 | 2.51% | +1.0pp |
| 10 | 46 | 1.11% | 60 | 1.63% | +0.5pp |
| 11 | 27 | 0.65% | 32 | 0.87% | +0.2pp |
| 12 | 14 | 0.34% | 20 | 0.54% | +0.2pp |
| 13 | 2 | 0.05% | 6 | 0.16% | +0.1pp |
| 14 | 2 | 0.05% | 4 | 0.11% | +0.1pp |

| Statistic | Naive | Proper |
|-----------|-------|--------|
| Mean word length | 3.85 | 4.34 |

The biggest change is the collapse of single-rune "words" from 9.69% to 3.49%. These
were artifacts of line breaks splitting words and leaving isolated rune fragments.

### Solved vs Unsolved vs English

Solved sections (7 sections, 249 words): `SOME WISDOM`, `CNOW THIS`, `THE LOSS OF
DIUINITY`, `AN INSTRUCTIAN`, etc.

Unsolved sections (22 sections, 3,418 words): all remaining.

| Length | Solved | % | Unsolved | % | English ~ |
|--------|--------|-------|----------|-------|-----------|
| 1 | 0 | 0.00% | 128 | 3.74% | 3.5% |
| 2 | 65 | 26.10% | 580 | 16.97% | 9.0% |
| 3 | 47 | 18.88% | 854 | 24.99% | 17.0% |
| 4 | 43 | 17.27% | 601 | 17.58% | 18.0% |
| 5 | 21 | 8.43% | 352 | 10.30% | 15.0% |
| 6 | 26 | 10.44% | 291 | 8.51% | 11.0% |
| 7 | 20 | 8.03% | 241 | 7.05% | 9.0% |
| 8 | 15 | 6.02% | 169 | 4.94% | 6.0% |
| 9 | 4 | 1.61% | 88 | 2.57% | 4.0% |
| 10+ | 8 | 3.21% | 114 | 3.34% | 7.0% |

| Statistic | Solved | Unsolved | English |
|-----------|--------|----------|---------|
| Mean length | 4.37 | 4.34 | ~4.7 |

**Key observations:**

1. **Solved sections are heavy on 2-rune words** (26.1% vs 9% in English). This is
   because Runeglish encodes digraphs (TH, EA, OE, NG, etc.) as single runes, so
   common short English words like "the" (2 runes: TH-E) and "of" (2 runes) become
   very short.

2. **Unsolved sections also have short words** (mean 4.34), tracking the solved
   sections closely. This is consistent with the unsolved text also being Runeglish
   — the word boundary structure (`-` and `.`) is preserved through encryption if the
   cipher operates within words.

3. **Single-rune words** appear only in unsolved sections (128 instances, 3.74%).
   The solved sections have zero single-rune words. In Runeglish, the only common
   single-rune words would be `I` and `A` (~3.5% in English). The 3.74% in unsolved
   sections is consistent with this expectation, but these could also be artifacts of
   section/paragraph boundaries or encryption padding.

## Doublet Position Analysis

### Effect of Proper Parsing

| Position | Naive | % | Proper | % | Change |
|----------|-------|-------|--------|-------|--------|
| Initial | 21 | 19.3% | 18 | 15.5% | -3 |
| Final | 35 | 32.1% | 35 | 30.2% | 0 |
| Middle | 53 | 48.6% | 63 | 54.3% | +10 |
| **Total** | **109** | | **116** | | **+7** |

Proper parsing reveals 7 doublets that were hidden at line-break boundaries:

| Fragment 1 | Fragment 2 | Joined | Doublet |
|-----------|-----------|--------|---------|
| ...NGMIA | IAMMW... | NGMIAIAMMW | IA-IA |
| ...YWJ | JPH... | YWJJPH | J-J |
| ...NGIA | IANGSWSPH... | NGIAIANGSWSPH | IA-IA |
| ...THRE | E... | THREE | E-E |
| ...FR | RIXUTHH... | FRRIXUTHH | R-R |
| ...HIAREA | EAXS... | EAHIAREAEAXS | EA-EA |
| ...THRE | EYSN... | THREEYSN | E-E |

Three word-initial doublets in the naive parse were actually mid-word doublets that
appeared initial only because the real word start was on the previous line.

### Solved vs Unsolved Doublet Positions

| Metric | Solved | Unsolved |
|--------|--------|----------|
| Total doublets | 20 | 96 |
| Total runes | 1,089 | 14,828 |
| Doublet rate | 2.38% | 0.84% |
| Suppression vs random (3.45%) | 1.5x | 4.1x |
| Word-initial | 0 (0%) | 18 (18.8%) |
| Word-final | 11 (55%) | 24 (25.0%) |
| Word-middle | 9 (45%) | 54 (56.2%) |

**Critical finding: zero word-initial doublets in solved sections.** This is expected
for English plaintext — virtually no English words begin with double letters.

The unsolved sections have 18 word-initial doublets (18.8% of all doublets), which is
strong evidence that these sections are encrypted. In a cipher that operates on
individual runes within words, the position of doublets within words becomes
essentially random.

### Word-Initial Doublets in Unsolved Sections

All 18 word-initial doublets from unsolved sections:

| Word (Gematria) | Starting Doublet |
|-----------------|-----------------|
| FF | F-F |
| EOEOAEC | EO-EO |
| RREOJM | R-R |
| CCEA | C-C |
| AAEAD | A-A |
| WWU | W-W |
| AEAEIEFNGTHH | AE-AE |
| SSEA | S-S |
| RRNGM | R-R |
| FFGF | F-F |
| THTH | TH-TH |
| OEOECTJ | OE-OE |
| WWYLEO | W-W |
| NNYIA | N-N |
| XXMNAES | X-X |
| EEW | E-E |
| WWOEOBO | W-W |
| WWP | W-W |

W is notably over-represented (4 of 18), but the sample is too small to draw
distributional conclusions.

### Word-Final Doublets in Solved Sections

The 11 word-final doublets from solved sections are all legitimate English patterns:

| Word | Final Doublet | English Pattern |
|------|--------------|-----------------|
| ALL | L-L | Common (-LL) |
| ALL | L-L | Common (-LL) |
| ALL | L-L | Common (-LL) |
| WILL | L-L | Common (-LL) |
| WILL | L-L | Common (-LL) |
| LOSS | S-S | Common (-SS) |
| LOSS | S-S | Common (-SS) |
| AMASS | S-S | Common (-SS) |
| TOO | O-O | Common (-OO) |
| THREE | E-E | Common (-EE) |
| FF | F-F | Common (-FF, e.g. "off") |

These match the expected English word-final double-letter patterns: LL, SS, EE, OO, FF.

## Summary of Findings

1. **Proper parsing matters.** Joining across line breaks changes mean word length
   from 3.85 to 4.34 and eliminates ~270 spurious single-rune fragments.

2. **Word length distribution is consistent between solved and unsolved sections**
   (mean 4.37 vs 4.34), suggesting the cipher preserves word boundaries and the
   underlying Runeglish encoding.

3. **Word-initial doublets are a cipher signature.** Solved sections have zero;
   unsolved sections have 18. English does not produce word-initial doublets, so
   their presence confirms encryption.

4. **Word-final doublets in solved sections are normal English** (ALL, WILL, LOSS,
   AMASS, TOO, THREE). This validates that the Gematria Primus encoding preserves
   natural doublet patterns.

5. **Unsolved doublet rate (0.84%) is heavily suppressed** compared to both random
   expectation (3.45%) and the solved sections (2.38%). This is consistent with the
   autokey cipher hypothesis described in `lp_doublet_hypotheses.md`.

6. **The cipher operates within word boundaries.** Word delimiters (`-` and `.`) are
   in plaintext, not encrypted. This rules out full-text stream ciphers and points
   toward word-level or rune-level encryption with preserved structure.
