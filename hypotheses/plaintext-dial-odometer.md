---
type: hypothesis
---
# Hypothesis: The Odometer Quagmire With Its Inner Dial on the Plaintext Side

## Claim

```
c = ( K[ (pos_K((p + a_w) mod 29) + S_k) mod 29 ] + b_w ) mod 29
```

`quagmire-odometer.md` with one change: the inner dial `a_w` shifts the plaintext rune
before it is looked up in the keyed alphabet `K`, instead of shifting inside `K`'s
coordinates. Everything else is the odometer: `S` the running sums of a five-step
schedule with exactly one zero offset, the clock `k` running on through word breaks,
the doublet preventer advancing the clock on a would-be repeat, `a` advancing every
word and `b` only when `a` wraps.

## Status

**Status**: unresolved; the sweep over 3301's own vocabulary is running (started
2026-10-20, `experiments/plaintext_dial_sweep.py --nproc 6`, about 35 hours; progress
in `$TMPDIR/plaintext_dial_progress.jsonl`, resumable; results to
`experiments/plaintext_dial_candidates.jsonl`). A true key scores near +1.0 nats per
rune; wrong keys score below +0.82 in the self-test.

## Why the dial moves

Inside a word the base cancels, so a lag-k coincidence reads a relation on the
plaintext, `p_i = R(p_(i+k))`. In the odometer the inner dial sits inside `K`'s
coordinates and cancels from that relation, which is then one of five shifts conjugated
by `K`, the same for every word. `within-word-relation-is-position-flat.md` (row C9)
finds that the body's within-word coincidences carry no word-position structure, and a
relation fixed across words passes English word structure through: the odometer reads
H 70 ± 28 on start-end classes against the body's 29, 0 of 100 draws.

With the dial on the plaintext side the relation is conjugated by `shift(a_w)`, a
different shift in every word, and the clock phase at the word start adds a second
per-word variation. The family then reads H 21.3 ± 6.2 on start classes (body 15.1,
P = 0.13) and 45.1 ± 10.8 on start-end (body 28.9, P = 0.05): it fits.

## Evidence for

The fingerprint battery, nothing fitted, 40 prose corpora
(`experiments/within_word_relation_by_position.py` for H; the battery run is recorded
in the commit that adds this file):

| cell | LP | model | tail |
|---|---|---|---|
| d1w | 0.0063 | 0.0070 | 0.45 |
| seam | 0.0079 | 0.0067 | 0.45 |
| d5w | 0.0492 | 0.0584 | 0.20 |
| d5x | 0.0347 | 0.0362 | 0.50 |
| ioc, entropy, triplets, bigram_chi2, kappa | — | — | 0.55–1.00 |
| identical | 17 | 12.1 | 0.20 |
| returns | 1 | 0.23 | 0.10 |
| doublet_pos, doublet_gap_min, long, clock | — | — | 0.20–0.85 |
| **d6w** | **0.0245** | **0.0372** | **0.000** |

18 of 19 free cells land. The miss is the one every per-word-relation model shares:
the body's distance-6 rate is 31 coincidences on 1,267 pairs, and against its own
binomial error the gap is 2.3σ, not the p = 0.000 the battery prints
(`distance-6-has-no-power.md`).

## Evidence against

- **The state pool is 841.** `base_pool_floor.py` reads the body's 2-rune blocks as
  consistent with a base distinct for every block: excess −13.4 ± 10.6 agreeing pairs
  against +14.5 predicted for a pool of 841, 2.6σ. The `identical` cell above passes
  because whole-word identity needs the same plaintext word as well, and the register
  carries the LP's own word lengths. The two statistics disagree on this family by
  about 2.6σ; the sweep decides.
- The doublet preventer's clock skips put the body's d5 shortfall at q ≈ 0.034, inside
  the allowed [0.003, 0.262] (`d5-bounds-the-clock-perturbation.md`).

## The sweep

Family: 1,264 keyed alphabets from 3301's vocabulary (`priority_vocabulary`, four
construction rules each) × 105,980 one-zero schedules × 29 inner dials, 3.9 × 10⁹
keys. The outer dial is a uniform ciphertext shift that the scorer's free bijection
absorbs. The scorer is `dodge_score_kernel`, which fits each 18-rune window's clock
phase so the preventer's skips cost nothing; only the log table changed:

```
odometer   tab[k][a][z] = log f( K[ pos_K(z) - a - S_k ] )
here       tab[k][a][z] = log f( K[ pos_K(z) - S_k ] - a )
```

Self-test (`--selftest`): the table inverts a planted ciphertext at every rune (61
dodges in 1,802 runes); the planted schedule is in the generator; the planted key
ranks 1 of 2,001 at z = +28 with its dial recovered; 5,026 keys/s/core.

To stop: `pkill -f plaintext_dial_sweep`. To resume: run the same command; finished
tasks are read back from the progress file.

## Predictions

- A key in the family scores above +0.9 on 400 words and decrypts the body to
  runeglish; wrong keys top out near +0.8.
- If the sweep is negative, the family survives only with a keyword outside 3301's
  vocabulary or a schedule with two zero offsets, and the 841-state pool stays 2.6σ
  against it.

## Scripts

- `experiments/plaintext_dial_sweep.py` — the cipher, the table, the self-test, the
  sweep.
- `experiments/within_word_relation_by_position.py` — the position test.

## Related

- `quagmire-odometer.md` — the parent, disfavoured by C9.
- `within-word-relation-is-position-flat.md` — why the dial moves.
- `quagmire-dodge.md` — the preventer and the single zero offset.
