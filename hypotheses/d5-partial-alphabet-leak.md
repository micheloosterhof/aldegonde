# Characterization: The d5 Echo is a *Partial* Same-Alphabet Leak

## Claim

The within-word distance-5 coincidence excess
(`within-word-d5-coincidence.md`) is a **same-alphabet leak** — positions 5
apart inside a word tend to be enciphered under the same alphabet, so the
plaintext's own coincidence shows through. But it is only a **partial** leak.
Measured as a coincidence IoC it is **1.43**, well below the natural-runeglish
plaintext value of **~1.74** and above the flat cipher baseline of **1.00**.
On a two-state reading (a within-word 5-gap either shares the alphabet or is
independent), only **~58%** of within-word 5-gaps share the alphabet.

A base alphabet that is **constant across a whole word** cannot produce a
partial leak inside its own word — it is all-or-nothing and would give the
full 1.74. The 42% shortfall means the base alphabet **changes even inside a
word**. The cipher's base is therefore **not word-locked; it drifts at
sub-word (rune) scale** — the same boundary-blind behaviour the doublet
suppression already implied, now visible in the echo too.

## Status

**Status**: plausible (verified measurement; interpretation constrains the
mechanism family)

The measurement is solid on the clean corpus. The interpretation depends on
one external reference — the coincidence rate of natural runeglish plaintext —
which is taken from real English converted to runes, not from the (unknown)
LP plaintext. It is robust to the exact value: any plaintext IoC in the
confirmed 1.7-1.8 range leaves the leak clearly partial.

## Mechanism

Read every within-word coincidence as "did the flattening happen here?" The
cipher flattens plaintext (IoC ~1.74) to flat ciphertext (IoC 1.00) by mixing
alphabets. Where two positions reuse the **same** alphabet the flattening
fails and the plaintext coincidence leaks; where they use different alphabets
it flattens to 1.00.

- **d1 (adjacent)**: IoC 0.18 — *below* flat. Related alphabets whose relation
  suppresses coincidence (the g-diagonal). Boundary-blind (within 0.0063,
  seam 0.0079).
- **d2/d3/d4**: IoC 1.01 / 1.07 / 1.19 — at/near flat. Independent alphabets.
- **d5 within**: IoC **1.43** — partial leak. Same alphabet only part of the
  time.
- **d5 cross-word**: IoC 1.01 — flat. Different alphabets (phase differs
  across the boundary).

Two-alphabet-state model: if a within-word 5-gap shares the alphabet with
probability `q` and is otherwise independent,

```
rate(d5,within) = q * 0.0600 + (1 - q) * 0.0345 = 0.0492  ->  q = 0.58
```

A word-locked base forces `q = 1` (the base is constant across the word, phase
repeats every 5). Observed `q = 0.58` requires the base to change within the
word ~42% of the time over a 5-rune span — a rune-scale drift, not a per-word
reset.

## Evidence for

**Clean corpus** (sections 0-9 of `data/page0-58.txt`, 12,956 runes; words
tokenized with `- . & %`, `/` and newlines are line wraps and words flow
across them).

| distance | rate | IoC | same-alphabet fraction |
|---|---|---|---|
| flat baseline | 0.0345 | 1.00 | 0.00 |
| **d5 within** | **0.0492** (102/2073) | **1.43** | **0.58** |
| d5 cross-word | 0.0347 (377/10878) | 1.01 | ~0.00 |
| plaintext runeglish ref | ~0.0599 | ~1.74 | 1.00 |

**Plaintext reference** (proxy): 40,000 random words from `/usr/share/dict/web2`
converted to runeglish with the gematria digraph rules (TH, EO, NG, OE, IA,
EA, IO merge; K->C, Q->C, V->U, Z->S). Within-word d5 = 0.0599 (IoC 1.74),
cross-word d5 = 0.0588 — i.e. **natural runeglish has no special within-word
d5 structure**; both sit at the unigram-roughness baseline (ratio 1.02). So the
LP's within/cross d5 asymmetry (1.42) is created by the cipher, not inherited
from the plaintext, and the "full leak" reference for a same-alphabet 5-gap is
~1.74.

## Evidence against

- **The plaintext reference is a proxy.** It is English-in-runes, not the
  actual LP plaintext. If the true plaintext were much rougher or smoother the
  fraction shifts, though the qualitative "partial" result holds for any IoC in
  the 1.7-1.8 range.
- **Not a clean d5-only spike.** Within-word IoC rises d2 1.01 -> d3 1.07 ->
  d4 1.19 -> d5 1.43 rather than switching on only at d5. Samples at d3/d4 are
  moderate (179, 131 pairs) and edge effects in short words are possible, so
  this shoulder is a watch-item, not a result. If real, it argues the distance
  structure is graded rather than a hard 5-phase.
- **The harmonic decay is untestable here.** A drifting base predicts the leak
  decays across d5 -> d10 -> d15. Words are too short to check: d10-within has
  only 88 eligible pairs (2/88), d15 has zero. The echo lives almost entirely
  at d5 because words are < 10 runes.

## Predictions

- Any mechanism must have a base alphabet that **drifts within words**, not a
  single alphabet per word. Per-word monoalphabetic / single-per-word-base
  models are quantitatively excluded: they predict a full 1.74 leak at
  within-word d5, not 1.43.
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
