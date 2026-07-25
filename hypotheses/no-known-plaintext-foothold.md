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
- **Tested on planted keys — the objective is a superb VERIFIER and a
  useless SEARCH GRADIENT** (July 2026,
  `experiments/two_rune_gradient.py`; simulated walk ciphertext over
  real English words in the LP length structure, known key):
  - Given `g` and `σ`, plain transposition hill-climbing recovers
    `base_0` **exactly, on the first restart** — the true key scores
    −1319 against −5366 for a random base (a gap of 4,047 nats, 8.7 per
    word), and all 79 planted THEs decrypt.
  - Searching `base_0` and `g` jointly **fails completely** (best −4901,
    `base_0` 0/29 correct), and all three jointly likewise.
  - The reason is measured directly: define score\*(g, σ) as the score
    after optimally fitting `base_0`. Then score\*(true) = −1296, while
    **σ off by a single transposition gives −4968 and a random key gives
    −4994** — one swap is already indistinguishable from noise. Same for
    a single conjugation of `g` (−4967).
  This quantifies the diffusion barrier exactly: `σ` and `g` enter the
  base chain once per word, so a one-swap error is applied ~2,900 times
  and every base past the first is destroyed. The landscape over
  `(g, σ)` is a delta function — flat everywhere, spiked only at the
  exact key. **Consequence for the attack architecture**: no
  hill-climb, annealing or evolutionary search over `(g, σ)` can work,
  with this or any comparable objective. `base_0` is effectively free
  (a 29!-fold reduction, solved by the objective in seconds), so the
  entire difficulty is concentrated in `(g, σ)`, which must come from
  **enumeration over structurally constrained candidates** — making the
  filter stack (`sigma-power-step.md`, `g-from-5x5-grid.md`) and the
  small-key construction problem the whole game.
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
