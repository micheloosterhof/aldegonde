---
type: observation
---
# Observation: The Two Number Grids Are 176 Uniform Bytes

## What was sitting unread

Master chunks 65 and 66 — image pages 50 and 51 — carry no runes. They carry grids of
eight columns, thirteen rows and nine rows, of two-character tokens: `2M`, `0w`, `15`,
`4B`. `isdigit-counts-circled-marks` records them as "untranscribed base-60 data".
Nothing in this directory had decoded them.

## The decoding, and how the reading is pinned

The second character runs over 60 symbols — `0`–`9`, then `A`–`Z`, then `a`–`x` — and
the first over `0`–`4`. So each token is a two-digit base-60 numeral, which admits values
0 to 299.

The leading digit settles which range is actually in use:

| leading digit | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| observed | 45 | 34 | 46 | 39 | **12** |
| predicted if 0–255 | 41.2 | 41.2 | 41.2 | 41.2 | **11.0** |
| predicted if 0–299 | 35.2 | 35.2 | 35.2 | 35.2 | **35.2** |

Only values 240–255 carry a leading 4, which is 16 of 256. Twelve observed against 11
predicted, versus 35 for the wider range. **The grids hold 176 bytes**: 104 in chunk 65,
72 in chunk 66. Observed range 0–254.

## They are uniform, and they have no serial structure

| test | observed | uniform bytes predict |
|---|---|---|
| distinct values in 176 draws | 129 | 127.4 |
| Shannon entropy | 6.90 bits | — (7.46 is the 176-sample ceiling) |
| values above 127 | 52.3% | 50% |
| printable ASCII range | 38.6% | 37.1% |
| adjacent equal values | 0 | 0.7 |
| coincidences at lag 8 (one row) | 3 of 168 | 0.7 |
| coincidences at lag 13 | 0 of 163 | 0.6 |

Uniform over 300 would predict 133.3 distinct, which the observation also sits near, so
the distinct count does not discriminate the two readings — the leading digit does.

**So this is not an encoding of runes and not text.** 52% of the values exceed 127, which
no text encoding produces, and a 29-symbol alphabet packed into bytes would leave a wrap
artifact at 256 mod 29 that is absent.

## Not primes

The obvious Cicada guess. Reading each grid, both grids concatenated in both orders,
forwards and reversed, as base-256, base-300 and base-60-digit integers — 24 readings
from 575 to 2,075 bits — **every one is composite**, and every one has a factor below
10,000. Ordinary integers.

## Not the body's keystream

The second obvious guess: the grids are the key. Scored exactly like any generator in
`sequence_key_sweep.py` — values mod 29 and base-60 digits mod 29, both grids separately
and concatenated, forwards and reversed, over 29 alphabet offsets, both senses, and word
starts across the body. **8,760 candidates, best +10.93** against the +14.25 a true key
reads on a 57-rune prefix. Nothing.

## What this leaves

176 bytes, 1,408 bits, statistically indistinguishable from random. That is what a hash,
a cipher key, or already-encrypted data looks like — and it is a positive statement, not
an absence: the Liber Primus contains 1,408 bits of high-entropy material that is not
runes and not the rune cipher's keystream.

The block sizes are 104 and 72 bytes. Neither is a standard hash or key length, and the
two do not divide evenly into one.

## Falsifiable next steps

- If the bytes are a hash, they are 176 bytes, not 64 — so either two or more digests
  concatenated, or a digest plus something else. A 64-byte window that is a SHA-512 of a
  known Cicada string would show up in a direct search over window offsets.
- If they are ciphertext, they carry no structure to attack without the key, which is
  what uniformity means.
- Both grids read left-to-right, top-to-bottom here. Column-major or boustrophedon
  orders permute the multiset and so change none of the tests above except the integer
  and keystream readings; those are cheap to rerun if a reason appears.

## Status

**Status**: confirmed (measurement), 176 tokens, complete — 13×8 and 9×8 exactly, no
token dropped at a line wrap. `experiments/number_grid_bytes.py`, `--primes`,
`--keystream`.

## Related

- `isdigit-counts-circled-marks` (memory) — which flagged the pages as untranscribed.
- `running-key-math-sequence.md` — the +14.25 keystream benchmark.
