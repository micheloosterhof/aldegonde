# Hypothesis: Beaufort Ciphertext Autokey with 1-Based Indexing (EA Identity)

## Claim

The unsolved sections use a Beaufort ciphertext autokey cipher with Cicada's
1-based rune indexing, making EA (index 28) the identity element that produces
doublets.

## Status

**Status**: plausible

## Mechanism

Cicada 3301 uses 1-indexed rune numbering throughout their materials (Gematria
Primus assigns values 1-29 rather than 0-28). Under 1-indexed arithmetic, the
autokey formula becomes:

C[i] = C[i-1] - P[i] + 28 mod 29  (Beaufort variant)

This is equivalent to standard Beaufort autokey with a constant key offset of
28. The identity element shifts from index 0 (F) to index 28 (EA): a doublet
C[i] = C[i+1] implies P[i+1] = EA.

The self-referential property that key = 28 = EA's own 0-based index is
thematically consistent with Cicada's style.

## Evidence for

- **All 89 doublets map to EA**: Under this model, every doublet in the
  ciphertext corresponds to EA in the plaintext. This is algebraically certain.
- **EA frequency is plausible at 0.68%**: EA appears in runeglish words like
  "each", "ear", "eat", "earth", "east", typically as a word-initial rune. A
  frequency of 0.68% is plausible for this rare digraph-rune.
- **1-indexing precedent**: Cicada uses 1-indexed rune numbering throughout
  their published materials.
- **Self-reference**: Key = 28 = EA's index. Cicada favors self-referential
  constructions.
- **Historical precedent**: Cicada used Beaufort autokey in solved LP sections.

## Evidence against

- **Simple decryption fails**: Decrypting with Beaufort autokey key=28 does not
  produce readable English. An additional transformation or unknown primer is
  needed.
- **0.68% is on the low side**: Even for a rare digraph-rune, 0.68% might be
  lower than expected depending on the plaintext's vocabulary.
- **1-indexing assumption is unverified for the cipher**: While Cicada uses
  1-indexing for labeling, it is not proven they use it in cipher arithmetic.

## Scripts

- `experiments/lp_ea_hypothesis.py` — Tests this specific model: decrypts with
  Beaufort autokey key=28 and checks plaintext statistics.

## Verdict

Plausible. The algebraic fit is clean and the construction is thematically
Cicada-like. The main weakness is that simple decryption does not produce
readable text, implying either an additional cipher layer or the hypothesis is
wrong. This is a refinement of the general ciphertext autokey hypothesis (see
`ciphertext-autokey.md`) with a specific claim about the indexing scheme.
