# Characterization: Distance-11 Coincidence Deficit (Cross-Word, mod-5 Phase)

## Claim

Single runes **eleven positions apart** coincide *less* often than chance in
the clean corpus: 386 matches vs ~447 expected (IoC 0.863, z ≈ −2.9). It is
the deepest trough in a lag-1..80 scan. The deficit lives **entirely in
cross-word pairs**, not within words, and it belongs to a mildly depleted
**5k+1 residue class** (6, 11, 16, 21, …, 76) rather than to the multiples of
5. The originating conjecture was 11 = 2·5 + 1 — an echo of the confirmed
lag-5 *excess* (`within-word-d5-coincidence.md`). That specific harmonic story
does **not** hold; a weaker mod-5 phase effect might.

## Status

**Status**: weak (nominal trough; does not survive multiple-test correction)

The count is a hard fact, but on its own the lag does not clear a lag-scan
correction (Šidák over 79 lags → p ≈ 0.26). The one thread keeping it above
noise is the mod-5 phase clustering, and that thread is partly circular. Kept
as a watch-item, not a finding.

## What was measured

Clean corpus: sections 0-9 of `data/page0-58.txt`, 12,956 runes, chance match
rate Σf² = 0.03455 (uniform 1/29 = 0.03448). Words tokenized with `- . & %`
as boundaries. The kappa scan uses the low-doublet null
(`aldegonde.stats.nulls.doublet_shuffle` at the observed doublet rate); z is
the standard score against that null, which matches the analytic
frequency-based null to two decimals.

**Headline (lag 11):** 386 vs null 446.5 ± 20.9. Monte-Carlo one-sided
p = 0.0014 (5,000 trials); two-sided p = 0.0038; **Šidák over the 79 scanned
lags → p ≈ 0.26.**

## The scan and its multiplicity budget

Lags 1..80, analytic frequency null:

| threshold | observed | expected over 79 lags |
|-----------|----------|-----------------------|
| \|z\| ≥ 2.0 | 2 | 3.59 |
| \|z\| ≥ 2.5 | 2 | 0.98 |
| \|z\| ≥ 3.0 | 0 | 0.21 |

Nothing reaches 3σ. The two deepest troughs are lag 11 (−2.95) and lag 76
(−2.56); the strongest peak is lag 47 (+1.97), then lag 5 (+1.52). The
observed count of extremes is within the noise budget for a scan this wide.

## The mod-5 phase pattern (the one non-trivial thread)

Grouping the scan's z-scores by lag mod 5:

| lag mod 5 | n | mean z | pooled z | members |
|-----------|---|--------|----------|---------|
| 0 | 16 | +0.08 | +0.33 | 5,10,15,20,… (would-be harmonics) |
| **1** | 15 | **−0.77** | **−2.97** | 6,11,16,21,…,76 (contains 11) |
| 2 | 16 | −0.03 | −0.12 | |
| 3 | 16 | +0.34 | +1.35 | |
| 4 | 16 | −0.11 | −0.44 | |

Only the 5k+1 class leans depleted, and it holds the two deepest lags. This is
**not the harmonic prediction**: a period-5 echo of the lag-5 excess would
enrich the multiples of 5 (class 0), which are flat.

**Circularity caveat (load-bearing).** We started from "lag 11 is low," and
11 ≡ 1 mod 5, so asking "is class 1 low?" is rigged toward yes. Removing the
two driver lags (11, 76), the rest of the 5k+1 family only leans to pooled
z ≈ −1.7. Suggestive, not solid. An out-of-corpus 5k+1 test is required before
this counts for anything.

## Within-word vs cross-word (refutes the short-word explanation)

The natural mechanical guess — "words are too short to hold distance-11 pairs,
so you see fewer repeats" — is true about within-word pairs but is **not where
the deficit is**:

| class | matches / pairs | rate |
|-------|-----------------|------|
| within-word | 1 / 35 | 0.0286 (at chance) |
| across-word | 385 / 12,910 | 0.0298 (below 0.03455) |

Only 35 within-word pairs exist at d=11 in the whole corpus (few words reach
length 12), and they sit at chance. The boundary-permutation null is therefore
uninformative here (obs 1 vs 1.0 ± 1.0). The entire deficit is carried by the
12,910 **cross-word** pairs, which word length does not constrain. Whatever
this is, it is a cross-boundary effect, the opposite locus of the lag-5 excess.

## Section concentration

Not diffuse. Full-corpus z = −2.95 at lag 11:

| section | n | z | IoC | drop it → global z |
|---------|---|---|-----|--------------------|
| 1 | 1,145 | −3.41 | 0.472 | −2.06 |
| 8 | 3,008 | −2.54 | 0.756 | −2.01 |
| others | — | ≥ −1.0 | ≥ 0.88 | — |

Sections 1 and 8 carry it; section 1 has *half* the expected coincidences at
d=11. Removing either drops the global signal to ~−2σ, but neither alone
accounts for all of it. Concentration in two sections is equally consistent
with a local artifact and with a real effect that only some sections encode.

## Interpretations to test

- **Word-length periodicity (leading candidate).** If sections 1/8 carry a
  repeating word-length rhythm, cross-word pairs at exactly d=11 could
  systematically connect the same word-position (e.g. word-initial to
  word-initial). If consecutive words rarely open with the same rune, that
  alone yields a cross-word coincidence deficit at one lag class. Test:
  tabulate the word-positions the 385 cross-word d=11 pairs connect, and check
  sections 1/8 for a word-length period. This is the unbuilt "test F".
- **Pure multiple-testing noise.** The default null: Šidák p ≈ 0.26 and the
  extreme-count budget are both consistent with it. The mod-5 clustering is
  the only evidence against, and it is circular until reproduced out-of-sample.
- **Not a period-5 harmonic.** The 2·5+1 framing is excluded as stated:
  multiples of 5 are flat, and lag 10 (the first harmonic) is at chance.

## Predictions

- If word-length periodicity is the cause, the deficit should track
  word-position alignment and vanish when pairs are stratified by word-position.
- If the mod-5 phase effect is real, the 5k+1 depletion should reproduce in an
  independent transcription and in the not-yet-scanned tail beyond lag 80,
  *excluding* lags 11 and 76.
- Any candidate decryption need not explain this until it survives correction;
  it is currently below the bar the lag-5 anomaly cleared.

## Scripts

- `experiments/lag11_depletion.py` — reproduces every number above: the
  lag-1..80 scan with multiplicity budget, the mod-5 decomposition, per-section
  and leave-one-out stability, the Monte-Carlo + Šidák significance, and the
  within/across-word split (built on the unit-tested
  `aldegonde.analysis.coincidence` boundary functions).

## Related

- `within-word-d5-coincidence.md`, `lag5-digraph-structure.md`,
  `docs/lag5-phenomenon.md` — the confirmed lag-5 *excess* this trough was
  conjectured to echo. It does not: that effect is within-word and enriching;
  this one is cross-word and depleting.
- `cryptodiagnostics-page0-58.md` — the battery whose "kappa flat to lag 3000,
  nothing survives multiple-test correction" line this deficit is consistent
  with.
- `position-within-word.md`, `word-length-keystream-and-boundaries.md` — the
  word-structure mechanisms the word-length-periodicity test would engage.

## Verdict

Not a finding. A real 61-match deficit at d=11 exists but does not survive a
lag-scan correction, and its most-cited framing (a 2·5+1 harmonic of the lag-5
excess) is falsified — the effect is cross-word and the multiples of 5 are
flat. The only reason to keep watching is the depleted 5k+1 residue class,
which is presently confounded by the circularity of having been found through
lag 11 itself. The decisive next step is the word-length-periodicity test on
sections 1 and 8; absent that, treat the trough as scan noise.
