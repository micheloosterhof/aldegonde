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
with probability 0.9994. Neither sweep excluded its family.

## Status

**Status**: confirmed (argument); both affected sweeps re-run ungated, both negative
(the keyword family only inside its register bands). The compact-state reading the
argument opens is constrained but NOT closed: see "The compact-state reading, tested".

## The probability of each reading

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

A comment in `quagmire_runner.py` says the same: "A random key almost never
satisfies a state return, so to exercise the positive path we plant sigma inside
the conjugated-shift group". Its positive control used a degenerate key that
returns by construction. No test showed that a generic true key passes the gate.

## Which exclusions this affects

| exclusion | keys verified | keys in the family |
|---|---|---|
| keyword Quagmire (`mixed-alphabet-vigenere.md`) | 186,465 | 313,972,400 |
| affine σ × magic-square g (`affine-sigma.md`) | 28 | 37,352 (and only 46 of 190,008 g) |

Neither family was excluded. Statements in other files that "the keyword family has
been enumerated in full and is negative" depend on the gate.

## The second occurrence ends the encrypted text

Michel's point (2026-09-19): ᛞᛄᚢ-ᛒᛖᛁ at words 2926–2927 is the last two words of
the unsolved corpus, and the first occurrence opens a section body two words after
a 13-dot (`repeated-phrase-dju-bei.md`). He reads this as a deliberate repeat.

The corpus has 183 adjacent (3,3) word windows, and a chance repeat of this
size is (3,3)-shaped about three times in four, so a chance repeat includes the
final window with probability ≈ 0.75 · 2/183 = 0.8%, and "a chance repeat that ends
the text" is a ≈ 8×10⁻⁵ event. But a genuine return is no more likely to land there
than a chance one: a typical window holds the same 2/183 share of the repeated
(3,3) phrases as it does of the (3,3) window pairs. The position favours the genuine
reading only by the factor k by which the closing words of a text are more likely to
be a recurring formula than an average phrase. k is a prior about how 3301 writes.
A value of 3 to 10 is plausible. It is not the factor of about 100 that the 0.8%
figure alone implies.

The position does not make a genuine return more likely under the walk. With a group
of order ~4×10³⁰ a genuine return on six points has probability 3×10⁻⁹ at any
position. So "DJU-BEI is a deliberate repeat" and "the base walks in a generic
⟨g, σ⟩" cannot both be true. If the repeat is deliberate, the generic walk is wrong.
The next section covers that case.

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
null that could be off. The counts favour a state space of a few thousand bases.
They do not establish it. N = 812 (the affine group) is disfavoured the other way: it
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
24,360, which contains elements of order 5. None of this has been tested.

**The public-clock exclusion misses a clock that slips. A local test finds one
weak cell** (`experiments/word_state_local_sweep.py`). The global bucket test assumes the solver
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

One model gives numbers of this size. It is recorded so that it can be tested. The
data do not establish it. Let the alphabet be set by the public clock
(A − w) mod 29, a SECRET second coordinate with 29 values, and the within-word phase:
29 · 29 · 5 = 4,205 alphabets. Two words with equal public clock then share an
alphabet one time in 29, which predicts a global bucket reading of
1 + (1/29)(1.74 − 1) = 1.025; `word_state_sweep.py` measured 1.022 for this cell and
set it aside as the second best of ~7,400. Word identity needs both coordinates
equal, so N = 841: 0.57 expected two-word returns (one seen) and 9.5 to 16 excess
identical words (6.3 ± 3.3 seen), but also 3.4 repeated words of length ≥ 4 where
none is seen (p ≈ 0.03). It does not explain why the local rate is higher than the
global one.

## The compact-state reading, tested (2026-09-19)

`experiments/compact_state_models.py`. Each model sets the base of word w from a
state; English prose is enciphered under it and measured with the same functions as
the corpus. The LP reads 1 return, 17 identical cipher words of 3 runes or more, 0
of 4 or more, and 1.007 on the (A − w mod 29, phase) clock statistic.

**The transition rule matters more than the state count.** If the state is drawn
independently per word, a two-word return needs two coincidences and is about N
times rarer; the simulations give 0 returns at every N. If the state advances
deterministically from the plaintext, two occurrences of one phrase in the same
state stay in step across it, so a repeated word carries the next word with it. Only
the deterministic form can produce DJU-BEI at all.

**A state built only from public data is refuted again**, and by a wider margin than
in `word_state_sweep.py`: the public clock alone reads 2.196 on the clock statistic
against the LP's 1.007, because every word in a bucket then shares an alphabet.

**The word counts bound the state space from below.** 260 prose corpora over 10
registers, deterministic plaintext-driven state, N states:

| N | P(word counts fit) | P(return) | P(return \| word counts fit) |
|---|---|---|---|
| generic walk | 0.742 | ~1.4×10⁻⁶ | ~1.4×10⁻⁶ |
| 850 | 0.008 | 0.365 | 0.000 |
| 1,200 | 0.015 | 0.335 | 0.000 |
| 2,000 | 0.123 | 0.242 | 0.031 |
| 4,205 | 0.342 | 0.096 | 0.011 |
| 20,000 | 0.619 | 0.031 | 0.006 |

N below about 1,200 is refuted by the LP's own counts: it leaks 27 to 73 identical
cipher words where the LP has 17. This corrects the estimate earlier in this file,
which put N at 600 to 5,000 from the excess of identical words alone; the proper
null for that count is a generic walk on real prose, which already gives 11.0, so
the LP's excess is +1.3σ rather than +1.9σ and the lower bound moves up.

Among the state counts that do fit the word counts, the return occurs in 0.6% to 3%
of corpora, against 1.4×10⁻⁶ for a genuine base return under a generic walk.

**That comparison is wrong, and the correction costs two orders of magnitude
(2026-09-20).** 1.4×10⁻⁶ is the probability the walk produces a GENUINE return. It is
not the probability the walk produces the observed data, because a walk also produces
chance collisions: two different plaintext phrases enciphering to the same runes. The
repo already measures that — a word-anchored, boundary-consistent repeat of 6 runes or
more appears in **1.0%** of doublet-corrected surrogate corpora
(`repeated-phrase-dju-bei.md`). Under the walk the data is 7,000 times more likely to
be a collision than a return, so P(data | walk) = 0.010, not 1.4×10⁻⁶.

| N | P(genuine return) | P(data \| compact) | P(data \| walk) | likelihood ratio |
|---|---|---|---|---|
| 2,000 | 0.265 | 0.275 | 0.010 | 27.5 |
| 2,500 | 0.212 | 0.222 | 0.010 | 22.2 |
| 4,205 | 0.126 | 0.136 | 0.010 | 13.6 |
| 20,000 | 0.026 | 0.036 | 0.010 | 3.6 |

So the repeat favours a compact state by a factor of **4 to 28**, not 10⁴. The
end-of-text position adds its own factor of 3 to 10 (see above), giving perhaps 10 to
300 in all — against which the architecture needed spends 88 of the 103 bits in a
base. The honest reading is that DJU-BEI is weak-to-moderate evidence for recurrence,
not strong, and that it does not by itself carry an architecture.

**The seam constrains it, but does not close it (corrected 2026-09-20).** None of the
models above suppresses the cross-word doublet: an unrelated base per state gives
0.0355, the chance rate, against the LP's 0.0079 — 101 predicted against 23 observed,
z = −7.8. So consecutive bases cannot be independent; the difference
`base_w⁻¹ ∘ base_{w+1}` must be a rare-diagonal permutation at most boundaries.

An earlier version of this section went on to argue that this makes the set of bases a
group, so the state count is a group order, so Burnside's theorem on transitive groups
of prime degree closes the reading. **Michel pushed back and he is right: that step is
wrong.** A tuned difference on every transition does not make the bases a group. It
makes them a set of N permutations whose pairwise differences along the transition
edges are tuned — a constraint satisfaction problem, not closure under composition.
Group structure follows only if the step is drawn from one fixed set and composed
along the walk, which is the walk's own architecture and exactly the assumption a
compact-state alternative is entitled to drop. With state-dependent steps there is no
group, Burnside does not apply, and the orbit test below tests a case that never had
to arise.

What survives is weaker and quantitative.

**A counting bound on the branching factor.** A random permutation's seam diagonal
lands in the observed interval [0.0050, 0.0118] with probability 1.14×10⁻³, so each
tuned relation costs 9.8 bits, while one base carries log₂(29!) = 102.8 bits of
freedom. The seam rate is an average, so not every relation need be tuned — but at 80%
tuned it is already 0.0117, above the observation, so roughly 90% must be.

The seam relation is `g^(−a) ∘ D` with `a` the last word's final phase, so **one
transition edge carries five constraints, not one** (corrected 2026-09-20,
`experiments/compact_base_cycle.py`; a first version of this paragraph counted one and
concluded ten):

| branching d | tuned relations per state | bits needed | against 102.8 |
|---|---|---|---|
| 1 | 4.5 | 44 | yes |
| 2 | 9.0 | 88 | yes, marginally |
| 3 | 13.5 | 132 | no |
| 10 | 45.0 | 440 | no |

So the transition may branch about **two** ways: the plaintext feature driving the
state carries roughly one bit per word, and even then the design spends 88 of the 103
bits available in a base. The gematria-sum automaton tested above branches 29 ways and
is excluded outright; a one-bit feature is at the edge of possible.

**The cyclic sub-case is closed twice over.** First on the state count.  If the base advances by powers of a single σ, the
bases are ⟨σ⟩ and N = ord(σ). The letter step must then lie in ⟨σ⟩ as well, so
`g = σ^(N/5)`, and the walk needs `g` rich — cycle type 5⁵1⁴, since a `g` with many
fixed points passes plaintext doublets straight through. Over every cycle type of 29
points, 35 qualify and the largest state count is **N = 100** (σ of type (25,4)),
with 75 and 60 next. That is far below the 2,000–4,205 the word repeats allow, and
N = 100 would leak roughly 150 excess identical words against the 6.3 observed. So a
schedule that is powers of one permutation cannot be compact enough.

Second, and independently of the state count, powers of one permutation are far too
correlated to serve as bases at all. Dropping the walk's `g` factor from the base step
frees `g` from ⟨π⟩ and lets π reach order 2520 (cycle type (9,8,7,5)), which is inside
the window the word repeats allow — but `π^h` and `π^h'` agree on every cycle whose
length divides `h − h'`, so two states share about 4 of 29 images where two independent
permutations share 1. Measured against the LP: identical cipher words 144 against 17,
long repeats 34 against 0, unigram IoC 1.033 against 1.000, and the clock statistic
1.21 against 1.007. A permutation with short cycles is worse still — cycle type
(2,3,5,7,11,1) pins one ciphertext rune for every state, IoC 1.056. **The bases must be
close to independent, which no single-generator schedule gives.**

**The orbit test, for the sub-case it covers.** Where the schedule *is* a group and
that group is intransitive, orbit labels pass through the cipher unchanged and adjacent
ciphertext runes carry the plaintext's orbit correlation. Over 1,500 random partitions
the 2×2 within-word adjacency chi-square reaches 1443.4 on real prose, 43.3 on the LP,
and 38.2 ± 4.0 on doublet-preserving surrogates — z = +1.28, nothing. (The surrogate
is essential: a uniform null puts the LP near 38 on the suppressed diagonal alone.)
This closes intransitive group schedules. It says nothing about non-group ones.

**So DJU-BEI as a genuine state return is open, and the room left is narrow.** It
requires a cipher whose per-word base is drawn from a designed set of a few thousand
near-independent permutations, with tuned transitions and a branching factor of about
two — a one-bit plaintext feature per word, spending 88 of the 103 bits in a base.
Nothing tested here is that, and no construction for it is known: the only cheap way to
tune every edge at once is a single generator, which is exactly what the correlation
result above rules out.

**Three corrections in three days, all in the same direction.** The gate itself
inherited the walk's assumption about DJU-BEI; the closure above inherited the walk's
assumption that steps compose into a group; the 10⁴ figure compared a genuine return
against a genuine return instead of against the data. Each time the error was
comparing the challenger with the wrong alternative, and each time it favoured
whatever I had just built. The standing check before any verdict here: name the
alternative explicitly, and ask which of the incumbent's assumptions the test
inherited. The position argument at the top of this
file still applies to it, and so does the word-count evidence, which favours such a
state over the generic walk by about 10⁴.

**Also not yet tested.** Whether such a model reproduces the d5 echo and the doublet
suppression. Both are properties of `g` and the within-word base, so they should carry
over unchanged, but that has not been measured.

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

## Short windows: a near-miss key scores above random only within a few transpositions

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
misses. At 4 swaps the score equals that of a random key. Blind search still does
not work (`no-known-plaintext-foothold.md` stands). An enumeration scored this way
detects keys within one transposition of the true key.

## The candidate bands depend on the stand-in register

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
coverage at roughly ten times the candidates per side. With the compiled verifier
that is about a day of compute.

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

The keyword sweep was killed twice for lack of memory (each spawned worker
re-imports `aldegonde.c3301`, which builds ~330 MB of n-gram tables). The
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
