---
type: hypothesis
---
# Hypothesis: The Apostrophes Mark English Contractions (Four Plaintext Cribs)

## Claim

The Liber Primus page images carry a **raised tick glyph** that the working
transcriptions omitted entirely. It appears in two roles:

- **four times alone**, inside a word near its end — an apostrophe
- **fourteen times in adjacent pairs** — double quotation marks

The four lone ticks mark English contractions. Each constrains the plaintext at
that site to a small candidate set, giving roughly **28 bits** of known-plaintext
constraint spread over 14 rune positions in sections 7, 10, 13 and 14.

## Status

**Status**: plausible

The mark census is measured and reproducible. The reading of the lone ticks as
contraction apostrophes is well supported but rests on n = 4; the decorative
alternative is weakened (p = 0.028), not excluded.

## Mechanism

Runeglish collapses digraphs to single runes, so contraction tails have fixed
rune lengths. Section 11 (plaintext Parable) fixes the rules directly:
`ᛞᛁᚢᛁᚾᛁᛏᚣ` = DIUINITY (V→U), `ᛚᛁᚳᛖ` = LIKE (K→C), `ᚦᛖ` = THE (TH→ᚦ).

Therefore:

| tail | runes | contractions |
|---|---|---|
| `'S` `'D` `'T` | 1 | IT'S, HE'D, DON'T, GOD'S, … |
| `'RE` `'VE` `'LL` | 2 | WE'RE, YOU'VE, THEY'LL, … |

**All four observed marks leave exactly one rune after them, and the word ends
there.** That excludes the entire two-rune tail family. The plaintext tail at
each site is `S`, `D` or `T`.

The stem length then splits the four sites:

| page | word | shape | position | stream offset | admissible readings |
|---|---|---|---|---|---|
| 4 | `ᛗᛉᛁ'ᚹ` | 3 + 1 | before a `.` mark | 1107 | n't, or any 3-rune stem + `'S`/`'D` |
| 21 | `ᚫᚩ'ᚣ` | 2 + 1 | mid-run | 5136 | IT'S, HE'S, WE'D, HE'D, IT'D |
| 35 | `ᛈᛖ'ᛏ` | 2 + 1 | after a `.` mark | 8513 | IT'S, HE'S, WE'D, HE'D, IT'D |
| 41 | `ᛉᛚᛄ'ᚳ` | 3 + 1 | mid-run | 10086 | n't, or any 3-rune stem + `'S`/`'D` |

**Pages 21 and 35 cannot be n't contractions.** `n't` needs a three-rune stem at
minimum (DON, CAN, WON, ISN, AIN); these have two-rune stems. Their tail is
`'S` or `'D`.

## Evidence for

- **Glyph census** (`experiments/apostrophe_census.py`): a connected-component
  sweep of all 58 page images finds the tick as a clean geometric class,
  `h = 40, w = 12` inside the text block, against a rune height of 114 and dot
  marks of 9-10 px. Singletons occur on exactly pages 4, 21, 35 and 41 — no
  apostrophe was missed. Adjacent pairs at 20 px spacing occur 14 times across
  pages 6, 7, 22, 40, 42, 43 and 53.
- **The mark is not a separator.** The word separator is a single mid-height
  dot and the sentence mark a four-dot diamond. The tick is a raised stroke,
  distinct in both height and vertical placement.
- **Position is linguistically valid** (`experiments/contraction_shape_test.py`).
  Under a null placing each mark at a uniform internal slot of its host word,
  all four landing with a one-rune tail has p = 0.028 (exactly 1 in 36). A
  decorative mark has no reason to prefer that slot.
- **The paired ticks imply direct speech.** Fourteen quotation glyphs — an even
  count, consistent with seven quoted spans — mean the plaintext contains
  dialogue. Dialogue is the register in which contractions occur, so the two
  mark classes corroborate each other. The solved pages include koans with
  reported speech.
- An apostrophe-plus-double-quote system is English typographic convention. The
  mark set was designed for an English plaintext.

## Evidence against

- **n = 4.** Four marks in 2,928 words (0.14%) is a low contraction rate even
  for formal prose. The shape result is a single nominal p = 0.028 on four data
  points; it does not survive any serious multiple-test discount.
- **The `.`-mark result blocks the strongest refinement.** Page 4's word sits
  immediately before a `.` and page 35's immediately after one. If `.` marked
  English sentence ends, page 4 would be forced towards `n't` (a possessive
  needs a following noun; `'D` and `'S`-as-*is/has* need a complement) and page
  35 towards IT'S / HE'S. But `word-length-keystream-and-boundaries.md`
  establishes that the `.` marks do **not** mark English sentence ends
  (sentence-final word lengths z = -1.21 against solved-page z = +7.06,
  contrast z = +5.86, direction-independent). **That refinement is therefore
  withheld.** It must not be reinstated by assuming the sentence reading, and
  the contraction data must not be used to argue the `.` marks are sentence
  ends — with two mark-adjacent sites out of four (p ≈ 0.06 against
  mark-adjacency at chance) the sample is far too small to bear on that
  question either way.
- Decoration is not excluded. A forger imitating English typography would place
  apostrophes plausibly; the shape test measures only that placement is not
  uniform-random.

## Predictions

1. Any candidate decryption must render all four host words as valid English
   contractions with the tick in exactly the recorded slot. Measured against
   `/usr/share/dict/words` this is a filter of 1 in 62 per 2+1 site and 1 in
   219 per 3+1 site — **≈ 28 bits combined**, against 24.3 bits for a 5-rune
   key.
2. The cribs do not chain. The four sites lie 1107 / 5136 / 8513 / 10086 runes
   apart in four different sections, and `no-periodicity.md` excludes a periodic
   key, so they constrain the keystream only locally. They are a filter on
   candidate plaintexts, not a key-recovery lever.
3. If page 4 is `n't`, then rune `ᛁ` at offset 1109 enciphers N and `ᚹ` at 1110
   enciphers T, and the additive key there ends `[…, …, 1, 20]` (Beaufort
   `[…, …, 19, 23]`) — the last two positions are fixed across all five n't
   candidates because the plaintext ends N,T regardless of stem.
4. The 14 quotation marks, once located to rune positions, should bracket
   contiguous spans. Spans that do not nest or pair would argue the marks are
   decorative after all.

## Scripts

- `experiments/apostrophe_census.py` — connected-component sweep of all 58 page
  images; classifies tick / dot / rune / artwork and locates every mark.
- `experiments/contraction_shape_test.py` — decoration-vs-language null test.
- `tests/aldegonde/test_transcription.py` — guards the data files: the four
  apostrophes are present, and the rune stream, word count and doublet count are
  unchanged (12,956 / 2,928 / 86), so the new character can never enter the
  cipher stream or split a word.

## Related

- `no-known-plaintext-foothold.md` — its claim that no known-plaintext pair
  exists inside `page0-58.txt` now needs qualifying: these are partial cribs.
  They are weaker than a plaintext↔ciphertext pair (the plaintext is a small
  candidate set, not a known string) but they are not nothing.
- `word-length-keystream-and-boundaries.md` — the `.`-mark result that blocks
  the sentence-position refinement above.
- `no-periodicity.md` — why the cribs cannot be chained.

## Verdict

The mark census is solid: the transcriptions were missing a whole punctuation
class, and it is now recorded. The contraction reading is the natural one and
carries real filtering power, but four marks is a thin base and the sharpest
inference available — sentence position — is closed off by the `.`-mark result.
Treat the tails as constrained to `{S, D, T}` and the two-rune-stem sites as
non-`n't`; treat everything finer as untested.

Open: locating the 14 quotation marks to rune positions. That is a larger and
more informative structure than the apostrophes — seven bracketed spans of
plaintext — and it is still entirely absent from the transcription.
