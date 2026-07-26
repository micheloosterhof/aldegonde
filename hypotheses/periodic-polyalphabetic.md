---
type: hypothesis
---
# Hypothesis: Periodic Polyalphabetic Cipher (Vigenere with Fixed Key)

## Claim

The unsolved sections use a Vigenere cipher (or similar periodic polyalphabetic
cipher) with a fixed repeating key.

## Status

**Status**: disproved

## Mechanism

C[i] = P[i] + K[i mod L] mod 29, where K is a key of length L. Variants
include Beaufort (C[i] = K[i mod L] - P[i] mod 29) and other tabula recta
constructions. All share the property of a fixed repeating key period.

## Evidence for

- Cicada 3301 used Vigenere and Beaufort ciphers in the solved sections of
  Liber Primus
- Polyalphabetic ciphers can flatten letter frequencies (though not perfectly
  for short keys)

## Evidence against

- **No Friedman period**: The Friedman test detects no period. Any periodic key
  would produce a detectable IOC spike at the key length. With ~13,000 runes of
  ciphertext, even long keys (up to several hundred) would be detectable.
- **IOC exactly random**: The IOC is 0.0345, exactly matching 1/29. A periodic
  polyalphabetic cipher on English text produces IOC above random at multiples
  of the key length.

## Scripts

- `src/aldegonde/analysis/friedman.py` — Friedman test implementation. Run on
  `data/page0-58.txt` to confirm no period is detected.

## Related

- `length-clocked-walk.md`, `mixed-alphabet-vigenere.md` — periodic
  polyalphabetic components *inside* a per-word re-keyed walk are a
  different matter: the per-word base destroys the global period, so
  Friedman cannot see them. The plain-shift member is excluded by the
  doublet floor (a 5-letter Vigenere step floors at 0.0119 against
  0.0063 observed); the mixed-alphabet (Quagmire) member is NOT
  excluded — the full-dictionary exhaustion leaves 12,064 keyword `g`
  candidates and it is the live enumerable formulation
  (`mixed-alphabet-vigenere.md`).

## Verdict

Disproved by the Friedman test. The absence of any periodic IOC signal rules
out all fixed-period polyalphabetic ciphers regardless of key length —
as *global* structure (scanned: periodic IoC to period 600, keystream
reuse to lag 6,400; `no-periodicity.md` and the gap audit). Period-5
components hidden under a per-word re-key are invisible to Friedman; of
those, the plain-shift version is excluded on the doublet rate while
the mixed-alphabet (Quagmire) version remains live — see Related.
