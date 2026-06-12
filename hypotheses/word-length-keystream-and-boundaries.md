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

**Measurement** (word-length autocorrelation, permutation z, lags 1-6):

| lag | unsolved (n=2953) | solved LP (n=698) | English prose (n=13512) |
|-----|-------------------|-------------------|--------------------------|
| 1 | -0.007 (z=-0.4) | **-0.086 (z=-2.2)** | **+0.056 (z=+6.5)** |
| 2 | +0.018 (z=+1.0) | **+0.092 (z=+2.5)** | **+0.021 (z=+2.4)** |
| 3 | -0.017 (z=-0.9) | +0.015 (z=+0.4) | **+0.062 (z=+7.3)** |
| 4 | +0.012 (z=+0.6) | +0.037 (z=+1.0) | **+0.062 (z=+7.4)** |
| 5 | +0.024 (z=+1.3) | +0.014 (z=+0.4) | **+0.060 (z=+6.0)** |
| 6 | -0.018 (z=-1.0) | +0.002 (z=+0.1) | **+0.049 (z=+5.9)** |

Three distinct signatures. Generic prose is positive at every lag (topic
clustering). The solved LP register shows a short-range -/+ ALTERNATION at
lags 1-2 only (function/content word alternation, no long-range drift).
The unsolved cipher is flat at all six lags. With 2953 words, the solved
pages' lag-1 autocorrelation would surface at ~4.7 sigma if shared; it
does not. Register-matched joint test on the two informative lags (solved
vs unsolved, lags 1+2): chi2 ~ 6.6 on 2 df, **p ~ 0.036**.

**Why this is NOT yet a finding**: English word-length autocorrelation is
**register-dependent and not even a fixed sign** — generic prose is
positive (+0.06 at every lag), the solved LP koans alternate -/+ at lags
1-2 only. A flat sequence sits between them, so flatness alone cannot
prove synthetic boundaries. The register-matched joint comparison (solved
vs unsolved LP, same author/work, lags 1+2) reaches p ~ 0.036 —
suggestive, not conclusive.

**Status: unresolved.** The unsolved word-length sequence is flatter than
both the solved pages and generic English at every lag through 6, which
would be expected if the boundaries were placed to match a length
histogram without copying English word *order* — but the register-matched
evidence is ~2 sigma and confounded by the small solved sample.
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
