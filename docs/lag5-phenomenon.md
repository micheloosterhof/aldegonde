# A Fourth-Order Statistical Anomaly in the Unsolved Liber Primus: Paired Lag-5 Coincidences

*Research note, June 2026. Analysis code: the `experiments/` directory of
this repository. Corpus: `data/page0-58.txt` (the rtkd/iddqd master
transcription; rune content verified byte-identical to that source).*

## TL;DR

In the unsolved Liber Primus corpus (12,956 runes; the 55 unsolved pages,
excluding the solved AN END and parable pages), positions where a rune
equals the rune five places later — "lag-5 coincidences" — occur in
**pairs at separations of exactly 1 and exactly 4**, about 85% above
chance, while separations 2, 3, and 5+ are exactly at chance. Equivalently:
consecutive five-rune windows agree in their (1st, 2nd) positions or in
their (1st, 5th) positions more often than they should, and in no other
configuration. The effect replicates in both halves of the corpus, survives
removal of its largest single cluster, is verified glyph-by-glyph against
the page scans, and is invisible to every standard cryptanalytic statistic
(IoC, kappa, Friedman, bigram tables, mutual information) because it is a
fourth-order correlation with an almost-zero second-order footprint.

Honest significance: **p ≈ 0.03** under the fairest pre-registered-style
test, degrading to non-significance if you widen the search family far
enough. This is a lead, not a proof. We publish it because its *shape* is
mechanistically diagnostic, and because it is the only statistical
departure from randomness in this ciphertext other than the well-known
doublet suppression.

## 1. Definitions and data

- Corpus: concatenated runes of the 55 unsolved pages of
  `liber-primus__transcription--master` (the `page0-58` segment minus its
  two solved tail pages). N = 12,956 runes over the 29-rune Futhorc
  alphabet. Word/line/sentence/page delimiters are tracked but the
  statistics below are over the continuous rune stream.
- Define the lag-5 match indicator **M[i] = 1 iff C[i] = C[i+5]**,
  for i = 0..12,950.
- A "**d1 event**" is a pair M[i] = M[i+1] = 1: the digraph C[i..i+1]
  repeats verbatim 5 positions later (`X Y · · · X Y`).
- A "**d4 event**" is a pair M[i] = M[i+4] = 1: consecutive 5-grams agree
  in their first and last runes (`A · · · B A · · · B`).

## 2. The observation

| statistic | observed | uniform expectation |
|---|---|---|
| Σ M (mono lag-5 matches) | 479 | 446.6 (+1.5σ — unremarkable) |
| pairs at separation d=1 | **29** | 15.4 |
| pairs at separation d=2 | 15 | 15.4 |
| pairs at separation d=3 | 14 | 15.4 |
| pairs at separation d=4 | **28** | 15.4 |
| pairs at separation d=5 | 19 | 15.4 |
| separations 6–25 | all flat | 15.4 |

Key decomposition facts:

- The monographic excess (+32) is **entirely inside the paired events**:
  excluding positions that belong to d1/d4 pairs, mono matches are at
  chance (422 vs 444.6, z = −1.1).
- The full delta histogram at lag 5 is uniform (χ² = 24.2, df 28); the
  delta = 0 bin (479) literally *ties* with delta = 23 (479). Nothing
  first- or second-order is special about lag 5.
- Cluster structure: 59 two-match clusters (null ≈ 50), 8 three-match
  clusters (null ≈ 7 — at chance), and one six-match cluster. Removing
  the six-match cluster leaves d1 = 27, d4 = 26: the signal is not one
  passage.
- Split-half: d1 splits 15+14, d4 splits 13+15.
- No phase: event positions are uniform mod 5; the pattern is translation
  invariant (this excludes any fixed-grid/blocked reading).
- Spatially: corpus-wide with a concentration in transcription section 4
  (8 d1-events vs 2.2 expected, z = +3.8 alone); excluding section 4
  entirely the joint statistic still stands at z = +3.7.
- Events freely cross word boundaries, sentence boundaries (one verified
  event straddles a `:` sentence mark), and page boundaries. They show no
  correlation with word lengths, word positions, line structure, or the
  positions of the 86 doublets (see §6).

## 3. Verified examples (in Cicada's ink)

All of the following were checked glyph-by-glyph against the 2400×3600
page scans (`liber-primus__images--unsolved`); an automated forced-
alignment OCR comparison additionally verified ~83% of the whole corpus
against the images with **zero transcription errors found**.

- **Page index 50, lines 11–12** (image `51.jpg`): line 11 ends
  `... T OE M · S D`, line 12 begins `NG G L S D NG · OE · S J D ...`
  — the trigram **S-D-NG repeats at distance exactly 5**, entirely inside
  the 8-rune word `ᛋᛞᛝᚷᛚᛋᛞᛝ` spanning the line break. This single
  cluster contains 2 d1-events and 2 d4-events.
- **Page index 16, line 1** (image `16.jpg`):
  `E D A AE T O EA E EA X C EA T O D C EA N C TH` — the digraph **C-EA**
  at positions 11–12 repeats at 16–17 (d1), overlapping an EA···C /
  EA···C frame (d4).
- **Page index 16, line 4**: `... H G L OE F H G ...` — digraph **H-G**
  repeats 5 later (d1).
- **Page index 0, line 12**: `... M R NG D A M R ...` — digraph **M-R**
  repeats 5 later (d1).

The complete list of all 57 events with page/line/column coordinates is in
`hypotheses/transcription-verification.md`.

## 4. Honest statistical assessment

Three levels of test, in increasing fairness:

1. **Local**: the joint statistic T = (d1 pairs) + (d4 pairs) = 57 vs a
   doublet-suppressed-null expectation of 30.7 ± 6.5 → local z ≈ +4.1.
2. **Family-blind scan**: over all 174 cells (lag L = 2..30 × separation
   d = 1..6), the top two cells of the entire grid are (5,1) = 29 and
   (5,4) = 28 — both at lag 5. Monte Carlo for "any single lag carries two
   cells jointly ≥ (29, 28)": **p ≈ 0.033**. This is the fairest figure.
3. **Wide dragnet**: over a 399-template family of 4-point statistics
   (paired equal-lag, shared-vertex, cross-lag), the two strongest
   templates are still exactly the lag-5 components, but the global
   maximum is reached by noise in ~43% of trials. Searching wide enough
   dissolves the signal, as it dissolves any p ≈ 0.03 effect.

So: roughly a 1-in-30 chance of being a fluke under the fair test, with
two qualitative facts that pure noise does not owe us — the two top cells
of the family-blind scan landing on the *same lag*, and the excesses
landing on the structurally complementary separations 1 and 5−1 = 4.

**Null-model warning.** All quoted significances use a doublet-suppressed
null (uniform random except reproducing the corpus's 0.664% adjacent-repeat
rate). This matters enormously: against naive uniform nulls, this corpus
manufactures large fake signals — we documented +8σ (bigram IoC), −4σ
(trigram repeat counts), and +6σ (isomorph duplicates) artifacts, all of
which vanish under the corrected null. Anyone reproducing this work must
include the doublet rate in their null or they will "discover" structure
that is not there.

## 5. Why a decade of analysis missed it

The anomaly is a **four-point correlation**: it relates two *coincidence
events* at adjacent offsets, i.e. four text positions jointly. Its entire
two-point footprint is the +1.5σ mono kappa at lag 5 — as a contribution
to the full 29×29 contingency χ² at lag 5, that is ≈ 38 against a noise
floor of ±41 (df = 840). Standard tooling — IoC, kappa, Friedman, bigram
tables, mutual information, autocorrelation, spectral tests — is all
1st/2nd-order machinery and is mathematically incapable of seeing it. We
verified the corpus is flat at 1st order (distribution, positions), 2nd
order (full 29×29 tables at every lag 1–60; kappa to lag 6,400), and 3rd
order (zero triplets; trigraphic kappa flat). The complete order
hierarchy of this ciphertext is:

| order | result |
|---|---|
| 1-point | flat |
| 2-point | flat except the lag-1 diagonal (doublet suppression, 17σ) |
| 3-point | flat |
| 4-point | the lag-5 pairing — and nothing else (399-template scan) |

Precedent: Zodiac-340 was cracked starting from the same statistic family
(repeated two-symbol sequences at trial offsets, peaking at 19), the only
handle its 340 symbols offered. At LP's length, we additionally verified
the Z-340 mechanism class (homophones + transposition) is *excluded* here:
it would leak at 2nd order at this sample size, and LP does not.

## 6. What it is not (eliminated explanations)

Each item below was tested directly; scripts in `experiments/`,
write-ups in `hypotheses/`.

- **Transcription error**: events verified on the page scans; full-corpus
  OCR comparison found zero errors in the ~83% it could align (the rest
  are decorative section-start pages, where the key events were verified
  manually).
- **Period-5 polyalphabetic** (any 5 alphabets): would put mono lag-5
  kappa at ~1.7× flat; observed 1.073×.
- **Plaintext/ciphertext autokey** with feedback depth 1–8, either text
  direction, any tabula recta: preceding-rune split tests flat.
- **Fixed-width-5 blocks/seriation/bifid** (including GF(29)-native
  constructions and binary 5-bit fractionation): excluded by missing mod-5
  phase, residual IoC, or wrong pair-shape (broad d=1..4 elevation instead
  of selective {1,4}).
- **Lag-5-tapped LFSR/lagged-Fibonacci keystreams**: no pair structure
  (key reuse alone produces no ciphertext coincidences without plaintext
  coincidences — an information-theoretic point, see §7).
- **Word/line/sentence/page structure**: no correlation; no per-word or
  per-line key reset; events ignore all layout.
- **Shared grid with the doublets**: under "doublets mark group
  boundaries", close doublet-event distances should be {5,6}-expressible;
  observed consistency 4/22 = 18% vs 47% chance — *rejected* (the two
  phenomena do not co-tile).
- **Marker-rune or value-driven blocking rules**: runes adjacent to events
  and doublets are corpus-typical; capacity-accumulation scans flat.
- **Homophones + transposition** (Zodiac class): would show 2nd-order
  structure at this corpus length; LP is 2nd-order flat everywhere.

## 7. The information-theoretic constraint

The verified events are *deterministic copies*: ciphertext that exactly
reproduces ciphertext from five positions earlier. A copy carries no
information about the plaintext at the copied positions. Therefore one of
three things is true at those positions:

1. **Nulls** — the copied runes encode nothing and a decryptor skips them
   (the paired pattern is then the recognizable skip-marker);
2. **Coincidence** — the keystream repeated AND the plaintext repeated;
   rate-disfavored: producing 29 d1-events this way requires ~18% key-pair
   reuse, which would push mono lag-5 kappa to ~1.14 (observed 1.073);
3. **Back-references** — the events fire only where the plaintext itself
   repeats at lag 5 ("repeat the previous digraph/frame"), so the
   repetition is the information. Feasibility checks pass: runeglish-like
   text offers ~76 digraph and ~47 frame opportunities per corpus length
   vs 29 + 28 observed events. A simulation of this model reproduces the
   full corpus fingerprint — **but** with three fitted parameters matching
   the three free observables, so this is consistency, not confirmation.
   A fourth possibility outside the cipher proper: author-side copy-paste
   stutters during page composition. None of these four are
   distinguishable from ciphertext statistics alone.

If interpretation (3) holds, each event yields deterministic plaintext
constraints (P[i] = P[i−5] at marked positions): ~114 crib equations for
any key-search attack — conditional on an unverified assumption, and
clearly labeled as such.

## 8. Context: the other anomaly, and the number 5

The corpus's only other statistical feature is the famous doublet
suppression: 86 adjacent repeats vs 447 expected. Our measurements add:
the rate fits (1/5)·(1/29) with no free parameters (z = −0.36); the
positions are memoryless (Poisson, no positional frame in any modulus or
word/line coordinate); the minimum gap is 6 where ~3 gaps ≤ 5 were
expected (a weak hint of a ~5-position dead time, LR ≈ 18:1 for a
shifted-geometric gap law); and suppression requires the encryptor to see
its own output (no keystream-only constraint can produce it — a one-line
theorem: a doublet needs ΔP = −ΔK, and forbidding ΔK = 0 leaves the rate
at ~3.46%). The doublets and the lag-5 events do **not** share a
positional structure (§6), so the recurrence of the constant 5 in both —
acceptance probability ≈ 1/5, copy distance = 5, dead time ≈ 5 — is
either designer aesthetic or coincidence, not one mechanism.

## 9. Reproduction

Ten lines against the published transcription:

```python
AB = set("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
raw  = open("data/page0-58.txt").read()
pages = [p for p in raw.split("%") if any(c in AB for c in p)][:-2]
t = "".join(c for p in pages for c in p if c in AB)        # 12,956 runes
M = [t[i] == t[i+5] for i in range(len(t)-5)]
for d in (1, 2, 3, 4, 5):
    pairs = sum(M[i] and M[i+d] for i in range(len(M)-d))
    print(d, pairs, round((len(M)-d)/841, 1))              # 29/15/14/28/19 vs 15.4
```

Full pipeline: `experiments/lag5_digraph_chase.py` (discovery statistics
and Monte Carlo), `experiments/fourpoint_dragnet.py` (family-blind and
wide-family significance), `experiments/missed_tests.py` (order
hierarchy), `experiments/ocr_verify.py` (image verification),
`hypotheses/lag5-digraph-structure.md` (the maintained finding record,
including the re-assessment that downgraded our own earlier claims).

## 10. How to strengthen or kill this

- **Independent transcription**: re-transcribe pages 15–16, 21–22, 50 from
  the scans without reference to the master transcription and recompute.
- **Pre-registered replication**: if any additional unsolved Cicada
  ciphertext in the same system ever surfaces, the test is fixed in
  advance: pairs of lag-5 coincidences at separations 1 and 4, doublet-
  suppressed null. p < 0.01 there settles it.
- **Mechanism test**: any proposed cipher for LP must reproduce
  (a) flat orders 1–3, (b) doublet rate 0.664% with min-gap ≥ 6,
  (c) ~29 d1 + ~28 d4 lag-5 pair events with separations 2, 3, 5+ at
  chance, and (d) no co-tiling between (b) and (c). In ~35 simulated
  mechanism families, only explicit copy semantics (back-references /
  nulls / stutters) at distance 5 satisfies (c) — every classical family
  fails it, most by leaking at lower orders first.

*Corrections welcome. The repository's hypothesis files record several of
our own earlier claims that died under better nulls; we would rather this
note join them than mislead.*
