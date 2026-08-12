---
type: observation
---
# Observation: The Only Key-Local Channel is Empty (why no filter or gradient exists)

## Feature

Every statistical attack on this corpus has failed, and it is not luck. The cipher
has exactly one channel that is **local in the key**, that channel provably reduces
to six numbers, and everything else about the corpus is **key-global** — reachable
only by committing to the whole key at once. Key-global means no partial credit, and
no partial credit is what a delta-function landscape *is*.

## Measurement

### 1. The information is present (this is not an information-theoretic barrier)

Unicity distance with runeglish redundancy `log2(29) − H_lang` against a ~178-bit
key (`g` 79.7 bits + σ 97.9; `base_0` is free, recoverable exactly once the other
two are known):

| H_lang | redundancy | unicity distance |
|---|---|---|
| 1.5 b/rune | 3.36 | 53 runes |
| 2.0 b/rune | 2.86 | 62 runes |
| 2.5 b/rune | 2.36 | 75 runes |

The corpus is 12,956 runes — about **209× the unicity distance**. The key is
uniquely determined many times over, and a correct key verifies instantly. Calling
the key "unidentifiable" is wrong; it is identifiable and hard to identify.

### 2. The within-word channel is the isomorph pattern, and nothing else

Within a word `base_w` is ONE unknown bijection applied elementwise, and the
complete invariant of a sequence under an unknown elementwise bijection is its
**equality pattern**. So the isomorph pattern is not one within-word observable
among many — it is the only one. Anything else requires comparing across words,
where `base_w` and `base_w'` differ by the step product over the intervening word
lengths.

### 3. That pattern reduces to six scalars

`experiments/isomorph_census.py`. P(a word holds ≥1 repeat), predicted from the
measured per-distance rates alone with position pairs treated as independent:

| L | words | observed | from rates | z |
|---|---|---|---|---|
| 3 | 726 | 5.8% | 4.7% | +1.4 |
| 4 | 514 | 11.9% | 12.0% | −0.1 |
| 5 | 318 | 24.5% | 22.0% | +1.1 |
| 6 | 252 | 39.3% | 34.3% | +1.7 |
| 7 | 214 | 44.9% | 46.0% | −0.3 |
| 8 | 159 | 60.4% | 57.5% | +0.7 |

Summed z² = 6.6 on 6 df, p ≈ 0.36. Per pattern, 49 single-collision cells tested,
largest deviation L=6 `ABCDCE` at z = +2.5 against a Bonferroni threshold of 3.3 —
nothing survives. **No higher-order structure.**

### 4. Six scalars are worth ~4 bits about `g`

The doublet count pins `theta = Σ_b P(g(b), b)` from a prior spread of 0.0125 over
random order-5 permutations to a Poisson precision of 0.00079 — a 15.8× narrowing,
**4.0 bits**, against `g`'s 79.7. The seam count gives σ 2.2 bits of 97.9.

## Four extraction attempts, all consistent with the above

| attempt | script | result |
|---|---|---|
| doublet count → θ | `doublet_targeted_search.py` | 4.0 bits; the apparent +5.34σ lift was an artifact |
| isomorph score over `g` | `isomorph_g_score.py` | real gradient (true −3.71, 1 transposition −3.75, random −3.93) but hillclimbs plateau at **chance agreement, 0–3 of 29** |
| + quadgram sequence model | same | no measurable improvement — with ~20 candidates per word a wrong `g` still assembles into fluent text |
| hard rejection (impossible words) | same | median random `g` makes **zero** words impossible; 32% refuted at 3,000 words, a 1.5× cut |

The second deserves emphasis: it refutes the *letter* of "no hillclimb can work"
(`length-clocked-walk.md`), which holds for objectives needing the coupled base
schedule but not for this one. A gradient exists. It leads onto a plateau.

## Significance

```
within-word observables = the isomorph pattern        (complete invariant)
isomorph patterns       = the per-distance rates       (p ≈ 0.36)
per-distance rates      = six scalars, ~4 bits about g
⟹ every informative observable is cross-word, hence key-global
⟹ key-global means right key or noise — the delta function
```

This is a property of the cipher, not of any search. It explains every failure
without appealing to bad luck, and it predicts that further objective-engineering
will fail.

## Consequences

Exactly two routes remain:

1. **Shrink the key space until it is enumerable.** `magic-square-grid-key.md` is
   the only live candidate (1.9e5–7.8e8, affordable), and σ has no construction
   there — that gap decides it.
2. **Import external information.** About **63 contiguous crib runes, roughly 15
   consecutive words**, closes the gap. DIVINITY WITHIN is 13 runes and ~14 bits,
   consistent with its recorded 16,000× reduction and about a fifth of the way.
   `experiments/d5_crib_targets.py` supplies key-free plaintext constraints toward
   this: since d5 reads plaintext equality directly, 8 words carrying XY···XY are
   pruned to 4–152 dictionary candidates (word 1987 to **4**, word 2751 to **14**).
   Those are scattered rather than contiguous, so each carries its own unknown base
   and the crib is weaker per rune — but with `base_0` eliminated they still give
   injectivity constraints on `(g, σ)` alone.

## Falsifiable

The argument assumes `base_w` changes at every word and is otherwise free. If it
does not change per word, within-word invariants extend across words and the
isomorph channel stops being vacuous. `two-rune-depth-no-base-reuse.md` puts the
base at ≥~300 effective values, which is strong but not the same claim. A statistic
that is local in the key and NOT of the isomorph family would also break it; none is
known, and §2 argues none exists.

## Scripts

- `experiments/information_budget.py` — the budget, unicity distance, crib sizing.
- `experiments/isomorph_census.py` — the pattern-to-rates reduction.
- `experiments/isomorph_g_score.py` — the gradient that plateaus (worked negative).

## Related

- `length-clocked-walk.md` — the model this characterises.
- `no-known-plaintext-foothold.md` — the delta-function landscape, now explained.
- `magic-square-grid-key.md` — route 1.
- `two-rune-deficit.md` — where the plaintext's own structure is anomalous.
