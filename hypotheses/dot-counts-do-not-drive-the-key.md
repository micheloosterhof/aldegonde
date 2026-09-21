---
type: disproof
---
# Disproof: The Separators' Dot Counts Do Not Drive the Key

## The gap

`rotor-machine-compact-state.md` sweeps thirteen word-level state variables — word index,
cumulative rune count, section, line, sentence, the word's own length, a two-disk
combination — and finds none that indexes the alphabet. Every one counts something
structural. **None of them counts dots.**

The Liber Primus separates words with groups of dots and the transcription preserves the
count. Over the clean corpus:

| dots in the separator | 1 | 3 | 4 | 10 | 13 |
|---|---|---|---|---|---|
| occurrences | 2,762 | 4 | 136 | 2 | 25 |

3,663 dots against 2,929 words — **734 extra steps**. `marks-are-not-one-glyph` records
that the four-dot and thirteen-dot marks behave oppositely on an unrelated statistic, so
the count is not decoration.

"Advance the alphabet by as many steps as there are dots" is a natural hand instruction,
and the resulting state is the word index *perturbed*. That is the interesting part: it
is close enough to the plain word counter that a test of `w` would see a diluted version
of it, and far enough that the dilution matters. `word_state_sweep.py`'s two best cells
of ~7,400 were `w` and `A+w` — near misses of exactly that shape.

## Result: nothing, and the near miss was the null all along

| state | best nIoC | z vs surrogate | period |
|---|---|---|---|
| cumulative dot count | 1.023 | −0.43 | 65 |
| extra dots only (dots − 1) | 1.024 | −0.31 | 109 |
| marked words (1 or 2 per word) | 1.017 | −1.60 | 39 |
| word index (control) | 1.032 | +1.22 | 89 |

Best cells of 238 per state, periods 2–120, both phase conventions. **The surrogate scan
maximum is 1.0257 ± 0.0053** — so every state, the word-index control included, sits
inside the null.

Power is not the issue. A planted dot clock at period 37 reads **nIoC 2.638**, found at
period 111, its own third harmonic. A state that fully indexes the alphabet gives 1.74 by
construction.

## The null had to be empirical, and the first one was wrong

A first version scored these cells with a binomial standard error on the pooled
coincidence count, √(2/pairs). That gave the dot clock **z = +8.92** and the word-index
control **z = +10.45**, which looks like a discovery. It is not: pooled pairs share runes
and are not independent, and the scan takes a maximum over 238 correlated cells.

Against a surrogate — the same scan on a shuffled stream, same unigrams, same bucket
sizes — the whole set collapses to |z| < 1.6. The binomial figure was measuring the scan,
not the corpus. `rotor-machine-compact-state.md` flags this exact inflation and checks it
at 0.94–1.04× for its own tests; here, with a scan maximum rather than a single cell, it
is a factor of seven.

## Status

**Status**: disproved (planted control at nIoC 2.638 against a surrogate maximum of
1.026; every observed state inside the null). `experiments/dot_count_clock.py`,
`--control` for the plant.

## Scope

Three readings of the dot counts were tried: cumulative total, cumulative excess over
one, and a two-valued marked/unmarked counter. A rule that uses the dot count
*non-additively* — selecting an alphabet rather than stepping one, or resetting on a
13-dot mark — is not covered. What is excluded is the dot count as an additive clock.

## Related

- `rotor-machine-compact-state.md` — the sweep this adds a variable to, and whose near
  misses at `w` and `A+w` this explains as scan noise.
- `marks-are-not-one-glyph` (memory) — why the dot count was worth trying.
- `marks-are-not-clause-punctuation.md` — the other standing question about the marks.
