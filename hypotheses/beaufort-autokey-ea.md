# Hypothesis: Beaufort Ciphertext Autokey with 1-Based Indexing (EA Identity)

## Claim

The unsolved sections use a Beaufort ciphertext autokey cipher with Cicada's
1-based rune indexing, making EA (index 28) the identity element that produces
doublets.

## Status

**Status**: disproved

## Mechanism

Cicada 3301 uses 1-indexed rune numbering in their Gematria Primus. Under
1-indexed arithmetic, the autokey formula becomes:

C[i] = C[i-1] - P[i] + 28 mod 29  (Beaufort variant)

This is equivalent to standard Beaufort autokey with a constant key offset of
28. The identity element shifts from index 0 (F) to index 28 (EA): a doublet
C[i] = C[i+1] implies P[i+1] = EA.

## Evidence for

- **All 89 doublets map to EA**: Under this model, every doublet in the
  ciphertext corresponds to EA in the plaintext. Algebraically certain.
- **EA frequency is plausible at 0.68%**: EA appears in runeglish words like
  "each", "ear", "eat". A frequency of 0.68% is plausible for this rare
  digraph-rune.
- **Historical precedent**: Cicada used Beaufort autokey in solved LP sections.
- **Self-reference**: Key = 28 = EA's index. Cicada favors self-referential
  constructions.

## Evidence against

- **Preceding-rune split disproof**: This is a specific instance of ciphertext
  autokey. Splitting the ciphertext by C[i-1] should produce 29 streams with
  English-like IOC (permuted English letter frequencies). Measured: mean IOC
  0.0354, indistinguishable from random (1/29 = 0.0345). This rules out ALL
  ciphertext autokey variants, including this one.
- **Single-letter word contradiction**: 6-13 distinct values per preceding-rune
  group, far exceeding the 2-3 expected for "a"/"I" under continuous autokey.

## Predictions

Same as general ciphertext autokey: the preceding-rune split should produce
English-like IOC. It does not.

## Scripts

- `hypotheses/disprove_autokey_split.py` — Definitive disproof.

## Related

- `ciphertext-autokey.md` — General ciphertext autokey. Disproved by the same
  evidence.

## Verdict

Disproved. This is a special case of ciphertext autokey, which is ruled out by
the preceding-rune split test. The algebraic elegance of the EA identity and
1-based indexing was suggestive, but the data is conclusive.
