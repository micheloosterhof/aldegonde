# Finding: Lag-5 Paired-Match Structure

## Claim

The unsolved ciphertext contains a genuine, globally significant excess of
*paired* lag-5 coincidences: positions i with C[i] = C[i+5] occur in pairs
separated by exactly 1 or exactly 4, far more often than chance. Equivalently,
consecutive non-overlapping 5-grams agree in their (1st, 2nd) positions or in
their (1st, 5th) positions more often than they should.

## Status

**Status**: confirmed (characterization)

This is a statistical property of the ciphertext, not a cipher hypothesis.
Any valid cipher hypothesis must now explain it (alongside the constraints in
`README.md`).

## The numbers

Let M[i] = [C[i] == C[i+5]] over the 12,956-rune unsolved corpus.

| Statistic | Observed | Expected | Significance |
|-----------|----------|----------|--------------|
| Sum of M (mono lag-5 matches) | 479 | 446.6 | +1.5 sigma |
| Mono matches outside paired events | 422 | 444.6 | -1.1 sigma |
| Match pairs at separation d=1 | 29 | 17.7 | +2.7 sigma |
| Match pairs at separation d=4 | 28 | 17.7 | +2.4 sigma |
| Match pairs at d=2,3,5..25 | flat | — | all within noise |
| Joint T(5) = d1 + d4 pairs | 57 | 30.7 +/- 6.5 | local z = +4.1 |
| T(5) split-half | 28 + 29 | — | stable |
| Global Monte Carlo, max T(L) over L=2..50 | — | median 45 | **p ~= 0.01** |

The monographic lag-5 excess (+1.5 sigma) is entirely accounted for by the
paired events: outside them, mono matches are at chance. The phenomenon is
purely about pairs.

Plain digraphic kappa (the d=1 component alone, 29 vs 15.4, +3.5 sigma) is
NOT globally significant by itself — a max over lags 2..150 in null text
reaches +3.47 about 38% of the time, and lag 129 scores +3.78 in the real
text. The significance comes from the joint d=1 + d=4 statistic, which
survives max-over-lags correction at p ~= 0.01 and replicates in both halves.
Caveat: the pattern family (separations {1, L-1}) was chosen after seeing the
data; the d=4 margin was measured after d=1 flagged, but it is an orthogonal
component and landed exactly on the complementary separation 5-1=4.

## Spatial distribution

- Per-section lag-5 digraph kappa: section 4 (positions 3612..5506, LP pages
  ~15-22) carries z = +3.84 on its own (8 hits vs 2.2); section 8 is +1.82;
  all others are within noise. Within sections 4+8, lag 5 tops the whole lag
  spectrum (+3.81).
- Two loose pockets inside section 4: positions ~3715-3975 and ~5324-5495
  (sliding-window z up to +4.0). Matches inside pockets are scattered
  (gaps 1..38, no contiguous runs), with several gaps of exactly 29 noted
  but not significant.
- No mod-5 phase preference anywhere: the pattern is translation invariant.
- Events freely cross word boundaries. All 29 d=1 digraph values are
  distinct; no repeated rune values drive the effect.

## Mechanisms ruled out by the chase

- **Period-5 polyalphabetic (any 5 alphabets)**: would put the mono lag-5
  kappa at plaintext IoC (~1.7 normalized, tens of sigma). Observed 1.073.
- **Plaintext autokey with 5-symbol feedback**: C[i]=P[i]+P[i-5] makes mono
  lag-5 matches equal plaintext lag-10 coincidences (~6%). Observed 3.7%.
- **Ciphertext autokey with depth-L feedback, any tabula recta, L=1..8**:
  splitting C[i] by C[i-L] must yield permuted-plaintext groups with IoC
  ~1.7. Measured mean group nIoC: L1=1.026 (doublet artifact), L2..L8 all
  0.99-1.01, flat. Extends the depth-1/2 disproof in
  `ciphertext-autokey.md` to depth 8.
- **Fixed-grid seriation / columnar structure of width 5**: would impose a
  mod-5 phase on events. None observed.
- **Locally period-5 keystream patches** (key stuck repeating for a
  stretch): would make pocket matches contiguous runs at ~6% density.
  Pocket matches are scattered singletons and pairs.

## What could explain it (open)

The constraint for future hypotheses: a mechanism must generate consecutive
5-grams agreeing in (1st,2nd) or (1st,5th) positions ~85% above chance,
concentrated in (but not exclusive to) section 4, while leaving every other
statistic in `README.md` flat — including doublet suppression and zero
triplets. Directions not yet tested:

- Bifid/trifid-like fractionation with period 10 (classical bifid produces
  digraphic coincidence bumps at half the period; a 29-symbol fractionation
  scheme is nonstandard but Cicada-plausible).
- Per-word or per-line cipher state where 5-rune-distant positions share key
  material as a side effect of typical word lengths (avg word ~3.9 runes).
- Section 4 having a different (or buggier) cipher than other sections.

## Scripts

- `experiments/lag5_digraph_chase.py` — full reproduction of every number
  in this file.
- `experiments/aligned_kappa_nulls.py` — the original detection.

## Related

- `ciphertext-autokey.md` — depth-L split evidence extended here.
- `bifid-fractionation.md` — the leading untested mechanism family for this
  signature.
- `doublet-spacing-poisson.md` — the other confirmed characterization.

## Verdict

Real structure at global p ~= 0.01, the first statistically significant
deviation from randomness in the unsolved corpus beyond doublet suppression.
The cipher is NOT a clean stream cipher: something in its mechanics couples
positions 5 apart, in pairs bracketing 5-gram windows.
