# Hypothesis: The Doublet Marker Rune is EA

## Claim

**IF** each ciphertext doublet (`C[i] == C[i+1]`) marks a position where one
fixed plaintext rune occurs, **THEN** that rune is **EA (ᛠ)** — the least-refuted
candidate, with F, NG, and IO excluded. The premise itself is unproven.

## Status

**Status**: unresolved

The load-bearing premise — that doublets mark a single fixed plaintext rune at
all — is **not established**, and is undercut: the mechanism that would naturally
imply it (ciphertext autokey) is disproved (see Evidence against). EA was the
project's starting assumption, not a finding. The "filters" below are
consistency checks (EA is not *refuted*) conditioned on the premise; analysis
that assumes EA cannot establish EA. Treat this whole note as conditional.

## Mechanism

This is not a cipher mechanism — it is a constraint on the plaintext that holds
for any cipher in which doublets mark a single fixed rune. That class includes
ciphertext autokey (where `C[i]=C[i+1]` forces the **2nd** rune to the additive
identity) and its reverse-direction and inner-layer variants. The marker rune
can be the **1st or 2nd** rune of the doublet depending on keystream direction;
the frequency argument below does not distinguish the two, only the rune.

Two filters narrow the candidate *given the premise*. Neither is positive
evidence for the premise; both only test which rune survives if the premise is
granted.

## Consistency checks (conditional on the premise)

**Frequency filter.** The doublet rate is 0.678% (89 / 13,136). If each doublet
marks one fixed plaintext rune, that rune's runeglish frequency must match.
From `src/aldegonde/data/ngrams/runeglish/unigrams.txt`, only three runes fall
in the 0.4-1.0% band:

| rune | name | runeglish freq | predicted doublet rate |
|------|------|----------------|------------------------|
| ᛠ | EA | 0.587% | 0.59% (matches 0.68%) |
| ᛝ | NG | 0.826% | 0.83% |
| ᛡ | IA/IO | 0.961% | 0.96% |

F (ᚠ) = 2.566% predicts a 2.57% doublet rate — **refuted** (3.8x too many). This
kills the naive 0-indexed identity (F=0) and every common rune.

**Word-initial filter.** The marker rune demonstrably appears at the start of a
word: 24 times as the 2nd rune of a doublet (the cross-word doublets), 12 times
as the 1st rune. Either count is fatal to candidates that cannot begin a word:

- **NG** never starts an English/runeglish word. Predicts ~0 word-initial.
  Refuted.
- **IO** appears word-initially only in rare cases (ion, iota); in runeglish it
  is overwhelmingly the medial "-ION" cluster. Predicts ~0 word-initial.
  Refuted.
- **EA** starts each, ear, early, earth, east, eat... and also goes medial
  (great, dream) and final (sea, idea). Survives.

EA is the unique intersection of both filters — but only the closest of a band,
and the frequency match is loose (15% off, against a generic corpus). NG is fine
on frequency alone and is excluded only by the premise-dependent word-initial
argument.

**Positional neutrality is consistent.** The 2nd rune's word-position
distribution (start 24 / middle 46 / end 19) is statistically indistinguishable
from the all-rune baseline (21.9 / 55.5 / 21.9%): chi-square 1.98, 3 df,
p approx 0.58. A positionally-flexible digraph like EA fits; a strongly
positional rune would not.

**Suppression is uniform across word boundaries.** 65 within-word doublets, 24
cross-word (23 across `-`, 1 across `.`, none across segment/page/number-page
gaps). Cross-word count 24 vs 20.1 expected from opportunity — not suppressed.
This points to a continuous running mechanism that ignores word spacing, and
argues against word-boundary-reset autokey (see `word-boundary-reset-autokey.md`).

## Evidence against

- The frequency match is to a generic runeglish corpus, not the LP plaintext;
  observed 0.68% vs EA's 0.59% is a 0.09-point excess (about 12 doublets). Within
  text-to-text variation, but not exact.
- Pure ciphertext autokey — the most natural mechanism that produces a fixed
  identity rune — is itself disproved by the preceding-rune split test
  (`beaufort-autokey-ea.md`, `ciphertext-autokey.md`). So the EA-marker
  constraint must be carried by a different mechanism (e.g. autokey plus an
  inner layer), not plain autokey.

## Predictions

- Whatever the mechanism, decrypting it should place **EA** at all 89 doublet
  positions (1st or 2nd rune, per direction), including 24/12 word-initial EAs —
  i.e. words beginning "ea..." (each, ear, earth, east).
- 1st-vs-2nd (keystream direction) is still open. To decide it, obtain EA's
  initial/medial/final fractions from a runeglish corpus *with* word boundaries
  and test against the 2nd-rune split (24/46/19) vs the 1st-rune split
  (12/53/24); whichever matches EA's profile wins. The ngram files carry no word
  boundaries, so this needs a runeglish-encoded English corpus.

## Scripts

- `experiments/doublet_word_position.py` — word-position analysis plus the
  frequency and word-initial filters. Reproduces every number above.

## Related

- `beaufort-autokey-ea.md` — EA identity under ciphertext autokey (disproved as
  a full mechanism; this note salvages the mechanism-independent EA constraint).
- `ciphertext-autokey.md` — general ciphertext autokey, same disproof.
- `autokey-plus-inner-layer.md` / `autokey-plus-substitution.md` — live
  mechanisms that could carry the EA marker.
- `position-within-word.md`, `word-boundary-reset-autokey.md` — word-structure
  hypotheses tested here.

## Verdict

Unresolved, and weaker than it first looks. EA is the least-refuted candidate
*conditional on* an unproven premise (that doublets mark one fixed plaintext
rune). That premise has no positive support and is undercut by the autokey
disproof. The frequency match is loose and the word-initial argument is itself
premise-dependent, so the filters establish only that EA is *not refuted* — not
that it is correct. Doublet spacing is content-driven Poisson
(`doublet-spacing-poisson.md`), consistent with a single-rune trigger but
equally with a fixed n-gram trigger. EA-as-marker remains an open starting
hypothesis, not a result.
