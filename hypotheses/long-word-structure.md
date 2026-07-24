---
type: observation
---
# Characterization: Long Words Carry No Structure Beyond the d5 Echo

## Claim

The 1,124 words of length ≥ 5 (38% of the corpus, 7,693 runes) — the only
words that exercise `g³`, `g⁴` and the `g⁵ = id` echo internally — contain
exactly one departure from a doublet-aware null: the distance-5
coincidence echo. Their doublet suppression matches short words, their
internal repeat excess is entirely the echo, their cross-word collisions
are at chance, and their rune distributions are uniform at every
position.

## Status

**Status**: confirmed (characterization)

## What was measured

Clean corpus long words; null throughout is
`aldegonde.stats.nulls.doublet_shuffle` at the observed rate,
re-segmented into the real word-length structure, 400 surrogates
(`experiments/long_word_battery.py`).

**Doublet suppression is length-independent** — a model check that had
never been run per length class:

| word length | doublets / adjacencies | rate |
|---|---|---|
| 1-4 | 23 / 3459 | 0.0066 ± 0.0014 |
| 5-7 | 21 / 3816 | 0.0055 ± 0.0012 |
| 8+ | 19 / 2753 | 0.0069 ± 0.0016 |

**Distance profile (long words only)** reproduces the corpus profile with
no new features: d5 z = +3.7, d4 z = +2.0, d6 z = −1.9, and d1, d2, d3,
d7, d8, d9, d10 all within |z| ≤ 1.2.

**Internal repeats are the echo and nothing else.** Repeated bigrams
inside a single word: 25 observed vs 15.1 ± 4.1 (z = +2.4) — but
decomposed by separation, the excess is entirely at separation 5
(9 observed vs 1.44 ± 1.12, **z = +6.8**); excluding separation 5 the
count is 16 vs 13.6 ± 3.9 (z = +0.6). Repeated runes within a word
(669 vs 632 ± 22, z = +1.7) follow the same source. So the in-word
repeat structure is the `XY···XY` face of the lag-5 echo
(`within-word-d5-coincidence.md`), not an additional phenomenon.

**Cross-word collisions among long words are at chance** — the
starvation result of `collision-hunt-single-constraint.md`, extended to
the population where a base collision would be most visible: shared
2-rune prefixes 797 vs 769 ± 26, suffixes 793 vs 767 ± 29, 3-rune
prefixes 36 vs 27 ± 5 (z = +1.8, the largest lean), 3-rune suffixes 23
vs 27 ± 5, 4-rune prefixes 2 vs 1 ± 1, 4-rune suffixes 0 vs 1 ± 1,
shared 4-rune substrings 17 vs 14 ± 4.

Two long words share a 5-rune substring where ~0.4 are expected
(p = 0.058, the only cell worth naming):

- `ᛒᛗᚱᚾᛗ` — word 1232 at position 1 (`ᚹᛒᛗᚱᚾᛗᚻᛗᛁᚾᚪᛞ`) and word 2713 at
  position 3 (`ᛗᛁᛄᛒᛗᚱᚾᛗ`); phase offset 2.
- `ᚩᚢᚾᚹᛗ` — word 1570 at position 6 (`ᛠᛈᛄᛞᚾᛟᚩᚢᚾᚹᛗ`) and word 1814 at
  position 0 (`ᚩᚢᚾᚹᛗᛚ`); phase offset 1.

Neither sits at phase offset 0, so neither is the shape a plain base
recurrence would produce; at 2 events against 0.4 expected they are
most likely chance, and they are recorded because they would be the
only candidates for additional base constraints if a future model
predicted non-zero-offset collisions.

**Positional rune distributions are uniform** at first, second, third,
last and second-to-last position (chi2 19.5-34.2 on 28 df, all p > 0.05).

## The phase-class test (and its limit)

The walk's sharpest within-word statement is that positions sharing
`j mod 5` share an alphabet, so ALL same-phase pairs should leak while
different-phase pairs sit at chance. Measured: same-phase 0.0481 vs
0.0343 ± 0.0040 (z = +3.5), different-phase 0.0355 vs 0.0347 ± 0.0014
(z = +0.6), gap z = +3.1.

**This is not independent evidence.** Within these words the same-phase
class is overwhelmingly distance 5 (distance 10 needs length ≥ 11, only
53 words, and it runs low), so the test restates the d5 echo rather
than adding to it. The different-phase half is the informative part —
it is flat — but note it averages the d4 elevation and the d6
suppression together, which cancel; the two cells are only visible
separately (see `mixed-cycle-progression.md`).

## Consequences

- Long words behave exactly like short words plus the echo their length
  makes visible. No length-dependent keying, no positional structure, no
  accumulation of state within a word beyond the period-5 relation.
- Multiple-testing note: ~30 statistics were computed here; at |z| ≈ 2
  one or two leans are expected, and the 3-rune-prefix (+1.8) and
  5-rune-substring (p = 0.058) cells are consistent with that. Only the
  d5 echo survives correction.

## Scripts

- `experiments/long_word_battery.py` — the full battery.

## Related

- `within-word-d5-coincidence.md`, `lag5-digraph-structure.md` — the echo
  that accounts for every excess found here.
- `word-position-pairs.md` — the position-pair grid over all words.
- `collision-hunt-single-constraint.md` — the constraint starvation this
  extends to long words.
- `doublet-suppression.md` — the suppression this shows is
  length-independent.

## Verdict

Confirmed characterization. The long-word population carries the d5 echo
and nothing else: suppression is length-flat, internal repeats decompose
entirely into separation-5 events, cross-word collisions sit at chance
including a 5-rune substring census, and positional distributions are
uniform. The corpus's structure does not deepen with word length.
