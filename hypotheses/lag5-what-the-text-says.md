---
type: observation
---
# Observation: What the Ciphertext Itself Says About Lag 5 — the Text-Only Picture, and the Session That Closed It

## Purpose

A consolidation, written 2026-10-26/27 after a session of text-only diagnostics on lag 5.
Everything here is a statement about the ciphertext with no model behind it; the g/σ
walk is not assumed anywhere. Each numbered conclusion names its numbers and its file.
The ledger at the end lists every experiment the session ran, positive and negative, so
none has to be re-run to find out it was done.

## The six conclusions

1. **Positions five apart inside a block are enciphered with the same substitution; across
   a boundary they are not.** Within-block d5 = 102/2,073 = 0.0492 against chance 0.0345
   (p = 0.0014 under the boundary-permutation null); cross-block d5 = 377/10,878 = 0.0347,
   exactly chance. The whole-stream excess is entirely the within-block part
   (`within-word-d5-coincidence.md`, `lag5-digraph-is-inside-the-word.md`).

2. **Positions one to four apart are not.** d2–d4 at or near chance; d1 and d6 suppressed
   and mirroring each other, d6 being distance 1 mod 5. A key running through the text
   with period 5 would give 0.061 across boundaries; observed 0.037, −11.6σ. Five
   substitutions cycle inside each block and the cycle is re-keyed at every boundary
   (`d-profile-pins-g-to-five-cycles.md`, `distance-6-has-no-power.md`).

3. **The five are general permutations of one another, not shifts.** Within-block
   differences uniform off zero at every distance (χ² 21–34 on 27 df); ratios and every
   multiplicative-subgroup coset uniform; the full 29×29 tables flat off the diagonal at
   every lag, every seam reach, and after a lag-5 match (`local-channel-is-exactly-coincidence.md`,
   `base-family-is-2-transitive.md`, this session).

4. **No alphabet set repeats detectably anywhere.** 13.5M block pairs at matched positions
   coincide at 0.0344 (chance 0.0345); adjacent blocks at 0.0373 against 0.0569 for
   two-block runs (−8σ); ≥ 949 effective alphabets; any switching trigger fires at ≥ 85% of
   boundaries (`alphabet-sets-do-not-persist-across-blocks.md`, `flat-ioc.md`).

5. **Even the relations among the five are not fixed book-wide.** With one fixed relation,
   English word structure would make the lag-k coincidence depend on where in the block
   the pair starts; it is flat at every start (C9, Bayes e¹⁰) — and the five-apart identity
   is at one rate at every start position (χ² 4.9 on 8 df, p = 0.77), every block length
   (matches English's own gradient, χ² 4.2 on 6 df), and every layout context
   (`within-word-relation-is-position-flat.md`, `within-word-d5-coincidence.md`).

6. **Equality is the only within-block statistic that carries anything.** Every pair table
   flat off the diagonal; triple patterns reduce to pairwise rates; joint matches at (1,5),
   (5,6), (5,10) total zero events (`local-channel-is-exactly-coincidence.md`).

So the text alone says: a polyalphabetic substitution; five general alphabets cycling
inside each block; re-keyed every block with no detectable reuse; a boundary-blind
doublet preventer on top. Everything beyond that is key, not text.

## The three lag-5 shapes, final standing

| shape | scope | standing |
|---|---|---|
| `x····x` single echo | within block only | real; plaintext seen through a shared substitution; reads English at every length |
| `xy···xy` adjacent pair | within block (9 of 29 events; cross-block at chance) | real; English bigram morphology through the same window (prose shows it at every b) |
| `x···yx···y` frame | 27 of 28 cross a boundary | 28 against 17.5 ± 4.3 (P 0.016), 19.1 ± 4.8 under the walk (P 0.047); absent from running prose at every boundary count (0.94×); shares none of six pre-registered features against three nulls; priced, not explained, not an attack surface |

## Session ledger, 2026-10-26/27

| experiment | question | result |
|---|---|---|
| `lag_full_table.py` (lag 5, then 1–4, 6, 7) | any relation but equality in the 29×29 table, within / cross / whole | negative: 39 off-diagonal cells, max \|z\| 2.50; lag 1 all-cells row is the known doublet diagonal |
| `seam_reach_tables.py` | the same at all 25 seam reaches | negative: max \|z\| 1.68 over the 24 non-doublet reaches |
| `lag5_match_conditional_table.py` | the pair after a lag-5 match, off the diagonal | negative: flat; the diagonal is the known d1 pairing |
| `frame_count_baseline.py` | is 17.7 the right frame baseline; do frames occur in running prose | 17.5 ± 4.3 with the echo carried, baseline confirmed; prose frames 0.94× at every boundary count — negative for a plaintext source |
| `frame_feature_nulls.py` | do the 28 frames share a feature (six pre-registered) against a layout shuffle, the walk, and real matches | negative: lowest raw P 0.13, all three nulls agree; walk gives 19.1 ± 4.8 frames, P(≥ 28) = 0.047 |
| `echo_gradient_vs_english.py` | does the echo's rise with block length match English's | positive match: χ² 4.2 on 6 df, slope difference z = +0.76; gradient retired as a lead |
| `echo_dispersion.py` | universal attenuated sharing vs a sharing subset of blocks | undecidable: arms 0.08σ apart on 806 blocks |
| `echo_by_context.py` | echo rate by closing glyph, preceding glyph, line wrap, section | negative: one rate everywhere (all p ≥ 0.10) |
| `doublet_phase_gate_by_word.py` | within-block phase census; one-phase doublet gates under a block-reset clock | phases 29/26/21/14/10% of runes; doublets at every phase at one rate (χ² 2.6 on 4 df); every gate excluded by the seam (23 vs 100.6 or 0) |
| the total suppression against phase shares | does 0.192 ± 0.021 pick a phase | no: 1/5, phase 3's pair share, phase 2's rune share and phases 0+4 all within a sigma |
| `alphabet_sharing_by_word_distance.py` | do consecutive blocks share one alphabet set, fixed k or triggered | negative: adjacent −8σ against k = 2; lag 5 across one boundary −5.7σ; persistence ≤ 15% at 2σ |
| `length_adjacency_self_null.py` (27th) | are adjacent block lengths inside a span dependent, against the body's own shuffle | negative on the body (z −0.10; 0.00 at sections; +0.01 at every mark) where intact joined order reads +5.1 (author) and +5.8 to +17.1 (prose at the body's size): the words are permuted
| `joining_before_or_after_the_shuffle.py` (28th) | were short units joined before or after the permutation | undecidable: three models fit the marginal at P 0.55–0.70, two percent apart
| `doublets_per_span.py` (28th) | is the permutation the doublet avoider | negative: doublets per span binomial (121 on 145 df vs 145 ± 30; rate flat across span length) where a best-of-42 selector clears short spans

Two discussions recorded without a new run: whether period 5 can yield the doublet
suppression without an avoider (`doublet-suppression-requires-design.md`, October 2026
section) and whether the per-block sets are related
(`alphabet-sets-do-not-persist-across-blocks.md`, closing section).

## What is left at lag 5

Nothing text-only. The within-block channel is the equality pattern and every cell of it
is measured; across blocks lag 5 is at chance in every scope. The open questions are the
key's — how the per-block sets are generated — and those are reachable only through a crib
or a structured enumeration.
