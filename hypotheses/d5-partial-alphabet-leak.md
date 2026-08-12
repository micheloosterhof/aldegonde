---
type: observation
---
# Characterization: The d5 Echo is a Same-Alphabet Leak (partial-vs-full is underpowered)

## Claim

The within-word distance-5 coincidence excess
(`within-word-d5-coincidence.md`) is a **same-alphabet leak** — positions 5
apart inside a word tend to be enciphered under the same alphabet, so the
plaintext's own coincidence shows through. This is solid: IoC **1.43**
(102/2073) sits **3.7 sigma above** the flat baseline of 1.00, and cross-word
d5 is flat (1.01), so the echo is real and word-anchored.

**What is NOT established: whether the leak is partial or full.** The point
estimate 1.43 is below the natural-runeglish full-leak value ~1.60 (real
English prose, 128k words), which would suggest only ~72% of within-word
5-gaps share the alphabet — i.e. a base that changes inside the word. But the
data cannot support that conclusion. The word-level bootstrap 95% CI for the
LP d5 IoC is **[1.15, 1.72]**, which **contains the full-leak value 1.60**.
Against the length-matched full-leak expectation (113.5 matches, IoC 1.59) the
observed 102 is only z = -1.1 — not significant. So a **clean word-locked,
exact-order-5 base (full leak, q=1) is entirely consistent** with 1.43.

Resolving partial-vs-full **by the size of the echo alone** would need to separate
102 matches from 114 against Poisson noise ~10 — roughly 4x more within-word d5
pairs than the corpus contains. That is why this fork stood as undecidable.

**RESOLVED (August 2026) by using d3 and d4 as controls instead**
(`experiments/period5_confirmation.py`). The absolute size of the d5 echo is the
underpowered statistic; the PROFILE across distances is not. Against real
consecutive prose carried into runeglish and resampled to the LP's own word-length
histogram:

| d | LP | plaintext | chance | verdict |
|---|---|---|---|---|
| 3 | 3.70% | 5.30% | 3.45% | **chance** (z vs plaintext −5.9) |
| 4 | 4.10% | 5.38% | 3.45% | **chance** (z vs plaintext −3.7) |
| 5 | 4.92% | 5.51% | 3.45% | **plaintext** (z −1.2, z vs chance +3.1) |

**What this settles: one-alphabet-per-word is REFUTED.** It predicts
plaintext-level coincidence at d3 and d4 as well, and the corpus sits at chance
there — 5.9σ and 3.7σ below plaintext. So `g` exists and has order exactly 5; the
period-5 architecture is measured, not merely plausible. The d3/d4 cells supply an
internal reference for "scrambled", which is why this works where the IoC bootstrap
could not: it tests the SHAPE of the profile, not the magnitude of one cell.

**What it does NOT settle: φ5 is still open.** An earlier version of this note
claimed φ5 ≈ 1 on the grounds that d5 is within 1.2σ of plaintext. That is a
consistency statement, not an estimate. The point estimate is
`(LP − chance)/(plaintext − chance)`:

| runeglish convention | prose d5 | φ5 | z from full leak |
|---|---|---|---|
| `ing` → ᛝ (one rune) | 5.51% | 0.71 | −1.2 |
| `ing` → ᛁᛝ (two runes) | 5.75% | 0.64 | −1.8 |

Both readings are legitimate — the Ing rune is valued NG **or** ING in the Gematria
Primus — so the convention is a genuine ambiguity and φ5 lands at 0.64–0.71 either
way, consistent with full leak but below it. That is the same standing as the
0.85 ± 0.26 recorded below, so the partial-vs-full fork remains underpowered and
the "base may drift within the word" reading is NOT retired.

## Status

**Status**: partial — one-alphabet-per-word REFUTED and order-5 `g` confirmed via
the d3/d4 controls; φ5 itself still underpowered (0.64–0.71, consistent with full
leak, convention-dependent)

The echo measurement is solid. The *partial*-leak reading — and with it the
"base drifts within the word" interpretation — is a point estimate that does
not reach significance against full leak; do not treat it as established.
The full-leak reference is ~1.60 on real prose (higher, ~1.74, on a random
dictionary word list, which over-weights long words). The point estimate 1.43
is below both, but not significantly (see the CI above).

## Mechanism

Read every within-word coincidence as "did the flattening happen here?" The
cipher flattens plaintext (IoC ~1.77) to flat ciphertext (IoC 1.00) by mixing
alphabets. Where two positions reuse the **same** alphabet the flattening
fails and the plaintext coincidence leaks; where they use different alphabets
it flattens to 1.00.

- **d1 (adjacent)**: IoC 0.18 — *below* flat. Related alphabets whose relation
  suppresses coincidence (the g-diagonal). Boundary-blind (within 0.0063,
  seam 0.0079). (Real prose d1/d2 are themselves flat, ~1.0, so the
  suppression at d1 is a genuine cipher effect, not a plaintext artifact.)
- **d2/d3/d4**: IoC 1.01 / 1.07 / 1.19. Real prose d3/d4 are elevated
  (~1.57/1.51); the LP tracks a *damped* version, rising toward d5.
- **d5 within**: IoC **1.43** — real echo (3.7 sigma above flat), but its
  point value is consistent with anything from partial to full leak.
- **d5 cross-word**: IoC 1.01 — flat. Different alphabets (phase differs
  across the boundary).

Two-alphabet-state model: if a within-word 5-gap shares the alphabet with
probability `q` and is otherwise independent, using the real-prose full-leak
rate 0.0550 (IoC 1.60),

```
rate(d5,within) = q * 0.0550 + (1 - q) * 0.0345 = 0.0492  ->  q = 0.72
```

A word-locked base with exact order-5 g forces `q = 1`. The point estimate
`q = 0.72` would mean the alphabet changes across ~28% of within-word 5-gaps
(slow intra-word drift, or g⁵≠id) — **but `q = 1` is inside the bootstrap CI**
(the 102 observed matches vs 113.5 expected under full leak is only z = -1.1),
so this q is a suggestive point estimate, not a measurement. See "Evidence
against".

## Second period-5 signature: d6 mirrors d1

The within-word coincidence profile organizes by **phase (d mod 5)**, not raw
distance — a second, independent confirmation of the period-5 structure that
does not depend on the fragile d10. Word-length permutation null (rune stream
kept intact, each section's word-length sequence shuffled, 10,000 perms;
`experiments/within_word_phase_profile.py`):

| d | phase | obs | null | z | p |
|---|---|---|---|---|---|
| 1 | 1 | 63 | 66.6 ± 3.9 | -0.9 | 0.20 (binomial vs flat: strongly suppressed, IoC 0.18) |
| **5** | **0** | **102** | **76.5 ± 7.8** | **+3.3** | **0.0010 excess (the echo)** |
| **6** | **1** | **31** | **44.5 ± 6.2** | **-2.2** | **0.0155 deficit (suppression recurs)** |

`d=1` and `d=6` are both **phase-relationship 1** — the same g¹ doublet
diagonal — and both sit below flat (IoC 0.18 and 0.71). The doublet
suppression **recurs at the period-5 interval.** This is striking because in
real prose d6 is one of the *highest*-coincidence distances (IoC 2.12): the
cipher takes a distance where plaintext coincides heavily and pushes it below
flat, which only happens if the g¹ relation that kills adjacent doublets acts
again 5 positions later. Quantitative caveat (`mixed-cycle-progression.md`):
at the LP-implied tuning depth no simulated mechanism reproduces the d6
DEPTH — simulated 0.033-0.040 vs observed 0.0245 — so the g¹ recurrence
accounts for the direction of the dip, not its magnitude.

So the period-5 is confirmed twice: **excess at phase 0 (d5), suppression at
phase 1 (d1 and d6).** Multiple-testing note: d5 (p=0.001) survives correction
over the 10-distance scan; d6 (p=0.016) does not on its own, but it is a
*directed* prediction (the phase-1 image of the established d1 suppression),
so read it as corroboration of period-5, not a standalone discovery. Past d6
the samples collapse (d7=713 pairs down to d10=88) and are noise; the d5 echo's
real period-5 partner is **d6's suppression**, not the unmeasurable d10.

## Evidence for

**Clean corpus** (sections 0-9 of `data/page0-58.txt`, 12,956 runes; words
tokenized with `- . & %`, `/` and newlines are line wraps and words flow
across them).

| distance | rate | IoC | same-alphabet fraction |
|---|---|---|---|
| flat baseline | 0.0345 | 1.00 | 0.00 |
| **d5 within** | **0.0492** (102/2073) | **1.43** (CI [1.15,1.72]) | 0.72 (pt est) |
| d5 cross-word | 0.0347 (377/10878) | 1.01 | ~0.00 |
| plaintext prose ref | ~0.0550 | ~1.60 | 1.00 |

**Plaintext reference**: 128,577 words of real English prose (Project
Gutenberg #1342) converted to runeglish with the gematria digraph rules (TH,
EO, NG, OE, IA, EA, IO merge; K->C, Q->C, V->U, Z->S). Within-word IoC profile:
d1 1.005, d2 1.011, d3 1.569, d4 1.514, **d5 1.595** — i.e. natural runeglish
is flat at d1/d2 and elevated (~1.5-1.6) at d3-d5, with no special *distance-5*
peak. So the LP's within/cross d5 asymmetry (cross-word d5 is flat, 1.01) is
created by the cipher's period-5 phase, and the "full leak" reference for a
same-alphabet 5-gap is ~1.60. (A random dictionary word list gives ~1.74,
biased high by over-weighting long words.)

## Position decomposition: drift disfavored, phase insufficient

Decomposing every within-word pair by absolute start position and word length
(`experiments/within_word_position_decomposition.py`, clean corpus) tests
whether phase (d mod 5) captures all the structure:

- **No within-word drift.** The d5 echo is **flat across absolute start
  position** (i=0..i≥3: 0.043/0.049/0.053/0.059, homogeneity p=0.70) — if
  anything rising, not decaying. Base drift would make the echo *decay* as a
  pair starts later in the word (more accumulated drift). It doesn't. So the
  base is **word-locked**, and the partial leak is **not** intra-word drift.

  **Independently confirmed, August 2026** (`experiments/d5_profile_and_position.py`),
  against a different null — the structure-free surrogate of
  `negative-control-battery.md` rather than a within-file permutation. Per
  start position the rates run 0.0434 / 0.0487 / 0.0529 / 0.0552 / 0.0673 with
  homogeneity **chi2 = 4.89 on 8 df, p = 0.77**, and the fitted slope is
  **+0.00485 per position against a surrogate +0.00024 ± 0.00294, z = +1.57**.
  Since the surrogate preserves the word-length structure, the confound that
  later start positions exist only inside longer words is controlled, and it
  contributes nothing. The rise remains non-significant and was tested only
  after being noticed, so it carries no weight — but its *sign* is the
  load-bearing part, and it is positive. No drift.
- **No word-initial anomaly.** d1 doublet suppression is uniform across
  position including i=0 (the pair right after the σ step), p=0.12. σ does not
  make the first letter special.
- **d1 ≠ d6 is real but does NOT discriminate the mechanisms.** d1 = 0.0064 and
  d6 = 0.0245 (disjoint Wilson CIs, robust at L≥7). An earlier draft here claimed
  this "contradicts pure order-5-g (g⁶=g¹)" — that was **wrong**. The coincidence
  rate is `P(p[i]=g(p[i+d]))`, the g-diagonal evaluated on *distance-d skip-grams*;
  the same g¹ relation acts on adjacent bigrams at d1 (plaintext 0.0320) but on
  6-apart skip-grams at d6 (plaintext 0.0552), so d1 ≠ d6 is *expected*. Direct
  simulation (`mechanism_discriminator.py`, real runeglish words) confirms **both**
  advance-every-letter order-5-g and the stay-slot order-4+hold produce d1 ≠ d6.
- **The damped rising shoulder is the defensible "more than period-5".** LP's
  d2→d5 (0.0347/0.0370/0.0410/0.0492) tracks a roughly half-damped copy of the
  plaintext's own rising within-word profile (0.0466/0.0488/0.0534/0.0565), with
  *extra* suppression at the phase-1 distances d1 and d6. So period-5 sets the
  **envelope** (suppress at phase-1) and a **partial plaintext leak** sets the
  rising magnitude underneath. The partiality is neither drift (flat over
  position) nor a length effect (checked) — it is **uniform**, consistent with
  the per-word σ step damping the leak by a constant factor everywhere.
- **Order-5-g vs stay-slot: SEPARATED (July 2026) — stay-slot disproved.**
  In d1..d6 simulation the SSE winner flips with the random g-tuning seed
  (`mechanism_discriminator.py`), and stay-slot's d1 = plaintext-doublet/5
  = 0.0064 was parameter-free — but the doublet position-profile test
  (`experiments/doublet_position_profile.py`) settles it: stay-slot's
  doublets are plaintext double letters (start-forbidden, end-heavy in
  every register) and the observed doublets are positionally flat.
  Stay-slot is disproved (`stay-slot-hold.md`); the tuned order-5-g
  formulation stands, with the constraint that its diagonal bigram class
  be positionally near-baseline.

**φ-ladder restatement (July 2026)**: inverting the full within-word
staircase through r_d = φ_d·K_d + (1−φ_d)·(1−K_d)/28 with K_d measured
on real words of register prose in the LP length mix
(`experiments/mixed_cycle_g.py`) gives φ5 = 0.85 ± 0.26 — consistent
with full leak (order-5 predicts φ5 = 1) and with partial leak alike,
matching the bootstrap verdict here: partial-vs-full is undecidable on
this corpus. (Measuring K_d on random stream segments instead of real
words biases φ5 low.) The mixed-cycle explanation of the partiality is
disproved by the d6 cell (`mixed-cycle-progression.md`).

## Evidence against

- **Partial-vs-full is underpowered — this is the load-bearing caveat.** The
  102 within-word d5 matches vs the length-matched full-leak expectation of
  113.5 is z = -1.1, not significant. The word-level bootstrap 95% CI for the
  IoC is [1.15, 1.72] and **contains the full-leak value 1.60**. So a clean
  word-locked, exact-order-5 base (q=1, full leak) is consistent with the data;
  the ~72% is a point estimate, not an established fraction. Separating 102
  from 114 against Poisson ~10 needs ~4x more d5 pairs than sections 0-9
  provide, so on this corpus the fork is likely **undecidable**.
- **Drift vs imperfect period is also not separable** (even granting partial).
  The shortfall, if real, is equally explained by slow intra-word base drift or
  by `g` not being exactly order 5 (g⁵≠id). The clean discriminator is
  d10-within, but words are too short: d10-within has only 88 eligible pairs
  (2/88), d15 zero.
- **The d3/d4 shoulder is a plaintext feature, not a d5-only spike.** Real
  prose is itself elevated at d3/d4 (~1.57/1.51) and the LP tracks a damped
  version (1.07/1.19), rising toward d5 — consistent with period-5 phase
  regardless of whether the leak is partial or full.

## Predictions

- The phase (the period-5 that produces the within/cross asymmetry) **resets
  per word** — a global phase would leak across word boundaries too, and
  cross-word d5 is flat (1.01). This is solid.
- Whether the base is word-locked or drifts within the word is **not decided**
  by this statistic. If a future measurement (more corpus, or a decryption)
  does resolve it, the point estimate leans partial (q~0.72) but full leak is
  within the current CI.
- *If* the leak is partial, a rune-level iid drift with change probability r
  and a g-diagonal d_g can reproduce both the d5 leak and the doublet
  suppression: `d1 = (1-r) d_g + r/29`, `d5 = P5*0.055 + (1-P5)/29`; `r ~ 0.10`,
  `d_g ~ 0.003` fits both. This is a consistency demonstration, not evidence
  that drift is occurring — full leak fits the d5 datum too.

## Scripts

- `experiments/d5_partial_leak.py` — reproduces the numbers above: the LP
  within/cross coincidence-IoC profile (d1..d5, d10), the same-alphabet
  point-estimate q, and the significance tests (echo vs flat z=+3.7; partial
  vs full-leak z=-1.1, not significant). The full-leak reference (prose d5
  0.055) is documented in the script; the dictionary proxy is a cross-check.
- `experiments/within_word_phase_profile.py` — the d1-d10 word-length
  permutation null (d5 excess p=0.001, d6 deficit p=0.016).
- `experiments/within_word_position_decomposition.py` — coincidence by absolute
  position and word length: d5 echo flat over position (no drift, p=0.70), d1
  suppression uniform (p=0.12), and the d1≠d6 gap (0.0064 vs 0.0245).
- `experiments/mechanism_discriminator.py` — enciphers real runeglish words with
  order-5-g and stay-slot; shows both reproduce d1≠d6 and the d5 echo, the d1..d6
  SSE winner is seed-unstable, and LP tracks a damped copy of the plaintext
  shoulder. The two mechanisms are not separated by the within-word profile.

## Related

- `within-word-d5-coincidence.md` — the parent anomaly; the shared per-word
  key state is real (echo confirmed), but whether the base is constant across
  the word or drifts is not decided here.
- `per-word-related-alphabets.md`, `five-block-boundary.md`,
  `position-within-word.md` — word-aware mechanism families, all consistent
  with the confirmed echo; the d5 statistic does not choose among word-locked
  vs drifting base.
- `doublet-spacing-poisson.md`, `explicit-doublet-avoidance.md` — the
  boundary-blind doublet suppression, the other face of the rune-scale base.
- `rune-s-lag5-echo.md` — the rune-identity structure inside the same excess.

## Verdict

The within-word d5 echo is a confirmed same-alphabet leak: IoC 1.43, 3.7 sigma
above flat, and word-anchored (cross-word d5 flat). The period-5 structure is
confirmed twice — **excess at phase 0 (d5, p=0.001), suppression at phase 1
(d1 and d6, d6 deficit p=0.016)** — so the mechanism has a real 5-periodicity,
not just a single echo. Whether the d5 leak is **partial** (base drifts within
the word; point estimate q~0.72) or **full** (clean word-locked, exact-order-5
base; q=1) is **not resolved** — the bootstrap 95% CI [1.15, 1.72] contains the
full-leak value 1.60, and the corpus is ~4x too small to separate them. Do not
cite the "72% / base drifts within the word" reading as established; it is a
point estimate awaiting more data or a decryption. What is solid: a real,
word-anchored, twice-confirmed period-5 same-alphabet structure.
