# Hypothesis: Runeglish Encoding Alone Explains the Statistics

## Claim

The statistical anomalies (flat distribution, doublet suppression) are entirely
explained by the runeglish encoding of English text (where digraphs like TH,
NG, EA are compressed to single runes), without any cipher being applied.

## Status

**Status**: disproved

## Mechanism

No cipher. The observed statistics are a natural consequence of converting
English to runeglish using the Cicada 3301 rune-to-letter mapping, where
certain letter pairs become single runes.

## Evidence for

- Runeglish encoding does reduce natural English doublet rates somewhat,
  because some common English double-letters (e.g. "oo", "ee") get partially
  absorbed by digraph compression
- The encoding changes the effective alphabet and letter frequencies

## Evidence against

- **Insufficient doublet suppression**: Even accounting for all digraph
  compression (TH to thorn, NG to ing-rune, etc.), the natural English doublet
  rate in runeglish is reduced by at most ~2x. The observed suppression is
  5.09x. Encoding alone cannot bridge this gap.
- **Near-perfect uniformity**: Runeglish encoding of English text does not
  produce a uniform distribution. Some runes (corresponding to common letters)
  would still be much more frequent than others.
- **IOC**: Plain runeglish English text has IOC significantly above 1/29. The
  observed IOC matches 1/29 exactly.

## Scripts

None needed. The quantitative gap (2x vs 5x suppression) is sufficient.

## Verdict

Disproved. Runeglish encoding partially suppresses doublets but not nearly
enough to explain the observations. A cipher mechanism is required.
