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

## Predictions

- The full statistical battery has never been run on the **30-symbol
  stream** (runes + `.` occupying positions). If marks are real symbols:
  doublet count becomes 85 (the one X.X event straddling a mark is
  distance 2, not a doublet), and every distance statistic shifts by one
  across each mark. Small corrections (168 marks), but the lag-5 and
  kappa scans should be repeated on the 30-symbol stream; any improvement
  in the anomalies' sharpness favors this reading.
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

## Related

- `word-length-keystream-and-boundaries.md` — the sentence-mark forensics
  this reinterprets (its per-section variation claim corrected here).
- `stay-slot-hold.md` — the size-mismatched disk precedent.
- `length-clocked-walk.md` — the irregular clocking this disk would need.
- `running-key-math-sequence.md` — solved-page interrupt mechanics (the
  keystream-consumption question).

## Verdict

Unresolved and live. The hypothesis explains the marks' non-linguistic
behavior for free, and the newly measured facts (per-section homogeneity,
zero `..`, uniform contexts) all lean its way. Its quantitative obstacles
are the 1/77 rate (vs 1/30 naive) and the excluded constant stepping —
both survivable if the extra cell is avoidance-suppressed and the disk is
word-clocked, which converges suggestively with the length-clocked walk.
Next step: rerun the distance-statistics battery on the 30-symbol stream.
