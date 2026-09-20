---
type: hypothesis
---
# Hypothesis: A Word-Delimited Quagmire with a Doublet-Dodge Rule

## Claim

Michel's proposal (September 2026). The letter step is an ordinary Quagmire schedule —
alphabets `A_k = K ∘ (add S_k)`, so the relation between adjacent positions is a pure
shift in K coordinates — and the doublet suppression is a separate rule on top: when
the emission would repeat the previous rune, advance the clock one step and re-emit.
The base advances per word, which is the word-delimited part.

## Status

**Status**: unresolved. It explains the observed doublet rate's factor of **1/5**
structurally, which nothing in this directory has done, and it identifies a class of
key every sweep here has excluded by construction. Against it: `d6w` misses for every
key tried, `d1w` misses for four keys in ten, and it inherits the decodability problem
of `doublet-dodge-walk.md`.

## The mechanism, and the one thing it forces

The dodge re-emits with `A_(k+1)` in place of `A_k`, so it **fails precisely when**

```
A_(k+1)(p) = A_k(p)   ⟺   s_(k+1) = 0
```

which does not involve the plaintext at all — it is a property of the schedule. So a
five-step schedule holding exactly one **zero offset** admits doublets at one clock
phase and forbids them at the other four:

```
P(doublet) = P(next step is zero) × P(would-be doublet)
           = 1/5 × (a shift diagonal)
```

Verified directly (`experiments/quagmire_dodge.py`): with one zero offset, 92 of 377
would-be doublets survive (24%, predicted 20%); with **no** zero offset the doublet
rate is **0.00000 over eight keys** — the dodge then never fails, and the corpus's
doublets could not exist at all.

**This is why the (1/5) matters.** `README.md` records that the observed rate "fits
(1/5)×(1/29) with no free parameters (z = −0.36)" and nothing has explained the 1/5.
Here it is forced by the schedule length. The second factor is a shift diagonal, which
is **not** parameter-free — it varies with the key, averaging about 1/29 — so the right
statement is that the mechanism forces the 1/5 and leaves the rest to the key.

## What every sweep in this project got wrong

`quagmire_runner.g_candidates` masks its candidate schedules with

```python
nz = r != 0
NZ = nz[:, None, None, None] & nz[None, :, None, None] & ... & (IDX0 != 0)
```

requiring **all five offsets to be non-zero** — because under a no-dodge model a zero
offset means two identical adjacent alphabets and a doublet rate at the plaintext
level. That is correct for the walk and exactly backwards for this model.

So the 3.1×10⁸-key enumeration (`mixed-alphabet-vigenere.md`), the ungated 7.0×10⁸
re-run and the 4.2×10⁸ priority sweep **could none of them have found this key**. The
zero-offset half of the keyword schedule space has never been searched.

## Evidence for

Scored on the held-out battery with **only the word step fitted** (chosen against the
seam); the alphabets and the schedule are drawn at random. Best key of 60 draws:

| | LP | model | tail |
|---|---|---|---|
| d1w | 0.0063 | 0.0066 | 0.700 |
| d2w–d5w, d5x | — | — | 0.13–0.83 |
| unigram IoC | 0.9999 | 0.9999 | 1.000 |
| triplets | 0 | 0 | exact |
| kappa max z | 2.908 | 2.899 | 1.000 |
| doublet position | 0.553 | 0.473 | 0.200 |
| doublet min gap | 6 | 4.88 | 0.300 |

17 of 18 free cells, one fitted. For comparison the walk fits six and leaves 13 free.

## Evidence against

**Robustness, measured over ten independently drawn keys** — the check that caught two
earlier overclaims in this session:

| misses of 18 free cells | keys |
|---|---|
| 2 | 1 |
| 3 | 3 |
| 4 | 3 |
| 5 | 3 |

Median 4. The single-key table above is the best of the draws and should not be read
as the model's performance. Two cells miss systematically:

- **`d6w` misses for all ten keys.** The corpus reads 0.0245, below chance; a Quagmire
  shift relation at distance 6 gives chance. Suppressing it needs a tuned relation the
  shift structure may not be able to supply — this is the same wall `sigma_algebraic_floor.py`
  found for arithmetic families.
- **`returns`** — the DJU-BEI repeat, which no model here produces.

**`d1w` misses for four keys in ten**, because the second factor in the rate is a
key-dependent shift diagonal rather than a constant.

**Not uniquely decodable.** Inherited from `doublet-dodge-walk.md`: an output-conditioned
skip emits exactly what the unskipped clock emits for a repeated plaintext rune, so two
plaintexts collide. This is the substantive objection to the whole dodge family.

## What to do next

1. **Search the zero-offset schedules.** This is concrete, was never done, and the
   machinery exists: drop the `nz` mask in `g_candidates`, require exactly one zero,
   and run `quagmire_ungated_sweep.py`. The band filters must also go, since this
   model's d1 is not a tuned diagonal.
2. **Find whether any Quagmire can suppress d6.** If no shift schedule reaches 0.0245,
   the family is dead regardless and the search in (1) is wasted — so do this first.
3. **Find a decodable trigger**, or accept the family is a generative account only.

## Scripts

- `experiments/quagmire_dodge.py` — the cipher, the zero-offset self-test, the
  zero-doublet control and the battery score.

## Related

- `doublet-dodge-walk.md` — the dodge rule on a general walk; this replaces its tuned
  `g` with a Quagmire schedule and gains the 1/5.
- `mixed-alphabet-vigenere.md` — the sweeps whose offset mask excludes this model.
- `stream-cipher-no-repeat.md` — where the (1/5)×(1/29) fit is recorded as having no
  free parameters and no mechanism.
- `length-clocked-walk.md` — the incumbent, which fits six cells to this one's one.

## Verdict

Unresolved and worth pursuing. It is the first mechanism here to explain the 1/5 in the
doublet rate rather than fit it, and it shows that every keyword sweep this project has
run searched only half the schedule space. Its systematic failure is `d6w`, which
should be checked analytically before any new sweep, and its standing objection is
decodability, which it shares with the whole dodge family.
