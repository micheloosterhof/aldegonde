# New directions for the Liber Primus body, October 2026

What to do once the walk, the dodge and the odometer stop paying. Written after
the 2026-10-24 clean-up; every number below comes from
`experiments/new_directions_probes.py` or the file named beside it.

## 1. Why the walk family feels stuck, stated once

`hypotheses/what-any-solution-must-satisfy.md` leaves a cipher that changes its
alphabet at every letter, carries a period-5 structure inside words, changes
base at every separator through a chain of at least 2,700 distinct bases, and
suppresses adjacent repeats by looking at its own output, with memory of one
rune and strength φ ≈ 0.90.

`hypotheses/doublet-suppression-requires-design.md` then closes the design
space for the suppression itself. For any cipher that is a bijection position
by position, a sub-chance doublet rate is a rare-diagonal relation
`R_j = f_j⁻¹ f_{j+1}` tuned against the plaintext bigram table. The only way out
is a step that is not a bijection: the encryptor consumes extra state when a
repeat would occur. Those are the two classes, and the directory has one
carrier for each:

| class | carrier tried | where it stands |
|---|---|---|
| tuned relation | the walk, `g` of order 5 and `σ` per word | 16 bits recoverable of 283 (`why-the-body-resists.md`); every free cell lands except the DJU-BEI return |
| non-bijective step | the dodge on the walk; the Quagmire odometer with a dodge | 17 of 19 free cells, d6w misses on 31 coincidences; no recorded outcome of the enumeration (`quagmire_runner.py --run`) |

So "a mechanism that is neither" does not exist inside the position-wise
cipher class. What is open is everything around the suppression:

- **A. Information outside the rune stream.** The local channel is capped at
  16 bits; a crib programme needs about 300 words and the rubricated titles
  give 52.
- **B. The plaintext side.** What the words are, in what order, in what
  language, and how the 2-rune hole arises.
- **C. The carrier and its key size.** A carrier with an enumerable key turns
  a search into a verification.
- **D. Anchors for the base chain.** DJU-BEI is one exact state return; a
  second would multiply every base-free filter.

## 2. Probed today

Seven cheap, key-free probes. Each asks one question a direction depends on.

| probe | question | result | verdict |
|---|---|---|---|
| repeat-slot | Could the 86 doublets be one plaintext rune `s` written as "repeat the previous rune" (the exclusion-tableau cipher, which suppresses for free)? | `s` would need non-initial rate 0.0063, initial rate 0.0079, and be word-final in 30% of its non-initial uses. 0 of 29 runes fit all three within 2σ. IA and EA have the rate but are never final (z −2.6, −2.7). | **excluded** |
| period | Is the DJU-BEI word distance 1,449 the period of a word-clocked machine? | Word-aligned coincidence at D = 1,449 reads +3.19σ, rank 3 of 2,877 distances; the scan maximum is +3.74. Without the phrase itself, +2.73σ. A true period would give ~287 hits against 201. | **no period**; the signal is the phrase |
| anchors | Do the 17 identical ciphertext words mark base returns, as DJU-BEI does? | The three words after each pair: 11/140 pooled, 8/137 without DJU-BEI (+1.5σ). True returns would give ~8 extra. | **no second anchor** |
| predecessor | Does the alphabet depend on the previous ciphertext rune (memory-one output feedback under a per-word base)? | At lags 2, 3, 4, 6, 7, 8 the equal-predecessor cell reads 17/398 (+0.9σ) where the model predicts +1.7σ: 0.8σ of separation, so the corpus cannot decide. At lag 5, 9/66 = 4× chance, which is the known digraph pairing restated. | **no power**; needs a keyed test |
| lengths | Are the words interleaved or transposed with a fixed period? | Block-length autocorrelation is flat at lags 1–10; the +2.84 at lag 12 is what 12 null lags give. | **no fixed period** |
| language | Is the 2-rune hole another language's token-length marginal? | Against the whole marginal English fits best by far (χ² 139 on 11 df, digraph-compressed, from wordfreq) against ≥ 286 for nine others. | **English stays**; the hole is joining (E9) |
| grids | What is on the number-grid pages? | **Three** grids, not two: chunk 64 carries 10 × 8 beside its 66 runes. 80 + 104 + 72 = **256 bytes = 2,048 bits**, uniform (161 distinct of 162 expected). | **new fact**; see 3.1 |

## 3. Directions, ranked

### 3.1 The 256-byte block as RSA-2048 material (class A)

`number-grids-are-bytes.md` recorded 176 bytes in two grids and remarked that
neither 104 nor 72 is a standard length. With the third grid the total is the
one standard length in asymmetric cryptography. Read big-endian in page order
the integer is even, so it is not a modulus and not a prime; a signature or a
ciphertext can be any value below the modulus.

- **Test.** For each of Cicada's published RSA public keys with a 2,048-bit
  modulus, compute `pow(s, e, n)` for the block in four readings (row-major
  and column-major, page order and reversed) and look for PKCS#1 padding
  (`00 01 ff … 00` then a DigestInfo) or any structured output.
- **Also rerun** `grid_hash_search.py` and `number_grid_bytes.py --keystream`
  on 256 bytes and the six concatenation orders; their negatives were
  measured on 176 bytes and two orders.
- **Kill.** No key yields structure in any reading. The block then stays
  "ciphertext under a key we do not hold" and the direction closes.
- **Cost.** One session plus the keys, which are not in the repository.
- **Why it ranks first.** It is the only lead whose success would hand over
  bits the rune stream cannot supply, and it is decisive either way.

### 3.2 Within-sentence word transposition, keyed by length (class B)

Michel's reading (`the-words-are-transposed-within-sentences.md`): the four-dot
is a full stop, the spans are sentences, and the word order inside each span is
gone. `the-rearrangement-is-not-a-simple-rule.md` excludes identity (P = 2e-6),
reversal and rotations by 1–3, and finds no fixed rule better than a shuffle,
concluding the permutation varies from sentence to sentence.

- **What is untested.** A rule keyed by the sentence's own length is a
  varying permutation with no key: columnar with width `f(n)`, a rail fence
  with `f(n)` rails, a rotation by `n mod k`, or the mark's dot count as the
  width. `which_structured_permutation.py` takes a rule as a function of the
  span; add a dozen length-keyed rules and score them on the same two edge
  profiles.
- **Consequence for cribbing, whatever the result.** If the words are moved,
  a crib is a word, never a phrase. Any crib drag that slides a two-word
  phrase across the body assumes adjacency the plaintext may not have.
  DJU-BEI is a ciphertext phrase and stays valid as a state return; it says
  nothing about two adjacent plaintext words.
- **Kill.** Every length-keyed rule scores no better than a shuffle; then the
  permutation needs a key and the transposition is a second cipher layer to
  budget for.

### 3.3 Record the enumeration's outcome before building anything else (class C)

`quagmire_runner.py` is a complete verify-not-search programme over about
2.2 × 10⁸ odometer keys with the DJU-BEI filter first. Neither
`quagmire-odometer.md` nor the script records whether `--run` was carried to
the end. That is the cheapest decisive fact in the directory:

- a negative at full coverage kills the odometer carrier, which is progress;
- an incomplete run is the one computation worth finishing before any new
  carrier is proposed, because every carrier below needs the same machinery.

### 3.4 One library cipher for every carrier (class C)

Every carrier is the same object: a per-letter alphabet, a per-word base
chain, and a preventer. `library-candidates.md` item 7 asks for it as a cipher.
Make it one class with three pluggable parts and both directions:

```
encrypt(words, key) -> words      decrypt(words, key) -> words
  letter step   : g (order 5) | 5-shift schedule | none
  base chain    : product walk | odometer with carry | any f(state, L_w)
  preventer     : none | dodge (re-step) | hold | exclusion
```

Decryption with a dodge is deterministic: the receiver sees the same previous
ciphertext rune and re-steps at the same places. The payoff is that a crib test,
a planted-key control, and the fingerprint battery become one code path, so
a new carrier costs an afternoon rather than a script. Port it with the first
experiment migrated onto it.

### 3.5 Ciphertext feedback as the carrier's clock (class C)

`ciphertext-autokey.md` excludes an alphabet chosen by the previous ciphertext
rune alone; with a per-word base in front, today's key-free probe has no power.
The test that does have power is keyed: replace the dodge in
`compact_state_models.py` with "the dial advances by the previous ciphertext
rune", run the 19-cell battery across keys (G4: score the fraction of keys
that make the corpus plausible), and see whether the seam, d1w and the clock
cells land without a tuned diagonal. It is one more entry in that script.

### 3.6 Make the crib dictionary match the joined plaintext (class B)

`short-units-are-written-joined.md` fits the 2-rune hole by absorbing about
40% of 2-rune units into their neighbours (3,100–3,300 plaintext words, 170–400
joined). Today's language probe confirms the hole is not another language. So
the body's blocks include joined pairs the dictionary does not contain:
`ofthe`, `inthe`, `tothe`, `andthe`, `tobe`, `itis`. Extend
`build_register_vocab.py` with the register's 2-rune words joined to their
observed successors, weighted by the author's own text. Cheap, and it raises
every crib programme's hit rate before any cipher is chosen.

### 3.7 Things to stop doing

- Fitting one more cell to one fitted key. G4: eleven of nineteen cells test
  the key, not the mechanism.
- Scanning lags. A2, B4 and today's `period` probe have exhausted the
  autonomous-period channel to the corpus length.
- Reading one p-value from a scan. `stats.family_pvalue` is the path.

## 4. Verdicts to carry into the hypotheses directory

- The exclusion-tableau reading (repeat = one rune) is excluded on the
  positional profile. A line in `doublet-suppression.md` under consequences.
- The number grids hold 256 bytes in three grids. Recorded as a dated
  correction in `number-grids-are-bytes.md`.
- Word-aligned coincidence has no peak at the DJU-BEI distance beyond the
  phrase itself; the 17 identical words do not continue. Both belong in
  `the-chain-shows-only-in-extension.md` as further negative halves.
