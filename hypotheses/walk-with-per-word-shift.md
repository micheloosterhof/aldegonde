---
type: hypothesis
---
# Hypothesis: The Length-Clocked Walk With a Per-Word Caesar Shift of the Plaintext

## Claim

```
c_j        = base_w( g^(k_j)( p_j + s_w ) )          s_w = a_0 ± w  (mod 29)
base_{w+1} = base_w o g^((L_w - 1) mod 5) o sigma
```

`length-clocked-walk.md` with one addition: the plaintext of word w is Caesar-shifted
by s_w before the walk enciphers it. Equivalently the letter step of word w is
`shift(-s_w) o g o shift(s_w)`, a different conjugate of one g in every word. The clock
k is re-anchored at each separator and the doublet preventer advances it by one inside
the word when an emission would repeat the previous rune.

## Status

**Status**: unresolved. The sweep over keys built from one keyword each
(`experiments/walk_shift_sweep.py --run`, 1.8 × 10⁷ keys) ran on 2026-10-20; its
result is recorded below when it finishes.

## Why the shift

`within-word-relation-is-position-flat.md` (row C9): the body's within-word
coincidences carry no word-position structure, and the walk's single g on English
predicts it (every one-g model misses in 200 of 200 draws on start-end classes).
Conjugating g by a per-word shift taking all 29 values removes most of it: H 24.0 / 48.2
with s_w = w mod 29 against the body's 15.1 / 28.9 (P = 0.125 / 0.04), where a fresh g
per word reads 21.2 / 42.3. A keyword schedule with 6–8 distinct shifts is not enough
(start-end 64–78, 0 of 100).

## What survives from the walk

The base chain and its pool (rows C8, D7, D12, D13), the preventer in the stream
(D3, D9, D11), the lag-5 leak (D1, D2) and the clock bound (D10) are untouched: the
shift acts on the plaintext before any of them. Everything the walk fitted to g's
diagonals (d1w, d6w, the seam) is no longer fitted, because the shift averages g's
graph over 29 conjugates; those cells sit near chance under this model, and the body's
d6w of 0.0245 (−2.3σ against chance) is the same tension every per-word model carries.

## The verifier

`experiments/walk_shift_verifier_check.py`: the base_0-free unigram verifier of
`base_free_verifier.py`, with the shift folded into its table, assumes k_j = j and so
reads every word in which the preventer fired wrongly from the fire on. A planted key
still separates: true +1.09, best wrong +0.44 at 400 words, +0.31 at 800. (Without the
preventer one "conjugated g" scores +1.13: a conjugation by two of g's fixed points,
which is g itself.)

`experiments/walk_shift_kernel.c` is `walk_score_kernel.c` with one more table index.
It matches the Python reference to 1e-3, rejects the true key when the schedule is off
by one (+0.44 against +1.08), and runs 11,000 keys/s on three 250-word windows.

## The family swept

What one keyword builds, after `how-big-is-the-key-really.md`:

| part | construction | count |
|---|---|---|
| K | a keyed alphabet from 3301's vocabulary, four rules | 1,264 |
| g | K's first or last 25 runes as a 5×5 grid, a column or a row rotated by one, the other four runes fixed | 8 per K |
| σ | `K ∘ shift(d) ∘ K⁻¹` for d = 1..28, K as a map, K⁻¹ as a map | 30 per K |
| s_w | a_0 ± w | 58 |

1.76 × 10⁷ keys, scored on the windows (0, 250), (806, 1056), (2181, 2431) with the best
window kept. A true key reads near +1.1 nats per rune; wrong keys top out near +0.6.
Self-test: a planted key of the family ranks first at +1.078 against +0.561.

Not swept: two different keywords for K and σ (1,264² × 8 × 30 × 58, 2.8 × 10¹⁰), a
free σ, or a continuous clock. With a continuous clock the preventer's skips drift the
phase for the rest of the text and this kernel fails; `dodge_score_kernel`'s windowed
phase fitting would be needed on top of the chain.

## Result

(pending)

## Scripts

- `experiments/walk_shift_verifier_check.py`, `experiments/walk_shift_kernel.c`,
  `experiments/walk_shift_kernel.py`, `experiments/walk_shift_sweep.py`.

## Related

- `length-clocked-walk.md` — the parent model.
- `within-word-relation-is-position-flat.md` — why the shift.
- `plaintext-dial-odometer.md` — the other family that passes C9, swept in parallel.
