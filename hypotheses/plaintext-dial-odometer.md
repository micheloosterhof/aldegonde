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

**Status**: unresolved; **negative on the DIVINITY WITHIN crib** for every key of the
sweep's family with the clock at phase 0 on the body's first rune (see Evidence
against). The sweep over 3301's own vocabulary (`experiments/plaintext_dial_sweep.py
--nproc 6`, started 2026-10-20 01:08) was stopped at 03:46 after 12 of 240 tasks and
220 million keys (best +0.70; a true key scores near +1.0 nats per rune and wrong keys
reach +0.82 in the self-test), because `experiments/dialled_quagmire_crib_check.py`
tests the sweep's whole family through the crib at every start phase in twenty
minutes, and with the cipher alphabet in every rotation in a few hours. The sweep's
only coverage beyond that check is a crib with two preventer fires inside it, or a
wrong crib. To resume it run the same command; finished tasks are read back from
`$TMPDIR/plaintext_dial_progress.jsonl`, results go to
`experiments/plaintext_dial_candidates.jsonl`.

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

- **The opening crib refutes every key in the sweep's family, at clock phase 0.**
  `experiments/odometer_crib_check.py --run`: this family has no free base, so a key
  (K, schedule, a_0) fixes the ciphertext of DIVINITY WITHIN up to the outer shift b,
  and a wrong key reproduces the thirteen rubricated runes with one b once in 29^12.
  All 1,264 keyed alphabets × 105,980 schedules × 29 inner dials were tried with the
  clock at phase 0 on the first rune and either no preventer fire or one fire at any
  of the twelve places inside the crib, for this family and for the original
  odometer: 0 matches over 1.0 × 10^11 (key, clock) combinations, 106 minutes
  (2026-10-20). So a hit from the sweep can only be a key whose clock is not at phase
  0 on the first rune, or a key the crib check's assumptions exclude: the title is
  the first two blocks' plaintext (`crib_divinity_within.py` puts the red ink on
  exactly those 13 runes), the preventer fired at most once inside them (twice is
  about one chance in fourteen), and the inner dial advances by one at the first
  word break. The same check over the 3,000 most frequent English words as keywords
  (`--run --top 3000`, 11,016 keyed alphabets not already in the priority list, same
  four rules): 0 matches, 231 minutes. `dialled-quagmire-crib.md` takes the family
  further, with a second alphabet on the cipher side and the dials free in every
  word, and is negative too.
- **The two-rune agreement statistic leans against it.** `base_pool_floor.py` counts
  pairs of 2-rune blocks agreeing at both positions over an independent baseline; the
  body reads −13.4. On prose drawn to the body's own word-length sequence, 40 draws
  each: this family +11.9 ± 14.9 (1 of 40 at or below the body), the original odometer
  +3.4 ± 11.9 (2 of 40), 841 free bases −1.8 ± 9.9 (5 of 40), a distinct base per word
  −1.4 ± 11.2 (5 of 40). So the family is disfavoured at about 2σ, and the statistic
  has no power against a pool of 841 at this register, which weakens row C8's 2,713
  floor. The sweep decides.
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

The schedules are normalised to S_4 = 0. In the odometer that constant sits inside
K's coordinates with the inner dial and is absorbed by it. Here the dial is on the
plaintext side, so the constant is a rotation of K and the sweep covers one rotation
in 29 of each keyed alphabet. The `--rotations` run of the crib check covers all 29.

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

- `dialled-quagmire-crib.md` — the crib against this family with the dials free in
  every word and a second alphabet on the cipher side: negative for keyed alphabets.
- `quagmire-odometer.md` — the parent, disfavoured by C9.
- `within-word-relation-is-position-flat.md` — why the dial moves.
- `quagmire-dodge.md` — the preventer and the single zero offset.
