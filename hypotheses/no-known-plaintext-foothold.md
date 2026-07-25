---
type: observation
---
# No Known-Plaintext Foothold; Section 11 is the Only Plaintext Section

## Status

**Status**: confirmed (characterization) for the no-known-plaintext claim
itself. The "Consequences for the attack" section is conditional on the
length-clocked-walk model, which is plausible, not confirmed.

## Claim

The attack on sections 0-9 must be **blind (ciphertext-only)**. There is no
known-plaintext pair available inside `data/page0-58.txt`: the one readable
section, **section 11 (the Parable), is stored as unencrypted plaintext** — it
was never run through the 0-9 cipher, so it yields no plaintext↔ciphertext pair.

## Evidence

- Section 11 transliterates directly (Gematria Primus rune→English):
  "PARABLE. LIKE THE INSTAR TUNNELING TO THE SURFACE. WE MUST SHED OUR OWN
  CIRCUMFERENCES. FIND THE DIVINITY WITHIN AND EMERGE." — 95 runes, clean English.
- Its IoC is **1.82** (rough, plaintext-like) versus ~1.0 for the encrypted
  sections 0-10 (sec 0 0.99, sec 8 1.00, sec 9 0.98, sec 10 0.94). So section 11
  is the *only* plaintext section; everything else is flat/enciphered.
- The Parable text yields no locatable crib inside 0-9: no test run
  (running-key slides, kappa scans) finds it, and an enciphered copy under
  the unknown cipher would be undetectable by those tests anyway — so it
  provides no foothold, which is weaker than proving it absent.

Useful by-product: section 11 confirms real LP plaintext IoC ≈ 1.8, matching the
runeglish-is-rougher-than-English fact and better than dictionary/prose proxies.

## Consequences for the attack

- **No algebraic known-plaintext recovery** of `(base_0, g, σ)`. The blind
  hillclimb is the only direct path, and it fights the diffusion barrier (three
  globally-coupled permutations, no fitness gradient until nearly solved).
  **The gradient problem has a partial answer**: score candidate keys on
  the 465 two-rune words instead of on n-gram fitness. In runeglish THE
  is exactly `ᚦᛖ`, and the 2-rune word class is dominated by eight
  function words (69% of tokens), so a correct key yields ~75-108 `ᚦᛖ`
  decryptions where chance gives 0.6, and the register log-likelihood
  over the whole class supplies the partial credit a pure count cannot.
  See the Predictions section of `length-clocked-walk.md`. This is a
  statistical crib rather than a known-plaintext foothold — it assumes
  only that the plaintext is ordinary English, not that any particular
  word sits at any particular place.
- The deterministic-walk structure is the exploitable weakness instead: DJU-BEI
  gave one state-return constraint (`base_1477 = base_2926`, `[g] = −1449[σ]`);
  a systematic hunt for repeated ciphertext structures could add more equations
  on `(g, σ)` — a collision/constraint attack that uses the determinism the
  hillclimb ignores.

## Related

- `length-clocked-walk.md` — the candidate model and its key (plausible,
  not confirmed).
- `repeated-phrase-dju-bei.md` — the one known state-return constraint.
- `experiments/length_clocked_cipher.py` — encrypt/decrypt + round-trip.
