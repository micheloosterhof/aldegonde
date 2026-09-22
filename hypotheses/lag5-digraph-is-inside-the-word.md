---
type: observation
---
# Observation: The Lag-5 Digraph Excess Is a Within-Word Effect

## Question

`lag5-digraph-structure.md` measures 29 repeated digraphs at distance 5 against 15.4
expected on the raw rune stream, and correctly declines to call it significant: a max over
lags 2–150 reaches +3.47 in 38% of null runs, and lag 129 scores +3.78 in the real text.

That measurement ignores word boundaries. The base changes at every block edge, so a
digraph straddling one is written under two alphabets and its coincidence falls to chance.
Restricting to pairs inside a single block is where the base cancels.

`experiments/ngram_kappa_inside_a_word.py`

## Lag 5 is pre-specified, not a scan maximum

This is the reason the result is not another look-elsewhere artifact. g has order 5, so
inside a block `c_i = c_(i+5)` holds exactly when `p_i = p_(i+5)`. Every other lag reads
`p_i = g^(k mod 5)(p_(i+k))`, a g-twisted relation with no reason to be elevated. The cell
was named by the model before the measurement.

## The model passes a check it was not built for

Monograph kappa inside a block, z against chance:

| lag | 1 | 2 | 3 | 4 | **5** | 6 | 7 |
|---|---|---|---|---|---|---|---|
| the body | −15.24 | +0.13 | +0.97 | +1.83 | **+3.69** | −1.87 | +0.95 |
| English, runeglish, joined | −10.88 | +10.95 | +82.15 | +64.25 | +57.07 | +60.89 | +33.59 |

English repeats letters within a word at every distance. The body repeats them at distance
five and nowhere else. Lag 1 is negative in both — the body's doublet preventer and
English's own dislike of doubled letters.

## The result

| n | lag | inside hits | pairs | expected | z |
|---|---|---|---|---|---|
| 1 | 5 | 104 | 2,105 | 72.59 | +3.69 |
| 2 | 5 | **9** | 1,290 | **1.53** | **+6.03** |
| 3 | 5 | 1 | 731 | 0.03 | +5.60 |

### The sharper form, which needs no rate estimate

Of the hits already counted on the raw stream, how many are inside a block? Inside
positions are a known fraction of all positions, so this is a binomial test on the hits
themselves.

| | inside / total | chance puts | P |
|---|---|---|---|
| monograph, lag 5 | 104 / 479 | 77.9 | **0.0011** |
| digraph, lag 5 | 9 / 29 | 2.9 | **0.0015** |
| trigraph, lag 5 | 1 / 1 | 0.1 | 0.0565 |

**The digraph anomaly of `lag5-digraph-structure.md` is a within-word effect.** That file's
global-significance verdict was correct for the statistic it measured; the statistic was
diluted by the 90% of digraph positions that straddle a base change.

## The null that matters

A digraph coincidence needs two monograph coincidences, and the monograph rate inside a
block at lag 5 is already 0.0494 against chance 0.0345. The expectation to beat is that
rate squared, not 1/29²:

| | hits | expected if the monographs were independent | ratio | z |
|---|---|---|---|---|
| the body | 9 | 3.15 | 2.86 | **+3.30** |
| English | 724 | 431.84 | 1.68 | +14.06 |

Both are super-multiplicative — a repeated digraph is likelier than two independent
repeated letters, which is what language does. The body's ratio is higher than English's
and rests on nine hits, so the two are **not** distinguishable.

## What it rests on

Nine hits in **eight distinct blocks**; one block carries a repeated trigraph and so
contributes two overlapping digraph hits. Dropping any single event leaves 8 against 3.15,
z = +2.73. The effect is not one word.

    ᛝᛈᚩᚪᚣᛝᛈ  ᚹᛡᛠᚱᚫᚹᛡ  ᚣᛈᛟᚦᛋᚣᛈ  ᚾᚪᛠᚩᚪᚾᚪ
    ᚪᛝᛈᚦᛈᚪᛝ  ᛈᛋᚦᛁᚳᛈᛋ  ᛋᛞᛝᚷᛚᛋᛞᛝ  ᛖᛋᛇᚦᚦᛖᛋ

## What it does not show

- **Nothing about the trigraph.** One hit against an expectation of 0.03 is a one-arm
  tail. The trigraph cell expects one hit per thirty runs of the whole book and cannot be
  turned into a rate at this corpus size.
- **Nothing about the d=4 pairing.** `lag5-digraph-structure.md` gets its global
  significance from the joint statistic T(5) = pairs at separation 1 plus pairs at
  separation 4. Only the separation-1 half is tested here.
- **No key.** These are plaintext coincidences read through a channel that cancels the
  base. They constrain the plaintext, not g or σ.

## How to falsify

- Show the eight blocks are a parsing artifact — for instance that the page-break merge
  used here (32 blocks longer than `body_parse`) creates them. It does not: every one of
  the eight is a single block under either convention, since all are 7–11 runes.
- Show the within-block restriction is what inflates the ratio, by planting a stream with
  the observed monograph rate and no digraph structure and recovering ratio 1.0.
- Find an English register where the digraph-to-monograph² ratio reaches 2.86, which would
  make the body's nine hits unremarkable rather than merely unresolved.
