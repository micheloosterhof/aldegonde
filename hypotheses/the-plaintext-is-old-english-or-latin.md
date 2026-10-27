---
type: hypothesis
---
# Hypothesis: The Plaintext Is Old English or Latin, Not Modern English

## Claim

The body's plaintext language is not the register the solved pages are written in. The
rune row is the Anglo-Saxon futhorc, and four of its letters are dead in the author's
English: J, EO, OE and AE carry 5 of the register's 2,882 runes. Old English needs æ and
eo constantly; Latin needs ae and oe. An alphabet designed with four letters the author's
own text never uses suggests a text that does.

## Status

**Status**: unresolved. Proposed 2026-10-25. Modern languages were tried and failed
(`new_directions_probes.py language`); Old English and Latin were not, for want of a
corpus in the repository.

## Mechanism

No cipher change. Every inference that reads the plaintext through the cipher changes:
the bigram table `g` must be rare on, the within-word lag profile the carrier must
reproduce, the seam table for σ, the unigram table the alphabets must flatten, and the
word-length marginal with its hole at length 2.

## Evidence for

- Four dead letters in a 29-letter alphabet, exactly the Old English and Latin vowels.
- The author's style elsewhere (Latin title, Anglo-Saxon runes, archaic register).
- The 2-rune share of 0.159 against English's 0.242; joining explains it (E9), but a
  language with fewer 2-letter function words would too.

## Evidence against

- Against ten modern languages from wordfreq the body's whole length marginal fits
  English best by far (χ² 139 on 11 df against 286 or worse), so the hole is not a
  modern-language signature.
- The solved pages and every text Cicada published are English.
- The lag-5 echo's size depends on the plaintext's own within-word lag-5 coincidence,
  which is high in English (2.1× on the register) and would have to be measured again.

## Predictions

1. Transliterate an Old English corpus (Beowulf, Ælfric) and a Latin one (the Vulgate,
   Caesar) by the author's digraph rules (æ → ᚫ, eo → ᛇ, oe → ᛟ, ea → ᛠ, þ/ð/th → ᚦ,
   ng → ᛝ, io/ia → ᛡ) and compare the word-length marginal with the body's. A fit better
   than English's χ² 139 keeps the hypothesis; worse kills it.
2. Under Old English the within-word lag profile d1..d6 of the plaintext differs from
   English's (0.68, 1.12, 1.46, 1.71, 2.11, 1.74 × chance on the register); the carrier
   the ledger reconstructs must then reproduce a different profile, and the `g` filter of
   `d-profile-pins-g-to-five-cycles.md` must be rerun on the new tables.

## Scripts

- `experiments/new_directions_probes.py language` — the modern-language run.
- To add: the two corpora (not fetchable from this environment) and a transliterator
  beside `c3301.encode_english`.

## Related

- `encoding-only.md` — the English runeglish encoding, which is the baseline here.
- `short-units-are-written-joined.md` — the competing explanation of the hole at 2.

## Verdict

Open until an Old English or Latin corpus is in hand; one χ² decides it.
