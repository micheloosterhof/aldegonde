---
type: observation
---
# Bauer's Cross-Product Sum Finds Nothing (Flat Unigrams Make It Blind)

## Status

**Status**: confirmed (characterization), negative. The test is properly
calibrated and returns nothing at any window size from 29 to 2000 runes.

## Claim

Bauer's cross-product sum (`Decrypted Secrets`) decides whether two samples
follow the same distribution: for counts n_i and m_i it is
`chi = sum_i n_i * m_i`, which normalised estimates `sum_i p_i * q_i`. It is
the cross-text analogue of the IoC, classically used to decide whether two
ciphertext stretches share an alphabet.

Evaluated between every pair of windows of the unsolved corpus, **it shows no
structure whatsoever**. The heatmap is visually indistinguishable from the
same map computed on a shuffled corpus.

**This is expected, and the reason is worth recording: the cross-product sum
is a unigram statistic.** The LP's unigram distribution is flat (IoC = 1/29,
`flat-ioc.md`) and, as measured below, homogeneous across the corpus. A test
that can only see unigram distributions therefore has nothing to work with —
it is blind here by construction, not by bad luck. Any statistic in this
family (IoC, chi test, kappa against a fixed distribution) will return the
same null.

## Evidence

### Spread against a calibrated null

Localised alphabet structure would make chi vary more between window pairs
than shuffling the same corpus does. The null has identical window geometry
and identical unigram counts, so it isolates exactly that. Only
non-overlapping pairs (separation >= window) are used. Ratio is observed sd
over null sd; z is against the spread of 20 null draws.

| window | windows | pairs | vs plain shuffle | vs doublet-matched null |
|---|---|---|---|---|
| 29 | 1847 | 3394806 | 0.940 (z −4.90) | 0.993 (z −0.81) |
| 58 | 922 | 841806 | 0.931 (z −5.29) | 0.982 (z −1.41) |
| 100 | 515 | 261632 | 0.921 (z −5.69) | 0.982 (z −0.85) |
| 150 | 347 | 117306 | 0.913 (z −3.77) | 0.982 (z −0.96) |
| 200 | 256 | 63756 | 0.914 (z −2.51) | 0.960 (z −1.15) |
| 300 | 169 | 27390 | 0.921 (z −2.68) | 0.969 (z −0.97) |
| 500 | 100 | 9312 | 0.943 (z −1.10) | 1.000 (z +0.01) |
| 750 | 66 | 3782 | 1.030 (z +0.58) | 1.065 (z +0.70) |
| 1000 | 48 | 1980 | 1.006 (z +0.11) | 1.026 (z +0.29) |
| 1500 | 31 | 756 | 1.037 (z +0.29) | 1.103 (z +1.04) |
| 2000 | 22 | 342 | 1.066 (z +0.34) | 1.172 (z +1.21) |

Nothing exceeds the null in either direction once the right null is used. The
strongest individual window pair at window 300 reaches z = +4.30 raw, which is
Bonferroni p = 1 over the 1.5M pairs tested.

### Sections share one rune distribution

Chi-square homogeneity of the 29 rune counts across the ten clean sections:
**chi2 = 223.5 on 252 dof, p = 0.90**. Permutation nulls agree (plain shuffle
p = 0.88, doublet-matched p = 0.82). The sections are homogeneous, which is
consistent with `aligned-kappa-no-reset.md` finding no keystream reset at
section boundaries.

## Traps recorded

Four ways to read a signal into this that is not there:

1. **The bright diagonal is window overlap.** Windows closer than the window
   length share runes, and a window against itself gives `sum_i n_i^2`. The
   band is exactly as wide as the window. All statistics above exclude it.
2. **The off-diagonal blob texture is also overlap.** With a stride well below
   the window, neighbouring windows share nearly all their runes, so the chi
   field is smoothed over the window length — and smoothed noise looks like
   structure. The shuffled panel of the figure shows the same texture. This is
   why the figure renders the null beside the data on one colour scale.
3. **Against a plain shuffle the corpus looks underdispersed** — chi varies
   ~7% less than shuffled, z as low as −5.7, i.e. the LP spreads runes more
   evenly across the text than a random permutation of itself. This is
   entirely the known doublet suppression: under `c3301.low_doublet_null()`,
   which holds the observed doublet rate, the deficit vanishes (0.92 -> 0.99,
   z −5.7 -> −1). A plain shuffle is the wrong null for this corpus.
4. **A within-minus-cross-section window contrast reads p ~ 0.04** across
   windows 150-1000 and was nearly reported as a lead. It is an artifact. The
   sections run 9 to 3008 runes (sizes 729, 1145, 1729, **9**, 1894, 1021,
   1524, 1589, 3008, 308), so any null built by permuting the partition is
   unreliable and windows of 1000+ straddle several sections. The tell was
   that the contrast *grew* with window size (+0.00015 at 29 to +0.00339 at
   1000) — normalised chi estimates the same quantity at every window size,
   with only the noise shrinking, so a real per-section difference would be
   window-independent. The contingency test above settles it at p = 0.90.

## Scripts

- `experiments/cross_product_map.py` — the map, the null panel, the window
  sweep (`--sweep`), the null choice (`--null shuffle|doublet`), and the
  section homogeneity test.

## Related

- `flat-ioc.md` — the flat unigram distribution that makes this test blind.
- `doublet-suppression.md` — the effect behind trap 3.
- `aligned-kappa-no-reset.md` — the section-boundary result this agrees with.
- `cryptodiagnostics-page0-58.md` — the wider battery of negatives.

## Verdict

Negative, and structurally so. The cross-product sum is the right classical
tool for "do these two stretches share an alphabet", and it is well chosen —
but it reads only unigram distributions, and the LP's are flat and uniform
across the whole corpus. To distinguish windows here a statistic has to look
at rune *order*, not rune frequency. Do not re-run this family; the negative
is a property of the corpus, not of the window size, and the sweep already
covers two orders of magnitude of it.
