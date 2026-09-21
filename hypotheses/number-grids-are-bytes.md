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

## Three more readings tested, all negative

**Not a digest of anything in the book.** The AN END page states that *a page of this
book hashes to something*, which makes the self-referential reading the one to try
first. Every window of every digest length (16, 20, 32, 64 bytes) was indexed under four
grid orders — row-major and column-major, each forwards and reversed, for both
concatenation orders — giving 3,712 distinct windows. Against that: MD5, SHA-1, SHA-256
and SHA-512 of 261 strings, being every master chunk's runes as Unicode text, as UTF-8
and as raw indices, every solved page's plaintext in English and in rune indices, the
whole body, the master file, and the named strings the book uses as keys. **1,044
digests, no hit.**

That rules out the self-referential reading. It cannot rule out a digest of a string
this project does not hold, and nothing can.

**Not a page packed in base 29.** 1,408 bits is about 290 runes, so the grids are the
right size to be a densely packed page — a Cicada-idiomatic construction. Unpacking each
of the 24 big-integer readings into base-29 digits, both digit orders, and scoring with
runeglish trigrams:

| | mean log-trigram |
|---|---|
| LP's own plaintext | **+14.280** |
| best of 48 unpackings | +7.267 |
| uniform random runes | +5.662 |

Every unpacking sits by the random reference. (The plaintext reference +14.28 matches the
+14.25 a true key scores on the AN END page in `running-key-math-sequence.md`, which is a
useful cross-check on the scorer.)

**Not a repeating XOR.** Key lengths 1 to 8, each residue class fitted to the
best single XOR byte by English-likeness: the best score is 0.52 at key length 8, against
2.46 for English prose and −0.84 for random bytes. The score rises monotonically with key
length, which is the free parameters rather than a signal — eight key bytes fitted to 176
is 22 bytes per parameter.

## What cannot be tested, and why it is not worth pretending otherwise

The natural next guess is an RSA modulus: 128 of the 176 bytes would be 1,024 bits. The
only cheap test is that a modulus has no small factors, and a random integer avoids every
factor below 10⁴ about 6% of the time. Over the 49 possible 128-byte windows, roughly
three would pass by chance. A pass would therefore prove nothing and a fail would exclude
nothing, so the test is not run. Confirming a modulus needs factoring it.

This is what uniformity means in general: the tests above work because each proposes a
*specific* structure, and once those are exhausted a uniform blob offers no purchase.

## Falsifiable next steps

- The window search above covers strings the repo holds. A digest of an external Cicada
  artifact — an onion address, a published message, a key fingerprint — would need that
  artifact in hand, and is the one live extension.
- If they are ciphertext, they carry no structure to attack without the key, which is
  what uniformity means.
- Both grids read left-to-right, top-to-bottom here. Column-major or boustrophedon
  orders permute the multiset and so change none of the tests above except the integer
  and keystream readings; those are cheap to rerun if a reason appears.

## Status

**Status**: confirmed (measurement), 176 tokens, complete — 13×8 and 9×8 exactly, no
token dropped at a line wrap. `experiments/number_grid_bytes.py` with `--primes`,
`--keystream`, `--unpack`, `--xor`; `experiments/grid_hash_search.py` for the digest
windows.

## Related

- `isdigit-counts-circled-marks` (memory) — which flagged the pages as untranscribed.
- `running-key-math-sequence.md` — the +14.25 keystream benchmark.
