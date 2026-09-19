---
type: observation
---
# Observation: Under the Walk, DJU-BEI is a Chance Repeat, so the State-Return Gate Rejects a True Key

## Feature

Two exclusions in this directory tested only the keys that pass a DJU-BEI gate:
the interval product over words 1477..2926 must fix at least 6 points. The gate is
a necessary condition for a true key **only if DJU-BEI is a genuine state return**
(same plaintext phrase, same base on its six points). Under the length-clocked walk
with a large group ⟨g, σ⟩ that reading is about 7,000 times less likely than a
chance ciphertext repeat. If the repeat is chance, a true key passes the gate at
the same rate as any wrong key (5.9×10⁻⁴), so each gated sweep discarded a true key
with probability 0.9994 and excluded nothing.

## Status

**Status**: confirmed (argument); both affected sweeps re-run ungated, both negative
(the keyword family only inside its register bands).

## The two readings, priced

`experiments/base_free_verifier.py` header and the count below.

- **Chance repeat.** A word-anchored, boundary-consistent repeat of 6 or more runes
  appears in about 1.0% of doublet-corrected surrogate corpora
  (`repeated-phrase-dju-bei.md`, `experiments/anchored_repeats.py`).
- **Genuine return under the walk.** An LP-sized prose corpus
  (`walk_reference.json`, 2,928 words) holds **479** pairs of positions carrying the
  same two-word phrase of 6 or more runes. For the ciphertext to repeat, the
  interval product must fix six specific distinct points (DJU and BEI share no
  rune). For a product in a group of order ~4×10³⁰ that has probability
  1/(29·28·27·26·25·24) = 2.9×10⁻⁹. Expected genuine returns: 479 × 2.9×10⁻⁹ =
  **1.4×10⁻⁶**.

So under the walk the odds are about 7,000 to 1 that DJU-BEI is a coincidence. The
planted corpus agrees: enciphered under a generic key it contains zero repeated
two-word ciphertext phrases.

`quagmire_runner.py` states the consequence itself: "A random key almost never
satisfies a state return, so to exercise the positive path we plant sigma inside
the conjugated-shift group". Its positive control therefore used a degenerate key
that returns by construction. No test showed that a generic true key passes the gate.

## What this voids

| exclusion | keys verified | keys in the family |
|---|---|---|
| keyword Quagmire (`mixed-alphabet-vigenere.md`) | 186,465 | 313,972,400 |
| affine σ × magic-square g (`affine-sigma.md`) | 28 | 37,352 (and only 46 of 190,008 g) |

Neither family was excluded. Statements elsewhere that "the keyword family has been
enumerated in full and is negative" rest on the gate.

## The other reading: a genuine return means a small state space

DJU-BEI is genuine only if bases recur often enough. With N effective bases visited
about uniformly, two equal plaintext phrases share a base with probability ~1/N:

| N | expected two-word returns (479/N) | expected excess identical words, length ≥ 3 (13,449/N) |
|---|---|---|
| 600 | 0.80 | 22 |
| 2,000 | 0.24 | 6.7 |
| 12,180 (PSL(2,29)) | 0.04 | 1.1 |
| 4×10³⁰ | 1×10⁻⁶ (as computed above) | 0 |

The observed excess of identical words is 6.3 ± 3.3 (17 against 10.7,
`word-transform-census.md`), and there is one two-word return. Against "bases never
recur", N ≈ 2,000 is favoured about 5 to 1 by the identical-word count and about 24
to 1 by the return (0.24 against 0.01), roughly 100 to 1 together. N was fitted
after the fact, which costs a factor of a few, and the 10.7 baseline is itself a
null that could be off. So this is a lean toward a state space of a few thousand
bases, not a finding. N = 812 (the affine group) is disfavoured the other way: it
predicts 16.6 excess identical words and 3.5 repeated words of length ≥ 4, against
6.3 and 0 (joint p ≈ 10⁻³). The window that fits is roughly 2,000 to 5,000; 5·29·29
= 4,205 sits inside it.

The two readings disagree about the model. A genuine return is incompatible with a
generic ⟨g, σ⟩, because Burnside leaves no transitive group on 29 points between
812 and 4×10³⁰ (`rotor-machine-compact-state.md`). A compact state indexed by a
PUBLIC clock is already excluded (`word_state_sweep.py`: 13 state variables, the
841-state two-disk included, all under 4.5% of a full effect). What is left for a
compact state is a clock the solver cannot compute: one driven by the plaintext or
by key material. On 30 points there is also a mid-sized group: PGL(2,29), order
24,360, which contains elements of order 5. These are leads, not results.

**The public-clock exclusion has a blind spot, and one weak cell sits in it**
(`experiments/word_state_local_sweep.py`). The global bucket test assumes the solver
computes the state exactly. A clock that slips now and then, as 3301's F-interrupts
make their solved key streams slip, leaves distant bucket-mates unaligned: a planted
disk slipping once per ~40 words reads 0.0350 globally (chance 0.0345) and 0.068
within 10 words (z = +10). Re-run on pairs of nearby words, the sweep is negative
over 3,058 cells (max z +3.37). Inside the 29-disk family (A + βw) mod 29 the
strongest member is A − w, the count of letter steps so far, which is the walk's own
increment: 969 of 25,144 pairs within 60 words, z = +3.52, present in both halves,
above all 200 clocks built from shuffled word lengths, not a layout effect;
family-wise p ≈ 0.013. The digraph check gives +1.6σ where full alphabet sharing
predicts about +6σ, so it is at most a 6–10% partial effect. Status: weak
watch-item. The broader key (A − w + j) mod 29, a 29-step progressive alphabet,
shows nothing.

One model would give numbers of this size, and is stated here so it can be tested,
not because the data establish it. Let the alphabet be set by the public clock
(A − w) mod 29, a SECRET second coordinate with 29 values, and the within-word phase:
29 · 29 · 5 = 4,205 alphabets. Two words with equal public clock then share an
alphabet one time in 29, which predicts a global bucket reading of
1 + (1/29)(1.74 − 1) = 1.025; `word_state_sweep.py` measured 1.022 for this cell and
set it aside as the second best of ~7,400. Word identity needs both coordinates
equal, so N = 841: 0.57 expected two-word returns (one seen) and 9.5 to 16 excess
identical words (6.3 ± 3.3 seen), but also 3.4 repeated words of length ≥ 4 where
none is seen (p ≈ 0.03). It does not explain why the local rate is higher than the
global one.

## The replacement: a verifier that needs neither base₀ nor DJU-BEI

`experiments/base_free_verifier.py`, `experiments/walk_score_kernel.c`.

Under the walk c = base₀(M_w(g_j(p))) with M_w known once the letter perms and σ
are fixed. Write u = base₀⁻¹(c). Every ciphertext rune value stands for one unknown
point u, and the ~447 positions carrying it decrypt through known permutations of
that same u: p = g_j⁻¹(M_w⁻¹(u)). For the right key and the right u the decrypts
follow the plaintext unigram distribution; otherwise they are flat. The score is
the best one-to-one assignment of u to c, in nats per rune above flat.

On the planted corpus, base₀ withheld:

| words | true key | one-swap σ | one-conjugation g | random σ |
|---|---|---|---|---|
| 200 | 1.205 | 0.515 | 0.488 | 0.471 |
| 400 | 1.189 | 0.380 | 0.364 | 0.346 |
| 2,928 | 1.181 | 0.144 | 0.142 | 0.134 |

The assignment recovers base₀ exactly (29/29) with no hill-climb. The compiled
kernel scores about 14,000 keys per second per core on three 250-word windows, so a
(g-family × σ-family) product of 10⁹ keys takes a few hours on ten cores.

The assignment must be one-to-one. A wrong key whose g and σ share a fixed point x
lets every rune claim u = x and decrypt to the constant text x x x …; scored with
an independent maximum per rune, such a key beat the true key (1.54 against 1.22).
The grid × affine positive control found this.

## Short windows: partial credit near the key, none far from it

`experiments/windowed_gradient.py`. Cutting the corpus into disjoint k-word windows,
each with its own free base, limits how far one wrong σ image propagates. Planted
corpus, mean window score:

| k | true | σ 1 swap | σ 2 swaps | σ 4 swaps | g 1 conj. | random |
|---|---|---|---|---|---|---|
| 40 | 1.037 | 0.942 | 0.915 | 0.918 | 0.931 | 0.900 |
| 80 | 1.056 | 0.756 | 0.733 | 0.722 | 0.738 | 0.677 |
| 160 | 1.160 | 0.566 | 0.551 | 0.543 | 0.557 | 0.525 |
| 2,928 | 1.181 | 0.143 | 0.142 | 0.138 | 0.138 | 0.135 |

At k = 80 a key one transposition from the truth stands about 8 typical standard
deviations above random keys, so an enumeration scored this way also flags near
misses. The credit is gone by 4 swaps: the landscape is smooth only within a few
transpositions of the key. This does not rescue blind search
(`no-known-plaintext-foothold.md` stands); it widens what an enumeration can catch.

## A second loss in the same sweeps: the candidate bands rest on one register

`experiments/register_band_sensitivity.py`. The keyword sweeps keep a letter wheel
only if its predicted within-word doublet rate, computed on a stand-in prose table
(Pride and Prejudice), falls inside the Wilson band of the observed rate
[0.0049, 0.0080]. That rate is a sum of 29 rare pair frequencies, and rare pairs
are what differs between books. Of 4,838 random relations inside the band under
the stand-in, the share still inside it under another book is:

| register | still in band | diagonal ratio, 10th–90th percentile |
|---|---|---|
| Emerson, Essays | 46–52% | 0.91–1.46 |
| King James Bible | 49% | 0.80–1.53 |
| Nietzsche | 45–48% | 0.92–1.56 |
| Thoreau, Walden | 54% | 0.93–1.34 |
| Bunyan, The Pilgrim's Progress | 60% | 0.80–1.39 |
| Blake | 31–35% | 0.89–1.89 |
| Beowulf | 24% | 1.03–1.73 |

So a band built on one register keeps a true letter wheel about half the time, and
the seam band on the σ side loses again. A negative sweep inside these bands covers
roughly a quarter of the family. Widening d1 to about [0.004, 0.014] restores the
coverage at roughly ten times the candidates per side; with the compiled verifier
that is a day of compute, not a redesign.

## Results of the ungated re-runs

All three are negative (2026-09-19). Every key was scored directly on three
200-word section openings (sections 2, 4 and 8), base₀ free, no gate. A window score
of 0.85 nats/rune was the candidate floor: wrong keys sit near 0.5 and a true key near
1.2 (planted controls: 1.22 against a best wrong 0.54–0.60).

| sweep | complete keys | keys at or above 0.85 | best whole-section score of the top keys |
|---|---|---|---|
| keyword Quagmire, original 196,898 keywords × 446 disks | 365,526,436 | 0 | 0.44 |
| keyword Quagmire, 38,672 left-out keywords and 214 left-out disks | 334,988,084 | 0 | 0.49 |
| all 190,008 magic-square g × all 812 affine σ | 154,096,488 | 0 | 0.45 |

The left-out keywords are dictionary words of 3 and of 13–20 letters (CIRCUMFERENCE
has 13), the register vocabulary, and PRIMES, KOAN, CICADA, LIBER, PRIMUS, TOTIENT,
DIUINITY. A wrong key scores 0.2–0.45 on a whole section of 259–680 words; nothing
rose above that.

**What these negatives cover.**

- *Magic-square g × affine σ is excluded outright* under the walk's conventions
  (Gematria index order for the affine map, clock (L − 1) mod 5, standard
  tokenisation). No band filter was applied: every member was scored.
- *The keyword-Quagmire family is excluded only inside its register bands.* The d1
  and seam bands keep a true key about a quarter of the time (previous section), so
  this is a negative on roughly a quarter of the family, now including long keywords
  and 3301's vocabulary. Closing it needs the widened-band sweep, about 50 times
  the keys (~2×10¹⁰, of the order of a day on this machine).
- A key is missed if all three windows are spoiled, for instance by a wrong word
  boundary inside the first 200 words of sections 2, 4 and 8 alike, or if the
  plaintext's rune frequencies are far from English runeglish.
- A key within one or two transpositions of an enumerated key is NOT caught: on
  200-word windows a one-swap neighbour scores like a random key. Catching near
  misses needs the 80-word summed objective above, at about five times the cost.

The first attempt at the keyword sweep died twice for lack of memory (each spawned
worker re-imports `aldegonde.c3301`, which builds ~330 MB of n-gram tables). The
sweep now logs every finished task, resumes from that log, and forks its workers.

## Scripts

- `experiments/base_free_verifier.py` — the verifier and its planted-key self-test.
- `experiments/walk_score_kernel.c`, `walk_score_kernel.py` — compiled scorer.
- `experiments/quagmire_ungated_sweep.py` — keyword-Quagmire family, ungated.
- `experiments/grid_affine_ungated.py` — all 190,008 grid g × 812 affine σ, ungated.
- `experiments/windowed_gradient.py` — the short-window table.
- `experiments/register_band_sensitivity.py` — the band-retention table.

## Related

- `repeated-phrase-dju-bei.md` — the repeat and its 1% chance rate.
- `mixed-alphabet-vigenere.md`, `affine-sigma.md` — the gated sweeps.
- `key-local-channel-is-empty.md` — says σ's absence blocks the evaluation of any g
  construction; with this verifier a (g, σ) family pair is evaluated directly.
- `thirty-symbol-disk.md` — the 30-symbol reading that PGL(2,29) would need.
