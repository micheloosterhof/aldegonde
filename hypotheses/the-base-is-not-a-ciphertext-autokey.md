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

Also untouched: a **plaintext** autokey. That is unfalsifiable here for the obvious reason,
and it is worth recording that the ciphertext version was the testable one and it failed.

## How to falsify this result

- Find a coarser feature of the previous word that does lift matched-position coincidence;
  the five tried here are illustrative, not exhaustive.
- Show the 742 identical-predecessor pairs are mis-parsed — they depend on `body_words`
  treating page breaks as word-internal, which merges 32 blocks relative to `body_parse`.
- Show the English matched-position rate of 0.0794 is the wrong H1 for a plaintext whose
  register differs from the three used.
