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

- **IOC exactly random**: The IOC is 0.0345, exactly matching 1/29. This is the
  load-bearing evidence, and it is now quantified. Two positions share an alphabet
  with probability 1/L, so `IoC = 1 + (I_p − 1)/L`; with the author's own plaintext
  giving `I_p = 1.788`, the body's IoC bounds **L ≥ 949** under a single key, and
  ≥ 60 runes per key even granted a fresh key on every page
  (`flat-ioc.md`, `alphabet_count_bound.py`, `per_page_key_bound.py`). No periodic
  key anywhere near a human-memorable length survives that.
- **No Friedman period**: the Friedman test detects no period — but this bullet used
  to add that "even long keys (up to several hundred) would be detectable", and that
  is **only true of an uninterrupted cipher**. On the author's own ciphertext, a
  period-8 Vigenère with 6 interrupts in 251 runes is *invisible* to the Friedman
  scan, and restoring the interrupt phase recovers the full signal
  (`preventer-blinds-absolute-tests.md`). Friedman indexes runes by absolute
  position, so one interrupt corrupts every coset downstream.

  The correction does not rescue this hypothesis, because the IoC bound above is
  phase-independent: a perturbation changes *which* alphabet is used at a position,
  never *how many* alphabets exist. But the Friedman leg must not be cited on its own
  against any cipher in the preventer family.

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
