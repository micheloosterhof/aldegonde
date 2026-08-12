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

**Status**: no advantage demonstrated — but the sweep does NOT single this family out
(August 2026, `experiments/magic_square_sweep.py`, corrected on review)

The sweep ran against seven g-only distance constraints (d1..d7, each testing
g^(d mod 5) on the distance-d within-word plaintext table) at 2σ. With plaintext
tables weighted to the LP's own word-length histogram — the correct reference — the
family yields **0** survivors of 190,008, against **1.4 expected by chance** (3 of
400,000 random order-5 permutations pass; Poisson p = 0.25). So the family is not
distinguishable from random, and the sweep says nothing specific about the magic
square.

**Why: the filter admits only a TUNED g.** Optimising directly over order-5
permutations reaches all six tunable constraints to |z| ≤ 0.07, so the set is
jointly satisfiable and the model is not at fault. What it requires is a `g` designed
against the digraph tables — exactly the conclusion the repo already reached for
keyword grids. No unoptimised construction will supply one, so this outcome was
predictable for ANY construction family and is not evidence against the square in
particular.

An earlier version of this status reported "1 survivor against 2.4 expected by
chance, refuted". Those figures came from plaintext tables that were NOT
length-matched, which loosens every constraint; the control rate they rested on was
also 5–6 events, so "2.4" carried a factor-of-two error. Retracted.

Scope: canonical tie-break only; the square's twelve duplicated values admit up to
2^12 fill orders. Trying them is pointless for a different reason than stated before
— not absence of enrichment, but that no fill order produces a tuned diagonal.

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
- `experiments/magic_square_sweep.py` — the sweep that refuted it, with the
  random-order-5 control that is the load-bearing part.

## Related

- `g-from-5x5-grid.md` — the grid construction whose fill-order freedom this
  would remove.
- `mixed-alphabet-vigenere.md` — the exhausted keyword family this replaces.
- `running-key-math-sequence.md` — the documented 4×4 prime grid.
- `no-known-plaintext-foothold.md` — the 2-rune verifier used to score survivors.
- `length-clocked-walk.md` — the model being keyed.

## Verdict

No advantage shown, and it cost one sweep — which is the best thing about it. The
family gives 0 survivors of 190,008 against 1.4 expected by chance (Poisson p = 0.25),
so it carries no enrichment over random order-5 permutations.

**But it is not singled out, and that is the honest reading.** The control passes at
essentially zero as well, because the seven cuts admit only a `g` TUNED against the
digraph tables — optimisation over order-5 permutations reaches all six tunable
constraints to |z| ≤ 0.07, so the set is satisfiable and the model is not at fault.
Zero survivors was therefore predictable for ANY construction family. The general
consequence is stronger than the specific one: **no construction-based family can
work**, because the requirement is design, and design does not compress into an
enumerable key. That is the same wall keyword grids hit.

What is NOT established: that the family excludes `g`. Seven cuts at 2σ reject a true
`g` with probability ~28%, and only the canonical tie-break was tested. σ was never
given a construction here either, so that gap goes untested.

Byproduct worth more than the hypothesis: the sweep measures the seven g-only
distance constraints at **17.0 bits** (a 133,000× cut), correcting the 4.0-bit figure
in `key-local-channel-is-empty.md` by a factor of four. Still ~63 bits short on `g`
alone, with σ's 97.9 untouched.
