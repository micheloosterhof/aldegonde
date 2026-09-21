---
type: hypothesis
---
# The Base Chain Is Invisible in Every Marginal Statistic and Visible in Exactly One Conditional

## Status

**Status**: confirmed as a characterisation, weak as evidence. The negative half is
solid; the positive half rests on one event in the corpus.

## The question

Every σ result in this directory — `sigma-is-even.md`,
`sigma-moves-almost-every-rune.md`, `sigma-cycle-type-narrowed.md` — assumes the
walk's chain:

    base_(w+1) = base_w ∘ g^(a_w) ∘ σ

But `two-rune-depth-no-base-reuse.md` shows the base is effectively distinct for all
2,928 blocks, and a chain through 2,928 distinct permutations of A₂₉ looks, pairwise,
like 2,928 independent draws. So: is the chain an object the corpus can see, or only
a feature of the model?

The test builds a cipher identical in every other respect — same `g` of order 5, same
continuous clock, base fixed inside a word, base changed at every separator — and
differing only in whether the new base is composed with `g^a ∘ σ` or redrawn at
random.

## The negative half: no marginal cell sees it

`experiments/chain_is_observable.py`, 16 keys × 20 corpora per cipher. Separation
pools the within-model spread over corpora *and* keys.

**Not one of the 19 battery cells reaches separation 1.0.** The largest is `ioc` at
0.36. Six cells agree to four decimal places, and that is provable rather than
measured: a within-word statistic sees one uniformly random base under either rule,
so `d1w` through `d6w`, `doublet_pos` and `doublet_gap_min` are identical *in
distribution*.

Pairing on `g`, which both ciphers share, removes the key variance that dominates
eleven of the cells (`battery-cells-test-the-key.md`). It changes nothing: only
`kappa_max_z` reaches |t| = 1.71 over 16 keys, and that is a maximum over 39 skips.

### The positive control says the test is not simply blind

Against chains whose base pool is deliberately closed, so that base reuse exists to
find:

| pool | identical | returns | max separation | cell |
|---|---|---|---|---|
| 29 | 104.0 | 3.45 | **5.39** | long |
| 100 | 40.4 | 0.95 | **3.28** | long |
| 300 | 21.9 | 0.20 | **1.95** | long |
| 1,000 | 15.7 | 0.00 | 0.74 | identical |
| 2,928 | 13.5 | 0.00 | 0.57 | d2w |

The marginal counts detect base reuse down to a pool of about 300 and go blind above
1,000. The corpus sits above that, so the null result has a scope: **a chain that
never revisits a state leaves no marginal trace.**

## The positive half: the extension rate

One statistic is not marginal, and it is the one the chain is built to move.

Of the word pairs that repeat, what fraction extend to a repeated two-word phrase?

- **Under a chain**, equal bases at `w` and `v` give equal bases at `w+1` and `v+1`
  whenever the clock phases agree, because both step by the same rule. The phases are
  set by the block lengths, so that is one time in five.
- **Under independent draws**, the second alphabet has to coincide on its own: one
  time in N.

So a chain multiplies the extension rate by about **N/5** while leaving every
marginal count alone. That is precisely why nothing above saw it.

Measured over 8 keys × 20 corpora each:

| pool | rule | identical | returns | rate | 1 in |
|---|---|---|---|---|---|
| 300 | chained | 2,530 | 32 | 0.01265 | 79 |
| 300 | free | 2,390 | 1 | 0.00042 | 2,390 |
| 500 | chained | 1,998 | 32 | 0.01602 | 62 |
| 500 | free | 1,980 | 0 | 0 | >1,980 |
| **corpus** | | **17** | **1** | **0.05882** | **17** |

The predicted ratio N/5 is 60 at N = 300; the measured ratio is 30. The shortfall is
the six-rune floor on what counts as a phrase.

### What that says about the corpus

From 17 identical pairs, the expected number of extensions is 17/79 = 0.22 under a
chained pool of 300 and 17/2,390 = 0.0071 under free draws. The corpus has one.

    P(at least one | chained) = 0.19
    P(at least one | free)    = 0.0071

**The single return is about 30 times more likely under a chained base than under
independent per-word draws.** Under the chain it is an ordinary event; under free
draws it is a 1-in-140 coincidence.

## Superseded on evidence, confirmed on direction (next day)

The positive half above is a factor of 30 built from simulated prose at a chosen pool
size. `word-repeat-accounting.md` reaches the same conclusion from the corpus alone:
shuffling only the ORDER of the corpus's own ciphertext words holds all 17 repeats fixed
and puts two of them adjacent once in 20,000 draws, and requiring `identical` and
`returns` to imply one pool excludes the chainless reading by a factor of eight.

The negative half -- that no marginal battery cell sees the chain -- is unaffected and
is what makes the conditional reading necessary.

## Consequences

- `returns` is not a dead cell and it is not a key measurement. It is the chain's
  only observable, and it has to be read conditionally on `identical` rather than on
  its own. This corrects `battery-cells-test-the-key.md`, which classes `returns` as
  a mechanism cell that every shape fails identically — true marginally, false
  conditionally.
- The σ constraints keep their conditional status but gain a tested antecedent. The
  chain is no longer only a modelling convenience.
- The same arithmetic prices any future evidence: each additional identical pair buys
  0.013 of an expected extension under a chain and 0.0004 under free draws, so
  separating them at 3σ needs on the order of 700 identical pairs against the
  corpus's 17. **This channel cannot be strengthened with the text that exists.**
- It also explains `dju-bei-stands-alone.md` without needing a special mechanism. One
  extension among 17 repeats is what a chain produces; no shorter companions is what
  a pool of a few hundred produces.

## Falsification

- If the extension advantage is an artifact of the deterministic cycle used for the
  chained arm, replacing it with `base_(w+1) = base_w ∘ g^a ∘ σ` at a σ of matching
  order must reproduce a rate near 1/79 at pool 300. If it comes out near the free
  arm's 1/2,390, the argument fails.
- If `identical` is inflated by the prose register rather than the cipher, rerunning
  both arms on the LP's own plaintext (`lp_plaintext_register.py`) must preserve the
  ratio between the arms even if both counts move.
- If a marginal cell is later found with separation above 1 at pool 2,928, the
  negative half is wrong and the test was simply underpowered.

## Scope

One `g` family, prose plaintext, a deterministic-cycle chain as the archetype, and a
single observed event on the corpus side. The negative half is robust across 16 keys;
the positive half is one return and should be quoted as a factor of 30, never as a
proof.

## Scripts

- `experiments/chain_is_observable.py`
- `experiments/base_pool_thermometer.py`

## Related

- `battery-cells-test-the-key.md` — the classification this corrects for `returns`.
- `two-rune-depth-no-base-reuse.md` — the pool floor that puts the corpus beyond the
  marginal test's reach.
- `dju-bei-stands-alone.md`, `dju-bei-is-more-surprising-than-recorded.md` — the
  single return, now priced against a chainless alternative.
