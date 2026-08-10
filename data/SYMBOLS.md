# Transcription symbol table

What each non-rune character in `data/*.txt` means, and which of them come from
the page and which the project added.

The distinction matters. Characters that come from the page can be wrong about
the page; characters the project added are conventions and can only be wrong
about themselves. Until August 2026 the two were mixed, and the mark inventory
turned out to be short by three glyph classes
(`hypotheses/mark-glyph-inventory.md`).

## Runes

29 Anglo-Saxon futhorc runes, `ᚠ`-`ᛠ`, per `src/aldegonde/c3301.py`. Rune
values are settled and verified; do not re-adjudicate them through a mark
review.

## Marks that are on the page

Dot clusters, encoded by **dot count** as a circled numeral so the count is the
identity rather than an interpretation:

| char | codepoint | dots | role |
|---|---|---|---|
| `①` | U+2460 | 1 | word separator |
| `③` | U+2462 | 3 | — |
| `④` | U+2463 | 4 | sentence mark |
| `⑩` | U+2469 | 10 | — |
| `⑬` | U+246C | 13 | — |
| `⑈` | U+2448 | ? | unrecognised count, needs review |

**Legacy encoding, being replaced.** The current files use `-` for one dot and
`.` for everything else. That collapses `③` into the word separator and
`④ ⑩ ⑬` into one character, so any statistic counting `.` marks is measured on
a mixture. `experiments/transcription_review.py` and `apply_review.py` migrate
it line by line.

Counts of 14, 15 and above are **not marks** — they are page ornament and
marginal artwork (see `mark-glyph-inventory.md`) and must not be encoded.

## Marks that are on the page but not yet encoded

| glyph | count | status |
|---|---|---|
| apostrophe | 4 | recorded as `'` (`hypotheses/contraction-cribs.md`) |
| double quote | 14 | recorded as `"` |

Both were absent from the transcription until August 2026.

## Structure the project added

These are not on the page as characters; they record layout and division.

| char | count | meaning | is it a word boundary? |
|---|---|---|---|
| `/` | 645 | end of line | **no** — words wrap across lines |
| newline | 732 | end of line in the file | **no** |
| `%` | 57 | end of page | disputed, see below |
| `&` | 19 | end of paragraph / block | disputed |
| `$` | 11 | end of section | disputed |

**The boundary question is open.** `experiments/lp_corpus.py` treats
`- . % & $` as word boundaries and yields the published 2,928 words; section D
of `word-length-keystream-and-boundaries.md` argues words end only at `-` and
`.`, since 46 of 57 `%` page breaks fall mid-word. The two differ by 32 words.
Anything sensitive to word length should be reported under both.

## Other content

**Verse numbers.** Pages 36-38 open each block with a large **red Arabic
numeral** — 1, 2, 3, 4, 5 — set against whitespace and abutting the runes with
no separator dot. They are on the page, in red like the opening runes, and they
divide the text into numbered verses.

A word therefore cannot run through one. `c3301.NUMERALS` is part of
`WORD_BOUNDARY` for that reason: without it, a line that ends mid-word joins the
text after the next numeral, and the clean corpus reads 2,927 words instead of
2,928.

**Verse 3 opens without a closing mark, and that is on the page.** Four of the
five verses are closed by a cluster mark before the next numeral — verse 1 by
`⑩`, verse 2 by `④` then the page break, verses 4 and 5 by `④`. Verse 3 is
preceded directly by the runes `ᚠᛒ` at the end of page 37 line 3, with no mark
between them and the numeral. Both the page image and an independent read of the
scan agree no mark is there.

**No marker is written there, and none should be.** A circled numeral would
claim a dot count the page does not show, and a `-` would show a separator the
page does not have — besides colliding with the 236 literal `-` that are base-60
separators in these files. The transcription therefore records exactly what is
there: a line wrap, then the numeral. The boundary is carried by the numeral
itself, which `WORD_BOUNDARY` already honours, so nothing is lost by writing
nothing.

So the word before verse 3 is bounded by the numeral alone. Under the rule above
that yields `ᚠᛒ` and `ᛞᚢᛈ`; without it they would be the single 5-rune word
`ᚠᛒᛞᚢᛈ`. The choice moves exactly one word out of 2,928 — the 2-rune class
shifts 465 to 464 — so no statistic can turn on it. It is recorded here because
`ᚠᛒ` should not be read as an ordinary short word: it is the one word in the
corpus whose end is marked by a verse number rather than by a dot.

**A numeral also appears inline inside the ciphertext, and it is dotted.** Page
10 line 7 reads `ᛉᚩ①ᛇᛁᛡᚠᛟᛒᚦᚠ①ᛋᛒ①ᚠᛞᛇ①ᚩᚦᛏ①7①ᚷ①ᛚᛄᛖᚫ` — a black `7`, rune-sized,
set inline with a separator dot on each side. It sits after rune 2,566, in
`$`-section 2, so it is inside the encrypted corpus rather than the solved
sections. It is the ONLY inline numeral there: every other digit before rune
12,956 belongs to a base-60 block (at runes 3,612 and 12,114) or is a verse
number.

This is the precedent for treating a numeral as a word-level token. The `7` is
delimited exactly as a word is, so it splits the text either way — the dots do
the work, and `NUMERALS` is redundant at that site. It also sharpens the verse-3
anomaly above: where the scribe wrote a numeral inline, they dotted BOTH sides
of it, which is why the missing dot before verse 3 stands out.

Note the `7` yields no word of its own in any rune-based count, since a word is
a run of runes. It is a boundary that carries content.

Digits also appear in the final sections — the hex block and the plaintext
Parable in sections 10-11 — where they are content. Treating them as boundaries
costs nothing there, since those runs hold no runes.

## Content the transcription omits entirely

Found during the August 2026 line-by-line review, as bands the reader saw for
which the transcription has no line at all. These are not corrections — the
transcription is not wrong about them, it simply does not carry them.

| pages | content | status |
|---|---|---|
| 33-39 | **cuneiform**, two bands per page | unencoded |
| 2 | a picture | unencoded |

The cuneiform runs across seven consecutive pages. Nothing in the corpus files
records it, so any statistic over "the text of pages 33-39" is over the runic
portion only. Whether it should be transcribed, and in what alphabet, is
undecided.

## Not in the transcription at all

**Red runes.** The page uses colour on some runes; the transcription is
monochrome. The groupings live separately in `lp_section_data.py`
(`lp_sections_by_red_runes`) and are not recoverable from the text files. If
colour turns out to be load-bearing this needs encoding too, and the source
scans carry it.
