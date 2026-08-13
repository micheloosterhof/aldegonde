---
type: hypothesis
---
# Hypothesis: `g` Comes From the Book's Own 5×5 Magic Square

## Claim

The Liber Primus prints a **5×5 magic square with constant 3301** (master
transcription lines 179–183). The length-clocked walk needs `g` to be built from
a **5×5 grid** of 25 runes with 4 fixed points. The claim is that these are the
same grid: the square supplies the cell ordering the designer used to lay runes
into the 5×5, making `g` derivable from the book rather than from a guessed
keyword.

This matters because it is **enumerable**, which almost nothing else on the table
is. The keyword-Quagmire family was exhausted (`mixed-alphabet-vigenere.md`,
314M keys, negative) and free order-5 permutations number ~10²⁴.

## Status

**Status**: UNDECIDED — the sweep cannot test it (August 2026,
`experiments/magic_square_sweep.py`, corrected twice on review)

The sweep ran against seven g-only distance constraints (d1..d7, each testing
g^(d mod 5) on the distance-d within-word plaintext table, weighted to the LP's own
word-length histogram). At every threshold the family produces no more survivors than
chance:

| cut | a true `g` survives with prob. | family survivors | chance expects | z |
|---|---|---|---|---|
| 2.0σ | 0.72 | 0 | 2.9 ± 0.4 | −1.7 |
| 2.5σ | 0.92 | 7 | 11.2 ± 0.8 | −1.3 |
| 3.0σ | 0.98 | 24 | 32.2 ± 1.4 | −1.4 |
| 3.5σ | 1.00 | 46 | 70.7 ± 2.1 | −2.9 |

(Chance expectations from 3,000,000 random order-5 permutations — 46/177/509/1117
hits — not the 3-hit estimate two earlier versions of this file rested on.) The
family is consistently *below* chance, mildly but at every threshold, so
grid-derived permutations appear slightly less likely than random ones to land in
these bands.

**But this cannot decide the hypothesis, and that is the finding.** At 2σ the cuts
reject a true `g` 28% of the time, so 0 survivors is worth only a Bayes factor of
~3.6 against — suggestive, not a refutation. Widen to 3σ, where a true `g` is retained
with probability 0.98, and the false-positive floor rises to ~30, swamping the single
true hit. There is no threshold at which the g-only filter isolates one candidate.

One specification worry, checked and dismissed: the constraints assume full leak
(φ = 1). A uniform partial-leak alternative is **refuted** — at φ = 0.68 the dilution
floor `(1−φ)·chance` is 1.096% and the observed d1 is 0.628%, below it — so full leak
is the best-specified option available and the sweep's equations stand. What remains
is that the g-free d5 cell sits 1.4σ low under full leak, unexplained, which consumes
tolerance and makes the 72% power estimate optimistic.

The reason the sweep cannot decide is a bit count: the seven constraints are worth **16.0 bits** at 2σ
(46 of 3,000,000 random order-5 permutations pass), falling to 11.4 bits at 3.5σ,
against `g`'s 79.7. Separating one
candidate from ~30 false positives needs the 2-rune verifier, which needs the full
base schedule, which needs σ — and **σ has no construction here**. So the σ gap does
not merely block the attack; it blocks TESTING any `g` construction at all.

Note also that the family is only 2^17.5 of a 2^79.7 space, so unless the designer
used this exact construction it contains `g` with probability ~2^-62. A construction
hypothesis is therefore all-or-nothing: it is a bet on the designer's choice, not a
statistical narrowing, and it can only be settled by a verifier sharp enough to
confirm a single key.

Two earlier statuses were wrong and are retracted: "REFUTED, 1 survivor against 2.4
expected" (from plaintext tables that were not length-matched, and a control resting
on 5 events), and "no advantage shown" (which framed the result as absence of
enrichment when enrichment was never the mechanism).

## The square

```
 434  1311   312   278   966
 204   812   934   280  1071
 626   620   809   620   626
1071   280   934   812   204
 966   278   312  1311   434
```

Verified properties (`experiments/` — see Scripts):

| property | value |
|---|---|
| row sums | 3301 × 5 |
| column sums | 3301 × 5 |
| main and anti diagonal | 3301 |
| grid total | 16,505 = 5 × 3301 |
| centre cell | 809 — the only prime among the distinct values |
| symmetry | 180° rotational, `M[i][j] = M[4−i][4−j]` |
| distinct values | 13 (twelve appear twice, 809 once) |
| pandiagonal | no (broken diagonals 3301, 4035, 2567, 2567, 4035) |

3301 is itself prime. The repo's hypothesis set documents the *4×4* number grid
(the 3301±x prime table, `running-key-math-sequence.md`) but not this one; it may
be known in the wider Cicada community regardless.

## Mechanism

`g-from-5x5-grid.md` establishes the construction: 25 runes into a 5×5, each
column (or row) rotated by a fixed amount, giving cycle type 5⁵1⁴ with the 4
unplaced runes as fixed points. Its open problem is that the family is **too rich
to enumerate** — ~10⁹–10¹⁰ in-band candidates, because the fill order, the four
fixed runes and the rotations are all free.

The magic square removes the fill order, which is the largest of those freedoms.
Rank the 25 cells by value and use that as the order in which runes are laid into
the grid. What remains free is small:

| free parameter | count |
|---|---|
| which 4 runes are fixed points | C(29,4) = 23,751 |
| rotation amount | 4 |
| by column or by row | 2 |
| tie-breaking among the 12 duplicated values | ≤ 2¹² = 4,096 |

That is ~7.8 × 10⁸ candidate `g` at the pessimistic end, and ~1.9 × 10⁵ if ties
are broken canonically by reading order. For scale, the Quagmire sweep drove
3.1 × 10⁸ keys in 12.4 hours, so this is affordable at either end.

## Predictions

- A correct `g` must sit in the within-word diagonal band (~0.0063,
  `two-rune-deficit.md` and `doublet-suppression.md`). Grid-derived `g` has the
  diagonal distribution of a random order-5 permutation, so ~1-in-600 pass — a
  cheap first filter that cuts 7.8 × 10⁸ to ~10⁶.
- Survivors are scored with the 2-rune objective, which is a **validated
  verifier** (planted keys recovered exactly; `no-known-plaintext-foothold.md`).
  Use the length-independent form: `c₀ = base_w(p₀)` and `c₁ = base_w(g(p₁))` hold
  for any word, so score word-initial digraphs across all 2,928 words rather than
  the 465 short ones — necessary here because the 2-rune class is depleted.
- σ still needs a source, and this hypothesis does not supply one. Candidates
  worth trying in the same sweep: a 29-cycle from the 13 distinct values, the 4×4
  prime grid, or the Gematria ordering. **If σ must be enumerated freely the
  attack dies**, so σ's construction is the load-bearing gap.

## Evidence for

- The shape matches exactly: the cipher wants a 5×5 grid; the book prints one.
- The square is a deliberate artifact, not incidental — full magic with the
  project's own constant, and 180° symmetric.
- Cicada has form for putting key material in plain sight (the solved sections'
  keys were words from the text).

## Evidence against / open

- **13 distinct values, 11 distinct residues mod 29.** So the cells cannot map
  directly onto 25 distinct runes; the square can only supply an *ordering*, not
  the rune content. That is a real weakening — the ordering interpretation is a
  choice, not something the square forces.
- The symmetry creates 12 tied pairs, so even the ordering is not unique.
- The square sits on one page; nothing indicates it is meant as key material
  rather than as a signature or a separate puzzle.
- The 4×4 grid on another page is known to be *self-contained* design (all 16
  cells decode to primes), which is mild evidence these grids are decorative
  mathematics rather than keys.

## Scripts

- `experiments/magic_square.py` — verifies the square and reports what it can and
  cannot supply.
- `experiments/magic_square_sweep.py` — the sweep, with the random-order-5 control
  that is the load-bearing part.

## Related

- `g-from-5x5-grid.md` — the grid construction whose fill-order freedom this
  would remove.
- `mixed-alphabet-vigenere.md` — the exhausted keyword family this replaces.
- `running-key-math-sequence.md` — the documented 4×4 prime grid.
- `no-known-plaintext-foothold.md` — the 2-rune verifier used to score survivors.
- `length-clocked-walk.md` — the model being keyed.

## Verdict

Undecided, and the useful output is *why* — the g-only filter cannot test a `g`
construction at all. Widen the cuts enough to retain a true `g` (3σ keeps 98%) and
the false-positive floor reaches ~32; tighten them to 2σ and you reject the target
28% of the time. The filter is worth 16.0 bits against `g`'s 79.7, and no threshold
turns that into a single candidate.

Isolating one needs the 2-rune verifier → the base schedule → σ, which has no
construction here. **So σ's absence blocks the evaluation, not only the attack.**
Proposing σ constructions is the prerequisite for this whole route.

The family also sits consistently below chance (z = −1.7, −1.3, −1.4, −2.9 across the
four thresholds), so if anything grid-derived permutations are slightly *less* likely
than random to land in these bands — a mild effect worth noting but not a refutation.

Retracted from earlier versions: "REFUTED, 1 survivor against 2.4 expected"
(non-length-matched tables, control on 5 events) and "no advantage shown" (framed as
absence of enrichment, which was never the mechanism). The bit figure has been 4.0,
16.3, 17.0 and is now **16.0** on a 46-hit estimate; the earlier ones rested on 3-6
control events.
