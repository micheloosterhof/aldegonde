---
type: hypothesis
---
# Hypothesis: The '.' Mark is the 30th Character of a 30/29 Cipher Disk

## Claim

The visible `.` marks in the unsolved sections are not punctuation but the
**30th character of the cipher's alphabet**: the cipher operates on a
size-mismatched disk (a 30-cell ring against the 29-rune ring), and the
marks are output of (or gap events at) the extra cell. Proposed by Michel,
July 2026.

## Status

**Status**: unresolved

## Mechanism

A 30-cell ring rotating against a 29-cell ring never aligns the same way
twice within lcm(30, 29) = 870 steps, and at any rotation exactly one cell
of the larger ring faces no partner. Candidate readings:

- `.` is a 30th CIPHERTEXT symbol: the output alphabet is 29 runes + `.`,
  and a mark is emitted when the cipher maps the current plaintext letter
  to the extra cell.
- `.` is emitted at GAP events: when the current plaintext letter faces
  the unpartnered cell, no rune exists and the scribe writes `.`.

Either way the marks are machinery, not language — which makes their
established non-linguistic behavior automatic instead of anomalous.

## Evidence for

Measured on the clean corpus (`experiments/mark_thirty_symbol.py`):

- **Marks carry no English sentence semantics in either reading
  direction** (`word-length-keystream-and-boundaries.md` section C and the
  direction test): words before AND after marks look like random words.
  Automatic under this hypothesis; needs explaining under any punctuation
  reading.
- **The mark process is homogeneous across sections**: all ten clean
  sections have marks at rates consistent with one Poisson process
  (chi2 ~ 6 on 8 df, p ~ 0.6; rates 0.65%-1.64%). This CORRECTS the
  "four-fold density variation, two sections with no marks" claim in
  `word-length-keystream-and-boundaries.md`, which does not hold at the
  `$`-section level. A content-independent process fits cipher machinery
  better than authorial punctuation habits.
- **Zero `..` adjacencies** vs ~1.9 expected for independent placement
  (p ~ 0.15): consistent with the corpus's doublet suppression extending
  to the 30th symbol.
- **Uniform rune context**: the runes immediately before marks (chi2 25.0,
  df 28) and after marks (chi2 35.5) are uniform; mark gaps are
  near-exponential (cv 0.91). A mixing cipher state, no structure.
- **Prior art**: `stay-slot-hold.md` independently proposed a
  size-mismatched disk (in/out rings that cannot collide) as the
  structural zero-collision advance; this hypothesis gives the extra cell
  a visible identity.

## Evidence against

- **The rate**: 168 marks / 12,956 runes = 1.30% = 1/77. A uniformly
  visited 30th cell fires at 1/30 = 3.33% — observed is 2.6x too rare.
  The cell must be avoided ~60% of the time or reached only under special
  geometry; the simplest version fails on this number.
- **Constant stepping is excluded**: a per-letter-stepping 30/29 disk
  reuses alphabets with period 870, which kappa (flat to lag 3000) rules
  out. The disk would need irregular clocking — compatible with, and
  perhaps requiring, the word-length clocking of `length-clocked-walk.md`.
- The layout coupling (19.9% of marks at line ends, z=+11.3) is neutral:
  typesetting breaks lines at mark glyphs in the solved pages too (26.7%),
  whatever the glyph means.

## 30-symbol battery result (July 2026) — neutral, and structurally so

`experiments/thirty_symbol_battery.py` reran the distance statistics on
the 30-symbol stream (13,124 symbols, `.` occupying positions) against
the stripped stream:

| statistic | 29-symbol | 30-symbol |
|---|---|---|
| doublets | 86 (z=-17.4) | 85 (z=-17.3; the one X.X event separates) |
| kappa lag 5 | 479, z=+1.52 | 466, z=+1.07 |
| lag-5 pair separations d1/d4 (consecutive-match gaps) | 29 / 25 | 28 / 23 |
| kappa lag 6 | z=+0.36 | z=+0.15 |
| kappa lag 11 | z=-2.95 | z=-3.13 |

The lag-5 complex weakens mildly under mark-inclusive accounting — but
the test turns out to have little power either way: the real lag-5 signal
lives WITHIN words, marks sit only at word boundaries, so no within-word
pair ever straddles a mark. Mark accounting only relocates cross-word
matches, whose count is at chance; the mild degradation is consistent
with pure noise reshuffling. The battery neither supports nor
meaningfully damages the hypothesis. (Pair separations here count
consecutive-match gaps, reproducing the published d1=29; the published
d4=28 uses the chase script's event definition — the A/B comparison
applies one definition to both sides.)

Two additional measurements:

- **No doublet-style dead zone in the mark gaps**: min gap 4, gaps <= 12
  number 18 vs ~24 exponential expectation — a mildly thin tail, no more.
  This weakens the zero-`..` consistency point (it is the tail of a
  slightly under-dispersed process, not an avoidance law like the
  doublets' min-gap-6).
- **Marks do not split words**: mean word length before marks (4.23) plus
  after (4.38) is ~two full words, not the halves of one. Any
  cipher-symbol reading must be boundary-synchronized — the mark is
  emitted AT a word boundary (e.g. as a state-dependent variant of the
  `-` separator: 168 of 2,928 boundaries = 5.7%), never mid-word.
- **DJU-BEI arithmetic**: stripped distance 6395 = 5 x 1279; mark-inclusive
  distance 6480 = 2^4 x 3^4 x 5 (= 30 x 216). Both factorizations are
  numerology-grade; recorded without weight.

## Predictions

- Discriminating this hypothesis needs key-conditional tests, not stream
  accounting: under any candidate key, mark positions must decrypt to a
  consistent 30th-cell event (a specific plaintext symbol, or gap
  alignments of the disk schedule).
- Under the gap-event reading, marks either consume a keystream step or
  not (the AN-END interrupt question); trial decryptions must test both
  alignments.
- Any candidate cipher model should reproduce the 1/77 mark rate and the
  zero `..` count from its mechanism, not by fiat.

## Scripts

- `experiments/mark_thirty_symbol.py` — per-section rates, gaps, `..`
  count, rune contexts.
- `experiments/mark_direction_test.py` — the both-directions
  non-linguistic result.
- `experiments/thirty_symbol_battery.py` — the 30-symbol vs 29-symbol
  distance-statistics comparison, mark-gap tail, DJU-BEI arithmetic.

## Related

- `word-length-keystream-and-boundaries.md` — the sentence-mark forensics
  this reinterprets (its per-section variation claim corrected here).
- `stay-slot-hold.md` — the size-mismatched disk precedent.
- `length-clocked-walk.md` — the irregular clocking this disk would need.
- `running-key-math-sequence.md` — solved-page interrupt mechanics (the
  keystream-consumption question).

## Verdict

Unresolved and live. The hypothesis explains the marks' non-linguistic
behavior for free, and the mark process looks like machinery (per-section
homogeneity, uniform contexts, exponential-ish gaps). The 30-symbol
battery came back neutral — structurally low-power, because the lag-5
signal is within-word and marks sit only at boundaries — so the stream
accounting does not decide it. What must be honored by any concrete
version: the 1/77 rate (vs 1/30 naive), boundary synchronization (marks
never split words), no constant stepping (period 870 excluded by kappa),
and no dead-zone law in the mark gaps (min gap 4). The most promising
concrete form is boundary-synchronized: the mark as a state-dependent
variant of the word separator (5.7% of boundaries), clocked like the
length-clocked walk. Resolution requires key-conditional tests.
