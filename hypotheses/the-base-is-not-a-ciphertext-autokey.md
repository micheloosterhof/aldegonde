---
type: observation
---
# Observation: The Per-Word Base Is Not a Function of the Previous Ciphertext Word

## Why it was worth testing

The per-word base is a general permutation taking at least 949 values
(`alphabet_count_bound.md`, `lag5-digraph-is-inside-the-word.md`). Where those values come
from is the open half of the cipher. A **ciphertext autokey at the word level** — the
previous word determines the alphabet for the current one — is the answer that would make
them recoverable, because a ciphertext key is written on the page.

It is also sharply falsifiable. Two words whose predecessors are identical would get
identical bases, and two words sharing a base coincide at matched positions at the
plaintext rate rather than at chance.

| | rate |
|---|---|
| H1, a shared base | 0.0794 (measured on English at matched positions) |
| H0, no shared base | 0.0345 (chance) |

`experiments/is_the_base_a_ciphertext_autokey.py`

## Result: excluded in every form

| if the base is a function of | pairs | seen | H0 | H1 | z vs H1 |
|---|---|---|---|---|---|
| **the whole previous word** | 742 | 30 | 26 | 59 | **−3.9** |
| its last rune | 465,312 | 16,160 | 16,045 | 36,943 | −112.7 |
| its first rune | 465,053 | 15,999 | 16,036 | 36,923 | −113.5 |
| its last two runes | 15,881 | 548 | 548 | 1,261 | −20.9 |
| its length | 1,986,954 | 68,441 | 68,516 | 157,754 | −234.4 |

Every row sits on H0 and nowhere near H1.

**The first row is the general test.** It assumes nothing about the function — a shift, a
keyed alphabet, a hash, anything deterministic gives identical bases to words with
identical predecessors. It is also the weakest row, because only 742 word pairs in the body
share an identical preceding ciphertext word. The arms are far enough apart that it still
prices at **7,300 : 1 against**.

## The literal positional autokey is separately dead

If `c_i(w) = p_i(w) + c_i(w−1) mod 29`, subtracting the previous word rune by rune recovers
the plaintext, so the difference stream would read as language.

| | |
|---|---|
| difference stream, 9,296 runes | IoC = **0.03447** |
| flat | 0.03448 |
| English runeglish | 0.0794 |

Flat to four decimal places.

## What is not excluded

A base depending on the previous word **and** something else — an absolute position, a
page, a running counter — would not give identical bases to identical predecessors, and
none of this touches it. What is excluded is the previous word acting alone.

~~Also untouched: a **plaintext** autokey. That is unfalsifiable here for the obvious
reason.~~ **Wrong, and corrected below.** A plaintext key has something a ciphertext key
does not: plaintext words repeat constantly, so the base recurs and the repeats are
countable. Michel pointed this out; see the next section.

## How to falsify this result

- Find a coarser feature of the previous word that does lift matched-position coincidence;
  the five tried here are illustrative, not exhaustive.
- Show the 742 identical-predecessor pairs are mis-parsed — they depend on `body_words`
  treating page breaks as word-internal, which merges 32 blocks relative to `body_parse`.
- Show the English matched-position rate of 0.0794 is the wrong H1 for a plaintext whose
  register differs from the three used.

## The plaintext autokey is falsifiable after all, and it is excluded

`experiments/a_plaintext_autokey_would_repeat.py`

Under a plaintext autokey the base for word w is a function of p_{w−1}. English repeats
words, so the same base recurs whenever the same word precedes two others. Worse for the
hypothesis, whenever the same plaintext *pair* (p_{w−1}, p_w) recurs, the ciphertext word
is **identical**.

### Test A: word-aligned coincidence

| | |
|---|---|
| P(two joined English tokens are the same word) | 0.00539 |
| a plaintext autokey predicts | 0.03472 |
| chance | 0.03448 |
| the body observes | **0.03439** |

Predicted 468,903 hits against 464,370 observed, **z = −6.8**.

### Test B: repeated ciphertext words, which is far sharper

| | |
|---|---|
| observed repeated-word pairs | 230 |
| chance floor, runes permuted, lengths kept | 245.7 ± 15.8 (z = −0.99) |
| a plaintext autokey adds ~245 more | → 491 (**z = −16.5**) |

The body's repeated words are entirely chance, and they sit where chance puts them: 107
pairs among one-rune words, 106 among two-rune, 17 among three-rune against 10.6 expected.
That last mild excess is the DJU-BEI family.

### The sharpest form: long words never repeat at all

| words of | in the body | repeats | chance | if a word always enciphered alike | P |
|---|---|---|---|---|---|
| 4+ runes | 1,646 | **0** | 0.19 | 1,317 | 0 |
| 5+ runes | 1,133 | **0** | 0.00 | 454 | 4e-198 |
| 6+ runes | 815 | **0** | 0.00 | 161 | 1e-70 |

**Not one ciphertext word of four runes or more occurs twice in the whole book.**

This is the same conclusion as `alphabet_count_bound.py`'s ≥ 949 alphabets, reached from
the plainest possible observation. It excludes far more than the autokey: any scheme in
which the same plaintext word enciphers the same way, whenever its context recurs, is
dead.

## The Gematria-sum forms, at full power (October 2026)

`experiments/base_by_previous_cipher_sum.py`

The whole-previous-block row above is the general test and the weak one (742 pairs). A
sum has only 29 values, so grouping blocks by the previous ciphertext block's Gematria
Primus sum puts hundreds of thousands of rune pairs at the same within-block phase into
shared-alphabet buckets. Michel's question was whether a word-level autokey could be
ciphertext-driven rather than plaintext-driven; a plaintext-driven compact state is already
dead by the alphabet count and the repeat census, and a ciphertext-driven one is public,
so it is tested directly. The running-sum rows cover the composed public form
base_w = base₀ ∘ T^(cumulative index).

| state of a block | pairs | matched | × chance | z vs chance | z vs a shared base |
|---|---|---|---|---|---|
| previous block GP sum mod 29 | 658,951 | 22,487 | 0.990 | −1.6 | −94 |
| previous block GP sum mod 5 | 3,808,981 | 130,661 | 0.995 | −1.9 | −223 |
| previous block GP sum mod 28 / 30 / 2 | 681,594 / 642,606 / 9,518,964 | | 1.001 / 1.000 / 0.999 | +0.1 / 0.0 / −0.5 | −94 / −91 / −350 |
| previous block GP sum, raw | 47,297 | 1,662 | 1.019 | +0.8 | −24 |
| previous block index sum mod 29 / mod 5 | 658,707 / 3,806,443 | | 1.002 / 1.001 | +0.4 / +0.5 | −92 / −221 |
| running GP sum mod 5 / 29 / 58 / 87 / 145 / 290 | 3.8M … 67,185 | | 0.995–1.025 | −2.0 to +1.2 | −223 to −28 |

Planted control — prose re-cut to the body's block lengths, 29 random bases indexed by
the previous ciphertext block's GP sum mod 29, the same g-cycle inside blocks — reads
**1.765 × chance, z = +117** on the matching row, and its side channels (the other
moduli, the index sums, the running sums) all lift to 1.02–1.05 at z = +2 to +15. The body
shows neither the main signal nor any side channel.

So the per-block alphabet set is not a function of the previous ciphertext block's sum
under any modulus, in either rune numbering, and not of a running sum of the ciphertext
either. With the rows above, a ciphertext autokey at the word level is excluded in every
bounded-memory form the page could supply; what survives is the composed form with secret
generators, which is a keyed walk whose selector happens to be public, not an autokey the
solver can follow.

## Conditional on the order of operations (October 2026)

Every row above groups blocks by their **visible** predecessor. That is the keying
predecessor only if the cipher ran in the visible order, which is the "shuffle, then
cipher" ordering of `the-words-are-transposed-within-sentences.md`. If the words were
enciphered in the author's order and permuted afterwards, the keying predecessor of a
block is a hidden word of its span, the 742 identical-visible-predecessor pairs are not
pairs with identical keying predecessors, and this closure is void. So:

- shuffle, then cipher: a base keyed on the previous ciphertext word is excluded (this
  file, 7,300 : 1 on the general row, every observable tap at the noise floor);
- cipher, then shuffle: open, and the chain runs in the hidden order, so a solver could
  not follow it without the permutation.

The mirror case, a base keyed on the previous **plaintext** word, is closed under the
opposite ordering only (`word-level-autokey.md`, same date).
