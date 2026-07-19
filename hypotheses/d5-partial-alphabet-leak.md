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

Resolving partial-vs-full would need to separate 102 matches from 114 against
Poisson noise ~10 — roughly **4x more within-word d5 pairs than the corpus
contains**. With sections 0-9 fixed, this fork is effectively **undecidable**:
the base may be word-locked or may drift within the word; the echo statistic
cannot tell.

## Status

**Status**: partial (echo real and word-anchored; partial-vs-full leak
underpowered, likely undecidable on this corpus)

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
above flat, and word-anchored (cross-word d5 flat). Whether it is a **partial**
leak (base drifts within the word; point estimate q~0.72) or a **full** leak
(clean word-locked, exact-order-5 base; q=1) is **not resolved** — the bootstrap
95% CI [1.15, 1.72] contains the full-leak value 1.60, and the corpus is ~4x too
small to separate them. Do not cite the "72% / base drifts within the word"
reading as established; it is a point estimate awaiting more data or a
decryption. What is solid: a real, word-anchored period-5 same-alphabet echo.
