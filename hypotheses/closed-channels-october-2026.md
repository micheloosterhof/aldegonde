---
type: observation
---
# Observation: Six Channels Closed While Drafting the October 2026 Hypotheses

## Feature

Each candidate mechanism considered on 2026-10-25 implied one cheap key-free check. Six
were run; six came back at chance, two of them with a planted or recut control showing
the check had power. `experiments/closed_channels_october_2026.py`.

## Measurement

| channel | what a mechanism would give | the body | verdict |
|---|---|---|---|
| a restart at the thirteen-dot marks (26 unit starts) | the first words of every unit share a state: ~58 aligned hits of 949 | 38, z +0.94; two and three words deep +0.12, −0.17 | no shared start state |
| a Baconian message in the word lengths | 5-bit groups with letter-like nIoC ≈ 2.1 on 32 symbols | parity 0.983 against 1.000 for independent bits; length > 4 reads 1.271 against 1.300 | the lengths carry no second message |
| the rubricated runes as plaintext or key letters | nIoC ≈ 1.78 on 217 runes | **0.952 ± 0.035** | the red words are enciphered like the rest |
| words in lexicographic rune order | adjacent increasing pairs 1.00 | 0.501 | no |
| the per-word alphabet a function of a running checksum of the ciphertext (rune-index sum and Gematria sum, before and including the word, mod 29 to 3,000) | label-matched words share an alphabet; planted control at N = 3,000 reads **z +15.8** | largest of 36 cells z 1.91 | excluded with power |
| body sentences as word-scrambled copies of the author's 94 known sentences | long spans share a length multiset | 0 of 137 against a recut null of 2.9 | not from the solved pages |

## Significance

- The thirteen-dot marks structure the text (`the-thirteen-dot-closes-a-section.md`) but
  the cipher runs through them, extending `the-cipher-does-not-restart.md` from the
  four-dot marks to the thirteen-dot ones.
- The rubricated titles are cribs, not keys written in clear
  (`rubrication-crib-candidates.md` stands as written).
- A self-synchronising chain keyed by what has been written so far, the one way to get
  thousands of bases with no bookkeeping, is out for any additive checksum up to a
  3,000-state register. `the-base-is-not-a-ciphertext-autokey.md` covered the previous
  word; this covers the whole prefix.
- The known-plaintext reading survives only for texts outside the repository.

## Scripts

- `experiments/closed_channels_october_2026.py`

## Related

- `the-body-composes-the-taught-devices.md`, `the-body-is-a-scrambled-copy-of-published-text.md`,
  `the-plaintext-is-old-english-or-latin.md`, `the-body-is-machine-made.md`,
  `the-plaintext-was-prepared-against-cribs.md` — the hypotheses these checks were run for.
