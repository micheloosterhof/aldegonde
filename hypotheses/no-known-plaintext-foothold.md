# No Known-Plaintext Foothold; Section 11 is the Only Plaintext Section

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
- The Parable text does not recur (enciphered) inside 0-9, so it is not a crib.

Useful by-product: section 11 confirms real LP plaintext IoC ≈ 1.8, matching the
runeglish-is-rougher-than-English fact and better than dictionary/prose proxies.

## Consequences for the attack

- **No algebraic known-plaintext recovery** of `(base_0, g, σ)`. The blind
  hillclimb is the only direct path, and it fights the diffusion barrier (three
  globally-coupled permutations, no fitness gradient until nearly solved).
- The deterministic-walk structure is the exploitable weakness instead: DJU-BEI
  gave one state-return constraint (`base_1477 = base_2926`, `[g] = −1449[σ]`);
  a systematic hunt for repeated ciphertext structures could add more equations
  on `(g, σ)` — a collision/constraint attack that uses the determinism the
  hillclimb ignores.

## Related

- `length-clocked-walk.md` — the model and its key.
- `repeated-phrase-dju-bei.md` — the one known state-return constraint.
- `experiments/length_clocked_cipher.py` — encrypt/decrypt + round-trip.
