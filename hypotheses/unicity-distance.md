---
type: observation
---
# Observation: The Walk Family Is Over-Determined 60-Fold; a Free Per-Word Permutation Is Unbreakable

## Feature

Every attack here is a search. Before searching it is worth knowing which key models
12,956 runes could pin down *at all*, because a key carrying more entropy than the
ciphertext carries redundancy has many consistent solutions and no amount of
cleverness separates them.

Unicity distance is `U = H(key) / D`, with `D` the plaintext redundancy per rune.
`D` is measured on the author's own runeglish (1,796 runes of recovered plaintext)
rather than imported, and since a 1,796-rune sample overstates English entropy, the
true `D` sits at the high end of the range below — which makes the "unbreakable"
verdicts conservative.

| key model | H(key) bits | U at D=1.52 | at D=2.40 | at D=2.90 |
|---|---|---|---|---|
| walk: base₀ + g + σ | 308 | 203 ✓ | 129 ✓ | 106 ✓ |
| odometer: alphabet + schedule + 2 dials | 137 | 90 ✓ | 57 ✓ | 47 ✓ |
| per-word **shift** base | 14,224 | 9,341 ✓ | 5,927 ✓ | 4,905 ✓ |
| per-word base from a 1,000-element group | 29,180 | 19,163 ✗ | 12,158 ✓ | 10,062 ✓ |
| per-word **arbitrary permutation** | 301,005 | 197,679 ✗ | 125,419 ✗ | 103,795 ✗ |

✓ = determined in principle by the available ciphertext. ✗ = more key entropy than the
ciphertext can pin, so many keys yield sensible plaintext and none is distinguishable.

## Status

**Status**: confirmed (calculation). `experiments/unicity_distance.py`. The entropy
input is measured on the author's own plaintext; the key-entropy figures are exact
given each model's parameter count.

## What it settles

**The walk and odometer families are over-determined by 60 to 140 times.** Their keys
are three permutations and a handful of residues — 137 to 308 bits — against a
ciphertext that can pin roughly 20,000. So their difficulty is **entirely search**, not
information: the answer is uniquely there, and `no-known-plaintext-foothold.md`'s
finding that the landscape over (g, σ) is "flat everywhere, spiked only at the exact
key" is a statement about the search surface, not about whether a solution exists.

**A freely chosen per-word permutation is unbreakable with this corpus**, by a factor
of 8 at the most favourable redundancy and 15 at the most conservative. If the author
picked each word's alphabet independently, no method recovers the plaintext from
12,956 runes, and the project should stop looking for one.

So the decisive question is not which permutation family the bases come from, but
whether they are **generated or chosen**. `two-rune-depth-no-base-reuse.md` shows the
base essentially never repeats, which is consistent with both; a generator with a large
orbit and free choice look identical locally, which is exactly why
`key-local-channel-is-empty.md` finds no constraint on σ.

## Limits

- `D` is the uncertain input and the table spans it. The two verdicts that matter — the
  walk over-determined, a free permutation underdetermined — hold across the whole
  range. Only the 1,000-element-group row flips, at D ≈ 2.25.
- Unicity distance assumes the attacker can recognise correct plaintext, which here is
  true (English is recognisable). It says nothing about computational cost.
- There is no more ciphertext. The master transcription's 15,933 runes are the front
  matter's 2,797 plus page0-58's 13,136, of which the solved AN END page and the
  plaintext Parable make up the 180 beyond the clean 12,956.

## Related

- `no-known-plaintext-foothold.md` — the search-surface result this reframes.
- `key-local-channel-is-empty.md` — why σ has no local constraint either way.
- `flat-ioc.md` — the ≥949-alphabet bound, which says how many alphabets, not whether
  they are generated.
