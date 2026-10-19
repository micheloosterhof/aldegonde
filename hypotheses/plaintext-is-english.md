---
type: hypothesis
---
# Hypothesis: The Body's Plaintext Is Another Language Than English

## Claim

Every plaintext reference in this directory is English. Two key-free body facts sit
awkwardly with English: the length marginal has a hole at 2
(`block-lengths-have-a-hole-at-two.md`), and the block lengths carry little serial
order. Both depend on the language. If another language had both natively, the
joining rule of `short-units-are-written-joined.md` would be unnecessary.

## Status

**Status**: disproved for the ten languages tested (October 2026). No tested language
fits the length marginal and the serial order together. English with 2-rune units
joined at q ≈ 0.40 fits both.

## Evidence against

`experiments/plaintext_language.py --run` spells Gutenberg prose in runes with the
book's rules (umlauts as AE/OE/UE, other accents dropped) and measures windows of the
body's 2,928 words. Per-language summary:

| plaintext | 2-rune share | r1 (uncentred) | marginal χ² vs body (11 df) | d5w |
|---|---|---|---|---|
| **body** | **0.159** | **−0.009** | — | **0.0492** |
| English prose | 0.290 | −0.180 | 166 | 0.061 |
| Dutch | 0.161–0.173 | −0.06 to −0.09 | 34–60 | 0.071–0.084 |
| Danish | 0.144–0.166 | −0.06 to −0.08 | 75–78 | 0.060–0.075 |
| Latin | 0.120–0.153 | −0.03 to +0.02 | 168–688 | 0.059–0.070 |
| German | 0.084–0.103 | −0.03 | 212–307 | 0.072–0.078 |
| Swedish | 0.084–0.089 | −0.03 to −0.08 | 148–162 | 0.053–0.056 |
| Finnish | 0.103–0.113 | −0.01 to +0.03 | 641–651 | 0.087–0.091 |
| French, Italian, Spanish, Esperanto | 0.17–0.29 | −0.10 to −0.23 | 191–364 | 0.065–0.078 |

The table splits into two groups. Languages with articles and short function words
(English, the Romance languages, Esperanto) have strongly negative serial order and
too many short words. Languages with near-zero serial order (Latin, German, Finnish,
Swedish) have too few 2-rune words and too many long ones. Dutch and Danish come
nearest on the marginal and still reject it at χ² 34–78 on 11 df, with serial order
1.7–3.4 window-sd below the body.

**d5w does not discriminate.** Under the walk the body reads A × (plaintext d5w) +
(1 − A)/29, so any plaintext with d5w at or above the body's 0.0492 fits by choosing
the clock perturbation. Every language tested qualifies.

**English with joining fits both.** `experiments/plaintext_language.py --serial`
compares the lag-1 length correlation against the author's own sixteen solved pages.
Lengths are centred within 45-word chunks in every corpus, so the −1/n bias of
centring is equal on both sides:

| corpus | centred r1 |
|---|---|
| body | −0.0245 ± 0.0199 |
| author, 16 solved pages | −0.1280 ± 0.0389 (jackknife) |
| author, 2-rune units joined at q = 0.40 | −0.0373 ± 0.0493 |
| English prose | −0.2035 ± 0.0212 |
| English prose, joined | −0.1296 ± 0.0201 |

The body sits 2.37σ from the author's pages and 0.24σ from the author's pages with
short units joined. This agrees with the G² result in
`short-units-are-written-joined.md` (serial order at 1.2σ), using a different statistic.
Gutenberg prose is not the right reference here: its serial order is 1.6 times the
author's.

## Caveats

- The transliteration uses English spelling rules. A writer spelling German in runes
  might write SCH or CH differently, which moves word lengths by a rune.
- Two to five books per language, prose only. Register spread inside a language is
  priced only by those books.
- Old English could not be tested: Project Gutenberg lists no Old English prose.

## Scripts

- `experiments/plaintext_language.py` — `--run` for the language table, `--serial` for
  the serial-order comparison.

## Related

- `block-lengths-have-a-hole-at-two.md`, `short-units-are-written-joined.md` — the
  joining rule this supports.
- `separators-are-not-word-boundaries.md` — the serial-order observation.
- `d5-bounds-the-clock-perturbation.md` — why d5w cannot pick a language.

## Verdict

Disproved for the ten languages tested. The body's block lengths are what the author's
own English gives when about 40% of 2-rune words are joined to the next word. No other
language does better without a joining rule.
