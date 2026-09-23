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

## Adversarial audit: five attacks on the channel itself

`experiments/five_attacks_on_the_d5_channel.py`

The d5 measurements built the period-5 model, so confirming the model with d5 is circular.
Five attempts to break the within-word lag-5 result:

| # | attack | outcome |
|---|---|---|
| 1 | different lags draw from different word populations | **fails** — fixing the minimum word length at 6, 7, 8, 9 or 10 leaves lag 5 at +3.6 to +3.9 and its neighbours flat |
| 2 | look-elsewhere across lags | **fails** — max over lags 2–8 is +3.69 against a surrogate max of +0.29 ± 0.67 |
| 3 | held-out halves | **fails** — +3.18 and +2.03 |
| 4 | a single position inside the word | **fails** — the excess is at every start position 0–4 |
| 5 | the baseline | **lands, then falls over** — see below |

### The attack that landed

Shuffling letters **inside each word** preserves word length and letter multiset and is the
obvious null. It breaks the result: lags 2, 3 and 4 read +5.30, +4.40, +4.26 against lag
5's +5.62, so "only lag 5 is special" collapses.

**That null is contaminated by the cipher.** It preserves each word's letter multiset, and
the doublet preventer has already stripped repeated letters out of those multisets —
adjacent repeats are suppressed 82%. The null therefore sits about 24% below chance at
every lag and manufactures an excess wherever it is used.

A **global** shuffle — all body runes permuted, word lengths kept — preserves the
ciphertext letter frequencies and destroys everything else, including the preventer's mark
on the multisets. It lands on 1/29 (250.6 against 250.0 at lag 2) and only lag 5 survives,
at +3.7.

**Standing rule: a within-word shuffle is the wrong null for this corpus**, because the
preventer has already edited the thing it preserves.

### The control that decides nothing

The solved front matter uses a different cipher, so it should show no lag-5 excess. It
reads +1.70, with lag 7 higher at +2.37 — but on 694 words against 2,895 the body's own
effect size would only produce about +1.5 there. Underpowered, and recorded so it is not
mistaken for a passed control.

### What survives, narrowly

The excess is real at +3.7 on 104 hits against 72.6. It pins that **positions i and i+5
inside a word share an alphabet**. It does **not** pin that g is a permutation of order 5:
a five-long keystream restarting at each word predicts exactly the same thing, as does any
scheme giving those two positions the same alphabet. The model is one member of that
family, and this channel cannot choose between them.

## How strongly is the shared alphabet actually held?

`experiments/how_proven_is_the_shared_alphabet.py`

**Likely, not proven.** The monograph cell is 104 within-word lag-5 coincidences against
72.8 expected.

*(An earlier version of this section said the digraph cell was not extra evidence, because
its hits are a subset of those 104. That was wrong — see "The digraph is separate
evidence" below. Michel caught it.)*

A σ is the wrong summary when both alternatives are specified, and here they are.

| model | rate | expects | LR vs H0 | observed sits |
|---|---|---|---|---|
| H1 raw (English, length-matched) | 0.0574 | 120.9 | 123 : 1 | −1.59σ |
| H1 drift-adjusted | 0.0545 | 114.7 | **265 : 1** | −1.03σ |
| H0 no sharing (ciphertext chance) | 0.0346 | 72.8 | — | +3.72σ |
| **observed** | **0.0494** | **104** | | |

The drift adjustment is the preventer: a distance-five relation breaks whenever the
preventer fires in between, attenuating the excess by (1 − q)⁵ = 0.872 at the measured
q = 0.0271.

**A couple of hundred to one.** Strong, the right way round — the observed value sits one
σ below the shared-alphabet prediction and nearly four above the no-sharing one — and not
proof.

### What the number is sensitive to

H1's rate comes from English at matched word lengths over three registers, and registers
differ. Nothing pins that rate to better than about ten percent, so read 265 as "a couple
of hundred", not as a figure.

### Why it cannot be pushed much further here

| target | needs |
|---|---|
| 1,000 : 1 | about 1.2× these 2,105 pairs |
| 10,000 : 1 | about 1.7× |

The pairs come from the 815 body words of six runes or more, and the book has no more. So
within this corpus the claim tops out in the low thousands to one at best.

Getting past that needs either material outside the body, or a consequence of the shared
alphabet that is **not** the coincidence rate. The local-channel theorem says equality is
the only invariant visible at every order
(`key-local-channel-is-empty.md`), which is why there is one number here and not a
battery — and that is a structural ceiling, not a gap in effort.

## The digraph is separate evidence

`experiments/how_proven_is_the_shared_alphabet.py`

The digraph hits are a subset of the monograph hits, but the digraph statistic counts how
those hits are **arranged**, and arrangement is close to independent of count. Holding the
monograph total fixed at 104 and scattering them at random over the 2,105 slots:

| | value |
|---|---|
| adjacent-pair digraph hits under the scatter null | 3.11 ± 1.69 |
| observed | **9** |
| P | **0.0027** |

| model | expects | |
|---|---|---|
| H0 no shared alphabet → coincidences are chance, so no clustering | 3.11 | |
| H1 shared alphabet → English's clustering of 1.68× | 5.22 | |
| observed 9 | | **LR = 12.9 : 1** |

**Combined with the monograph cell: about 3,400 to 1, not 265.**

### The preventer does not cost the digraph much

A monograph distance-five relation needs no extra clock step across five positions,
(1−q)⁵ = 0.872. The digraph needs none across six, (1−q)⁶ = 0.848. The extra cost is
(1−q) = 0.973 — under 3%, not the large reduction one might expect.

Conditionally the preventer slightly **raises** the digraph rate: given c_i = c_{i+5} = X,
it forbids both c_{i+1} = X and c_{i+6} = X, so each draws from 28 letters rather than 29.
That is a 3.6% increase, moving the null from 3.11 to 3.22.

### The tension worth watching

The body clusters at 2.90× where English clusters at 1.68×, putting the observation
**+2.2σ above H1** rather than below it — the opposite sign to the monograph cell's −1.03σ.
On nine hits that is not a result. If it survives more material it is a problem for the
plaintext-is-ordinary-English arm, not for the shared alphabet.


## Which period-5 cipher does this pin?

`experiments/which_period_five_cipher.py`

**It does not choose between them, and it kills one variant outright.**

### Every period-5 scheme makes the same prediction here

If positions i and i+5 share an alphabet, `c_i = c_{i+5}` exactly when `p_i = p_{i+5}`, and
likewise for digraphs and trigraphs. A Vigenère with a five-long key, a Quagmire with a
five-long key, and the length-clocked walk with g of order 5 are **observationally
identical** on this channel. It sees that the alphabets repeat with period five. It cannot
see how the five alphabets relate to one another — shifts of a common alphabet in the first
two, powers of one permutation in the third.

### Triplets: yes, and they are present

| step | H0 | H1 | seen | LR |
|---|---|---|---|---|
| 1 monograph count | 72.6 | 114.7 | 104 | 265 : 1 |
| 2 digraph \| monograph count | 3.15 | 5.28 | 9 | 12.4 : 1 |
| 3 trigraph \| digraph count | 0.036 | 1.32 | 1 | 10.3 : 1 |
| **chain** | | | | **33,850 : 1** |
| without step 3 | | | | 3,295 : 1 |

Conditioning each order on the one below makes the steps independent, so they multiply;
the unconditional cells do not, because the hits nest.

**Step 3 swings on one word.** Had the trigraph count been zero it would read 0.28 : 1
*against*. The defensible figure is a few thousand to one with a hint of more.

*(This also corrects the earlier note that the trigraph cell "cannot be read at all". That
was priced against H0 only. With both arms specified — English repeats a trigraph at
distance 5 inside a word at 28.6× chance — one hit against 0.036 expected is worth about
ten to one.)*

### What is excluded: a key that does not restart at each word

A globally periodic key of period five repeats the alphabet every five runes regardless of
where words begin, so it makes the same prediction **across** word boundaries. Then the
whole-stream lag-5 coincidence would equal the plaintext rate:

| | |
|---|---|
| whole-stream lag-5 observed | 479 of 12,951 = 0.0370 |
| a globally periodic key predicts | 0.0614 → 796 hits |
| no shared alphabet predicts | 0.0345 → 447 hits |

**−11.6σ from the globally periodic prediction.** A plain period-5 Vigenère or Quagmire
over the running text is dead. `kappa-spectrum.md` reached the same verdict from the kappa
spectrum; this is it from the plaintext side, with the alternative quantified rather than
only the null.

### The shape is fixed, the mechanism is not

**Five alphabets cycling inside each word, re-based at every word boundary.** A Quagmire
whose key restarts per word fits exactly, and so does the walk. Separating them needs the
relationship between the five alphabets, which equality coincidence cannot see — that is
the local-channel theorem, not a gap in effort.

## What the five alphabets are: two answers and one impossibility

`experiments/what_the_five_alphabets_are.py`

### 1. Are they one alphabet shifted five ways? Undecidable

Inside a word the only visible thing is whether two runes are equal, and that depends on
the five alphabets only through the composite τ_k = A_r⁻¹A_{r+k}. The coincidence rate at
lag d is the diagonal mass of the plaintext distance-d bigram matrix under τ_{d mod 5}.

| lag | body rate | shift ensemble | arbitrary permutations |
|---|---|---|---|
| 2 | 0.0348 | 0.0221–0.0546, sd 0.0069 | 0.0344, sd 0.0085 |
| 3 | 0.0371 | 0.0245–0.0595, sd 0.0087 | 0.0347, sd 0.0073 |
| 4 | 0.0405 | 0.0216–0.0560, sd 0.0085 | 0.0345, sd 0.0068 |
| 6 | 0.0248 | 0.0231–0.0660, sd 0.0097 | 0.0345, sd 0.0077 |
| 7 | 0.0410 | 0.0205–0.0569, sd 0.0084 | 0.0346, sd 0.0077 |

Same centre, same spread, same range. **No observed value is evidence either way**, and
this is not a sample-size problem: the base family is 27-transitive, so the equality
pattern is the only base-invariant statistic of any tuple up to 27 runes, and the longest
body word is 14. There is nothing else to reach for.

### 2. Is the per-word re-basing a shift? No

Already in the repo (`affine_triple_invariant.py`), not re-derived. For an affine base the
ratio (c_c − c_a)/(c_b − c_a) cancels multiplier and offset, surviving the re-basing.

| | χ² on 28 df |
|---|---|
| the body, 3,357 within-word triples | **89.7** |
| planted affine bases | 620–1,252, median 848 |
| planted general bases | 31.5–141.2, median **82.2** |

**The per-word base is a general permutation — not a shift, not affine.** That kills the
AGL(1,29) family, the one that would have collapsed the base key space from 29! to 812.

It is also why question 1 is closed rather than merely hard: a shift-structured re-basing
would leave additive traces that expose the five alphabets, and a general one does not.

### 3. A continuous key with the words shuffled afterwards? Excluded

The model — one period-5 key running through the plaintext, words transposed afterwards,
preventer on top — explains the within-word period 5 and explains why nothing survives
across word boundaries, since the shuffle scrambles each word's entry phase. It is a
genuinely good fit to everything measured so far.

But it makes a prediction the general model does not: there is **no per-word base at all**,
only five entry phases. Two words sharing a phase use identical alphabets and coincide at
matched positions at the plaintext rate.

| | |
|---|---|
| English word-aligned coincidence (the same-phase rate) | 0.0794 |
| a five-phase model predicts 0.2 × 0.0794 + 0.8 × 0.0345 | 0.0435 |
| the body, 13.5M word pairs at matched positions | **0.0344** |
| chance | 0.0345 |

**Observed 464,370 against 586,927 predicted, z = −164.** Word-aligned coincidence does
not move off chance at all, so there is no small set of shared alphabets. Whatever re-bases
each word takes many more than five values — the same conclusion `alphabet_count_bound.py`
reaches from the other direction.
