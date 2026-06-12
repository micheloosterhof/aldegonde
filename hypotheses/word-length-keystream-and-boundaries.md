# Word-Length Keystream & Boundary Authenticity

Two probes of the one confirmed open channel — the word lattice (boundaries
+ lengths), which is transmitted as readable plaintext metadata.
(`experiments/word_lattice.py`, June 2026.)

## A. Keystream from word-length context — disproved

**Claim tested**: the keystream is a function of the local word-length
pattern (own length, position-in-word, neighbour lengths). This is
attractive because it would key the cipher from plaintext metadata the
solver can also read, and the DJU-BEI repeat's length context (2, [3,3], 2)
matches at both occurrences.

**Method**: bucket every rune by a length-context key; if runes sharing a
bucket share keystream, their within-bucket pairwise coincidence rate rises
from 1/29 toward the plaintext IoC (~0.06+).

| context key | coincidence rate (1/29 = 0.03448) | z |
|-------------|-----------------------------------|---|
| (pos, wlen) | 0.03438 | -0.85 |
| (pos, wlen, prev-len) | 0.03456 | +0.26 |
| (pos, wlen, next-len) | 0.03455 | +0.23 |
| (pos, wlen, prev, next) | 0.03473 | +0.31 |
| (pos, wlen, prev, prev2) | 0.03408 | -0.52 |

**Status: disproved.** Every bucketing stays exactly at 1/29. The keystream
is not any function of the word-length lattice. (Consistent with the
word-transform census and the J battery: the key varies at rune
granularity and ignores word metadata.)

## B. Boundary authenticity — unresolved (a real but inconclusive tension)

**Question**: are the word boundaries plaintext-faithful, or synthetic? A
synthetic length sequence (placed to mimic an English length *distribution*
without sequential structure) would lack the lag autocorrelation real prose
carries.

**Measurement** (lag-1 word-length autocorrelation, permutation z):

| text | n | lag-1 r | z |
|------|---|---------|---|
| unsolved cipher | 2953 | -0.007 | -0.37 |
| solved LP pages | 698 | -0.086 | -2.23 |
| generic English prose | 13512 | +0.059 | +6.92 |

The unsolved length sequence has **no detectable sequential structure** at
high power (all lags 1-3, |z| < 1.1), while both the solved LP pages and
generic English prose do (|z| = 2.2 to 6.9). With 2953 words, the solved
pages' autocorrelation would surface at ~4.7 sigma if shared; it does not.

**Why this is NOT yet a finding**: English word-length autocorrelation is
**register-dependent and not even a fixed sign** — generic prose is
positive (+0.06), the solved LP koans are negative (-0.086). A flat
sequence sits between them, so flatness alone cannot prove synthetic
boundaries. The register-matched comparison (solved vs unsolved LP, same
author/work) gives only z = -1.86 for the lag-1 difference — suggestive,
not significant.

**Status: unresolved.** The unsolved word-length sequence is flatter than
both the solved pages and generic English, which would be expected if the
boundaries were placed to match a length histogram without copying English
word *order* — but the evidence is ~1.9 sigma and confounded by register.
This is the one assumption-questioning lead worth revisiting with a
register-matched runeglish corpus (philosophical/koan prose with word
boundaries), which the repo does not currently contain.

**If confirmed**, it would matter a lot: it would mean the boundaries are a
separate synthetic layer, the "English-like word lengths" are a histogram
match rather than real word structure, and cribbing on word identity is
futile. **If refuted**, boundaries are real and the lattice remains the
best crib surface.

## Other checks (null)

- Doublet-containing words: length distribution matches the per-length
  doublet *opportunity* (L-1 adjacencies) — no excess at any length.
- Adjacent short-short word clustering: unsolved at chance (z=+0.18).

## Scripts

- `experiments/word_lattice.py` — all three probes.

## Related

- `repeated-phrase-dju-bei.md` — the length-context match that motivated A.
- `word-transform-census.md`, `autokey-plus-substitution.md` — rune-level
  key variation, consistent with A's negative.
