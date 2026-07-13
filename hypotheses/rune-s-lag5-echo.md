# Characterization: The Lag-5 Echo is Carried by the Rune S

## Claim

The within-word distance-5 coincidence excess
(`within-word-d5-coincidence.md`) is **not rune-agnostic**. One rune, **S**
(ᛋ, Sigel), echoes at distance 5 inside words far more than any other: 11
observed against a null of 1.75 (Poisson p = 2.4e-6, Bonferroni-clean across
all 29 runes). The effect is **specific to distance 5** (d = 1..4, 6 are
normal or suppressed) and **within-word only** (cross-word S at d=5 is at
chance). S alone accounts for ~22% of the entire within-word d=5 excess, about
twice the next rune's contribution.

## Status

**Status**: plausible (verified anomaly; mechanism unknown)

Found by inspection of the matched runes, then confirmed against a
distance-specific, position-controlled null. Robust: Bonferroni-clean, spread
over 11 distinct words in 7 of 10 sections, and confined to exactly d=5. The
lens (within-word, distance 5, echoed-rune identity) was chosen after seeing
the lag-5 excess, so read the significance as strong-but-directed.

## What was measured

Clean corpus: sections 0-9 of `data/page0-58.txt`, tokenized with `- . & %`
as boundaries (as in `within_word_d5.py`). The null holds each word's exact
rune multiset and length fixed and randomizes only the arrangement: for a word
of length L holding k copies of rune r, the expected r-r pairs at distance d is
`(L-d)*k*(k-1)/(L*(L-1))` — exact mean, Poisson upper tail for the p-value,
matched to two decimals by a within-word shuffle (0 of 4,000 shuffles reached
11 S-pairs).

**S echo by distance (within word):**

| d | obs | null | Poisson p |
|---|-----|------|-----------|
| 1 | 2 | 6.73 | — (S doublets suppressed, like all doublets) |
| 2 | 4 | 5.23 | 0.77 |
| 3 | 2 | 3.74 | 0.89 |
| 4 | 3 | 2.58 | 0.48 |
| **5** | **11** | **1.75** | **2.4e-6** |
| 6 | 0 | 1.22 | — |
| 7 | 1 | 0.82 | 0.56 |

Only d=5 fires. This is not "S clumps inside words"; it is "S sits exactly 5
apart."

**Every rune at d=5** (Bonferroni threshold p < 0.05/29 = 0.0017):

| rune | obs | null | Poisson p |
|------|-----|------|-----------|
| **S** | 11 | 1.75 | **2.4e-6** (clears Bonferroni) |
| P | 7 | 2.75 | 0.022 |
| A | 7 | 2.52 | 0.015 |
| N | 6 | 2.27 | 0.028 |
| NG | 6 | 2.14 | 0.022 |
| E | 5 | 1.75 | 0.033 |

The leaders (S, P, A, N, NG, E) are common runeglish letters — a broad
excess consistent with common-morpheme repeats — but S is the only one that
survives correction, and by a wide margin.

**Within vs cross-word (d=5):** within-word 11 (null 1.75); cross-word 10 of
10,878 pairs (chance 12.2) — at chance. The S echo is strictly a within-word
phenomenon, like the general d=5 excess it dominates.

**Share of the excess.** Against the within-word-arrangement null the total
d=5 excess is 102 − 60.6 = 41.4 pairs; S contributes 11 − 1.75 = 9.25, i.e.
~22%. (Against the looser word-length-shuffle null used for the headline
"102 vs 76" in `within-word-d5-coincidence.md`, S's share reads ~35%; 22% is
the internally consistent figure, same null for numerator and denominator.)

## The words

Eleven distinct words, one S-pair each, across sections 0,1,2,4,7,8,9:

```
ᛋᛟᚱᚢᚹᛋᛚᛡ      S·OE·R·U·W·S·L·IA          S at 0,5
ᛋᚣᛗᛞᚣᛋ        S·Y·M·D·Y·S                S·Y·_·_·Y·S (near-palindrome)
ᛋᛞᛝᚷᛚᛋᛞᛝ      S·D·NG·G·L·S·D·NG          SDNG···SDNG (trigram frame)
ᛖᛋᛇᚦᚦᛖᛋ        E·S·EO·TH·TH·E·S           ES···ES (frame)
ᚢᛈᛋᚦᛁᚳᛈᛋᛁᚹ    U·P·S·TH·I·C·P·S·I·W       PS···PS (frame)
ᛋᚩᛠᚳᛖᛋ        S·O·EA·C·E·S               S···S
ᚪᛋᛡᚦᛋᚦᛋᚠᛗᚷᛞᛠ  A·S·IA·TH·S·TH·S·F·M·G·D·EA  S at 1,4,6
ᚹᛁᛡᛋᛈᛚᚦᚪᛋᛄ    W·I·IA·S·P·L·TH·A·S·J      S at 3,8
ᚩᛋᛏᛗᚱᚣᛋᛉ      O·S·T·M·R·Y·S·X            S at 1,6
ᛝᚾᚳᛋᚾᛞᛇᚾᛋᛁᚳᛡ  NG·N·C·S·N·D·EO·N·S·I·C·IA  S at 3,8
ᚠᚢᛉᛋᛉᛁᚦᚫᛋᛗ    F·U·X·S·X·I·TH·AE·S·M      S at 3,8
```

S anchors most of the named `XY···XY` frame words (SDNG, ES, PS all involve
S).

## Interpretation

This cuts against the clean "plaintext morphology leaking through a random
per-word key" reading of the lag-5 echo. A random per-word key randomizes the
ciphertext value of each echoed position, so the echoed *rune* should be
uniform. It is not — one specific rune dominates. Candidate explanations, none
yet tested:

- **A non-randomizing component at these positions** — the cipher does not
  fully scramble the value where the d=5 echo occurs, so a specific plaintext
  or key rune survives as S.
- **S as a ciphertext-structural rune** — a marker or separator role (compare
  the EA-marker line in `doublet-marker-rune-ea.md`), here appearing as a
  distance-5 pair.
- **A specific plaintext morpheme** repeating at distance 5 whose enciphered
  value is consistently S — again requiring the cipher to be locally
  value-preserving.

Whatever the cause, the lag-5 echo is more specific than "runes repeat at 5":
it is disproportionately "S repeats at 5, inside a word."

## Predictions

- Any correct decryption should place, at the 11 S-pair sites, either a shared
  plaintext rune or a shared key relation that resolves to S — and should
  explain why S rather than a random rune.
- If S has a structural (marker) role, it should show other positional
  regularities (word position, spacing) beyond the d=5 pairing.
- The S-at-d5 excess should reproduce in an independent transcription and in
  any newly transcribed clean text (out-of-sample check).

## Scripts

- `experiments/rune_s_lag5.py` — reproduces every number here: S echo by
  distance, the full per-rune table at d=5, within-vs-cross-word split, the
  share of the excess, and the word list.
- `experiments/within_word_d5.py` — the parent within-word d=5 anomaly.

## Related

- `within-word-d5-coincidence.md` — the excess this refines; the excess is
  S-dominated, not rune-agnostic.
- `lag5-digraph-structure.md`, `lag5-back-reference.md`,
  `docs/lag5-phenomenon.md` — the lag-5 structure and the copy-event reading;
  the S-dominance is a new constraint on any proposed copy mechanism.
- `doublet-marker-rune-ea.md` — the precedent for a single rune carrying a
  structural role.

## Verdict

Verified anomaly, mechanism unknown. The within-word lag-5 coincidence is
disproportionately carried by the rune S (11 vs 1.75, p = 2.4e-6,
Bonferroni-clean), specific to distance 5 and to within-word pairs, spread
across 11 words and 7 sections. This is the first rune-level structure found
in the echo, and it argues that the lag-5 mechanism is not a value-randomizing
per-word key. The open question is why S: a non-randomizing cipher component,
a structural role for Sigel, or a specific plaintext morpheme that survives
encryption.
