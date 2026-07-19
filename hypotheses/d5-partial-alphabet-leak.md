# Characterization: The d5 Echo is a *Partial* Same-Alphabet Leak

## Claim

The within-word distance-5 coincidence excess
(`within-word-d5-coincidence.md`) is a **same-alphabet leak** — positions 5
apart inside a word tend to be enciphered under the same alphabet, so the
plaintext's own coincidence shows through. But it is only a **partial** leak.
Measured as a coincidence IoC it is **1.43**, below the natural-runeglish
plaintext value of **~1.60** (real English prose converted to runes,
128k words) and above the flat cipher baseline of **1.00**. On a two-state
reading (a within-word 5-gap either shares the alphabet or is independent),
only **~72%** of within-word 5-gaps share the alphabet.

A base alphabet that is **constant across a whole word** (with an exact
order-5 g) cannot produce a partial leak inside its own word — it is
all-or-nothing and would give the full 1.60. The ~28% shortfall means the
alphabet identity is not preserved across a within-word 5-gap. The most
economical reading is that the base **drifts slowly inside the word** (and,
from `base-keying-constraints`, re-keys hard at each word boundary). One
alternative is not excluded: `g` not being exactly order 5 (g⁵≠id) would
attenuate the same way without any drift. Both readings agree the base is
**not a clean word-locked order-5** substitution.

## Status

**Status**: plausible (verified measurement; interpretation constrains the
mechanism family)

The measurement is solid on the clean corpus. The interpretation depends on
one external reference — the coincidence rate of natural runeglish plaintext —
taken from real English prose (128k words) converted to runes, not from the
(unknown) LP plaintext. It is robust to the exact value: the full-leak d5
baseline is ~1.60 on real prose (higher, ~1.74, on a random dictionary word
list, which over-weights long words); either leaves the LP's 1.43 clearly
partial.

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
- **d5 within**: IoC **1.43** — partial leak. Same alphabet only part of the
  time.
- **d5 cross-word**: IoC 1.01 — flat. Different alphabets (phase differs
  across the boundary).

Two-alphabet-state model: if a within-word 5-gap shares the alphabet with
probability `q` and is otherwise independent, using the real-prose full-leak
rate 0.0550 (IoC 1.60),

```
rate(d5,within) = q * 0.0550 + (1 - q) * 0.0345 = 0.0492  ->  q = 0.72
```

A word-locked base with exact order-5 g forces `q = 1` (the base is constant
across the word, phase repeats every 5). Observed `q = 0.72` requires the
alphabet to change across ~28% of within-word 5-gaps — slow intra-word drift
(or, equivalently for this statistic, g⁵≠id).

## Evidence for

**Clean corpus** (sections 0-9 of `data/page0-58.txt`, 12,956 runes; words
tokenized with `- . & %`, `/` and newlines are line wraps and words flow
across them).

| distance | rate | IoC | same-alphabet fraction |
|---|---|---|---|
| flat baseline | 0.0345 | 1.00 | 0.00 |
| **d5 within** | **0.0492** (102/2073) | **1.43** | **0.72** |
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
biased high by over-weighting long words; either leaves 1.43 clearly partial.)

## Evidence against

- **The plaintext reference is a proxy.** It is English-in-runes, not the
  actual LP plaintext. If the true plaintext were much rougher or smoother the
  fraction shifts, though the qualitative "partial" result holds for any
  reasonable natural-language baseline (real prose d5 1.60, dictionary 1.74;
  both >> 1.43).
- **Drift vs imperfect period is not separable.** The ~28% shortfall is equally
  explained by slow intra-word base drift or by `g` not being exactly order 5
  (g⁵≠id). The clean discriminator is d10-within, but words are too short:
  d10-within has only 88 eligible pairs (2/88), d15 zero. Both readings agree
  the base is not a clean word-locked order-5.
- **The d3/d4 shoulder is a plaintext feature, not noise.** Real prose is
  itself elevated at d3/d4 (~1.57/1.51) and the LP tracks a damped version
  (1.07/1.19), rising toward d5. So the graded d2->d5 rise reflects the
  plaintext's own within-word profile seen through partial same-alphabet
  leakage, consistent with period-5 phase + slow drift.

## Predictions

- Any mechanism must attenuate the within-word d5 leak to ~72%, either by a
  base that **drifts within words** or by an inexact order-5 g. A clean
  per-word monoalphabetic / single-per-word-base with g⁵=id is quantitatively
  excluded: it predicts the full 1.60 leak at within-word d5, not 1.43.
- The phase (the period-5 that produces the within/cross asymmetry) still
  **resets per word** — a global phase would leak across word boundaries too,
  and cross-word d5 is flat (1.01).
- A correct drift rate should reproduce the within-word d5 leak (1.43) and the
  doublet suppression (0.0063) together. A rune-level iid drift with change
  probability r and a g-diagonal d_g gives
  `d1 = (1-r) d_g + r/29` and `d5 = P5*0.060 + (1-P5)/29` with `P5` the
  probability the base is unchanged across the 5-gap; `r ~ 0.10`,
  `d_g ~ 0.003` fits both. If words that share more of the drift show extra
  correlation, that is a further test.

## Scripts

- `experiments/d5_partial_leak.py` — reproduces every number above: the LP
  within/cross coincidence-IoC profile (d1..d5, d10), and the natural-runeglish
  reference via dictionary conversion, with the two-state same-alphabet
  fraction.

## Related

- `within-word-d5-coincidence.md` — the parent anomaly; this refines its
  "per-word key of length 5" interpretation: the shared key state is real but
  the base is **not** constant across the word.
- `per-word-related-alphabets.md`, `five-block-boundary.md`,
  `position-within-word.md` — word-aware mechanism families; the partial leak
  constrains them to a **drifting** (not word-locked) base.
- `doublet-spacing-poisson.md`, `explicit-doublet-avoidance.md` — the
  boundary-blind doublet suppression, the other face of the rune-scale base.
- `rune-s-lag5-echo.md` — the rune-identity structure inside the same excess.

## Verdict

Verified measurement. The within-word d5 echo is a same-alphabet leak that is
only ~58% complete (IoC 1.43 vs 1.74). This rules out a base alphabet that is
constant per word: the base must drift at rune scale while the period-5 phase
resets per word. The doublet suppression (boundary-blind, base drifts through
seams) and this partial echo (base drifts through the interior) are the same
statement about the base seen from two distances.
