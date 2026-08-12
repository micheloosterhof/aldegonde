# ABOUTME: Counts how many bits about the key the ciphertext statistics can supply
# ABOUTME: against how many the key contains, and how long a crib would have to be.
"""How many bits does the ciphertext actually give up about the key?

Two counting arguments, neither statistical.

**Why the doublet trigger set must have exactly 29 members.** At within-word
position k the pair map is

    (p_k, p_{k+1})  ->  (A(p_k), A(g(p_{k+1})))        A = base_w o g^(k mod 5)

a product of bijections, hence a bijection on the 29^2 = 841 bigrams. The doublet
ciphertext set {(x, x)} has exactly 29 members, one per rune, so its preimage has
exactly 29 members too, and it is {(g(b), b)} -- the GRAPH OF A PERMUTATION. Two
consequences, both structural rather than measured:

  - a single plaintext bigram cannot be the trigger: it cannot map onto 29
    distinct ciphertext doublets
  - "a doublet whenever p_{k+1} = X" cannot either: that set is {(y, X)}, which
    has the right count but repeats the second coordinate, whereas a permutation
    graph uses each rune exactly once there

The other 812 plaintext bigrams map bijectively onto the 812 non-doublet
ciphertext bigrams, so nothing is left unaccounted for. But it also means a single
adjacent pair leaks exactly ONE BIT -- in-graph or not -- because that is the only
A-invariant function of the pair.

**This argument is conditional on the walk's structure and FAILS for a ciphertext
autokey.** It assumed the pair map factors into two position-independent
bijections. If the second alphabet depends on the first ciphertext rune it does
not factor, and with an additive feedback

    c_{k+1} = p_{k+1} + c_k - X   (mod 29)   =>   c_{k+1} == c_k  <=>  p_{k+1} == X

a SINGLE plaintext rune is the trigger, and the doublet rate is simply that rune's
frequency. That reading is strictly better on one observation the walk has to pay
a coincidence for: the suppression is boundary-blind (within-word 0.628%, seam
0.786%, z = -0.92 of one rate), which an autokey trigger gives BY CONSTRUCTION
because `p = X` does not care where words end, whereas the walk needs g's diagonal
and sigma's diagonal -- unrelated permutations on different tables -- to coincide.

Feedback models nevertheless face a DILEMMA, and it closes them:

  - ADDITIVE feedback makes the delta stream the plaintext shifted by a constant,
    so it must read IoC ~1.78. Measured within words: delta 1.0246, second
    difference 1.0008, Beaufort sum 1.0004. Refuted.
  - GENERAL feedback (an arbitrary permutation B_x per previous rune x) escapes
    that, and can even force a single-rune trigger by requiring B_x(X) = x for
    every x. But then each group of runes sharing a previous rune is enciphered by
    ONE fixed permutation, so grouped IoC must read ~1.78. Measured, grouping
    within words: lag 1 gives 1.0227, lag 2 gives 0.9979, lag 5 gives 1.0060.
    Refuted.
  - A HYBRID -- per-word base plus feedback -- keeps grouped IoC flat because the
    base still varies inside every group. But the trigger becomes
    `p_k = B_x^-1(base_w^-1(x))`, which depends on the word, so it cannot equal a
    single rune X for all w, and the doublet rate reverts to ~1/29 unless the base
    schedule is tuned. The suppression then needs exactly the kind of tuning the
    walk needed, and nothing has been gained.

So feedback cannot deliver the single-rune trigger AND survive the grouped-IoC
test at the same time. What survives of the idea is its one real advantage:
boundary-blindness falls out for free, where the walk must pay a coincidence.

**What those bits are worth.** The doublet count pins the scalar
`theta = sum_b P(g(b), b)` to Poisson precision. Comparing the prior spread of
theta over random order-5 permutations with the measured precision gives the
information gained, and the doublet POSITIONS add nothing on top: phase mod 5 is
flat (chi2 2.59 on 4 df) and so is the start/middle/end profile, so the pattern
carries only its count.

**JOINT vs MARGINAL identifiability -- the distinction that matters.** The scalar
budget above is NOT the channel capacity, and reading it as such is a mistake worth
naming, because it gives the wrong diagnosis.

Unicity distance settles the joint question. With runeglish redundancy
D = log2(29) - H_lang and a key of ~178 bits, the key becomes unique after
H_key/D = 53-75 runes depending on the language entropy assumed. The corpus is
12,956 runes, about **209x the unicity distance**, so the true (g, sigma,
plaintext) is uniquely determined many times over. The Liber Primus is NOT
information-starved.

The isomorph channel shows where that information lives. For within-word positions
j < k,

    c_j == c_k   <=>   p_j == g^((k-j) mod 5)(p_k)

which involves g and the plaintext ONLY -- no base_w, no sigma, no global
schedule. Across 30,013 within-word position pairs with 804 matches (2.68%) that
is 0.178 bits per pair, **5,343 bits** in total, and it is LOCAL: given g, each
word constrains its own plaintext independently.

But that information is about (g, plaintext) JOINTLY. Marginalise the unknown
plaintext away and almost nothing about g survives, because each word admits many
plaintexts. Measured: for the 23 doublet-bearing words of length <= 4, each admits
roughly 420 of the 841 possible g-edges once the rare-bigram budget is applied --
half the edge space. Since g supplies 29 edges, every candidate g satisfies every
word, so a per-word constraint-satisfaction attack has no pruning power at all.
What is left after marginalisation is the handful of scalar bits tabulated above.

**A rigorous version, which is stronger than the empirical one.** Within a word
`base_w` is ONE unknown bijection applied elementwise, and the complete invariant
of a sequence under an unknown elementwise bijection is its EQUALITY PATTERN. So
the isomorph pattern is not merely one within-word observable, it is the ONLY one.
Anything else requires comparing across words, where `base_w` and `base_w'` differ
by the step product over the intervening lengths -- i.e. it is key-GLOBAL.

And the isomorph constraint turns out to be satisfiable for essentially every
candidate: over 3,000 consecutive real prose words the MEDIAN random order-5 g
makes ZERO words impossible, and only 32% are refuted at all. A constraint
satisfiable by almost every g carries almost no information about g. That closes
the local channel by argument rather than by exhaustion:

  - within-word observables = isomorph only, worth ~16 bits about g (see below)
  - therefore every informative observable is cross-word, hence key-global
  - key-global means no partial credit: right key or noise, which IS the delta
    function

CORRECTION (August 2026, `magic_square_sweep.py`): the 4.0-bit figure below is the
DOUBLET COUNT alone. Since g has order 5, every distance d tests g^(d mod 5) on the
distance-d plaintext table, so d1..d7 give SEVEN g-only constraints. With plaintext
tables weighted to the LP's word-length histogram they cut the space by 133,000x =
**17.0 bits**, four times what the budget credited. The conclusion is unchanged --
17.0 against g's 79.7 leaves ~63 bits, about 1e19 candidates, and sigma's 97.9 are
untouched -- but the local channel is four times richer than stated. Note the
reference tables must be weighted, not resampled: resampling ~23k words leaves enough
noise to swing a 2-sigma pass/fail with the seed.

Four measured attempts agree with it: the doublet count yields 4.0 bits; the
isomorph bag score gives a real gradient but hillclimbs plateau at chance
agreement (0-3 of 29); adding a quadgram sequence model gives no measurable
improvement, because ~20 plausible candidates per word let a wrong g be assembled
into fluent text; and the hard-rejection filter cuts only 1.5x.

That is the precise diagnosis, and it explains every failure here without
appealing to bad luck:

  - jointly identifiable, 209x over -> a correct key is verifiable instantly
  - the local channel is nearly vacuous -> no filter or gradient can exist
  - therefore only joint search works, and that is ~10^53 keys

Falsifiable, and this is where to push: the argument assumes `base_w` changes at
every word and is otherwise free. If it does not change per word, within-word
invariants extend across words and the isomorph channel stops being vacuous.

So the two escape routes are exactly: shrink the key space by structure until it
can be enumerated, or import external information. This file sizes the second --
a contiguous crib long enough to cover the gap.
"""

from __future__ import annotations

from math import factorial, log2, sqrt

M = 29


def key_entropy() -> tuple[float, float]:
    """Bits in g (order-5, type 5^5 1^4) and in sigma (a 29-cycle)."""
    n_g = factorial(M) // (5**5 * factorial(5) * factorial(4))
    n_s = factorial(M - 1)
    return log2(n_g), log2(n_s)


def scalar_bits(prior_sd: float, count: int, trials: int) -> float:
    """Bits gained by measuring a rate to Poisson precision against a prior."""
    post_sd = sqrt(count) / trials
    return log2(prior_sd / post_sd)


def main() -> None:
    bits_g, bits_s = key_entropy()
    print("KEY ENTROPY (base_0 is free -- recoverable exactly once g and sigma are)")
    print(f"  g,  order-5 type 5^5 1^4 : {bits_g:>6.1f} bits")
    print(f"  sigma, a 29-cycle        : {bits_s:>6.1f} bits")
    print(f"  total to determine       : {bits_g + bits_s:>6.1f} bits\n")

    print("WHAT THE CIPHERTEXT SUPPLIES")
    rows = [
        ("within-word doublets -> g", scalar_bits(0.0125, 63, 10028), "count only"),
        ("seam doublets -> sigma", scalar_bits(0.0073, 23, 2927), "count only"),
        ("d5 echo -> phi5", scalar_bits(0.26, 102, 2073), "one scalar, CI holds 1.0"),
        ("d6 suppression", scalar_bits(0.0125, 31, 1267), "null-dependent"),
    ]
    supplied = 0.0
    for name, bits, note in rows:
        supplied += bits
        print(f"  {name:<28}{bits:>6.1f} bits   ({note})")
    print(f"  {'d2, d3, d4 at chance':<28}{0.0:>6.1f} bits   (no information)")
    print(
        f"  {'IoC, entropy, periodicity':<28}{0.0:>6.1f} bits   (flat = no information)"
    )
    print(f"  {'total':<28}{supplied:>6.1f} bits\n")

    need = bits_g + bits_s
    print(
        f"  supplied / needed = {supplied:.1f} / {need:.1f} = {100 * supplied / need:.1f}%"
    )
    print("  This is the MARGINAL information about the key, after averaging the")
    print("  unknown plaintext away. It is why no filter and no gradient exists.\n")

    print("JOINT IDENTIFIABILITY -- the other half, and the one that matters")
    for h_lang, label in ((1.5, "English-like"), (2.0, "conservative")):
        d = log2(M) - h_lang
        print(
            f"  redundancy {d:.2f} b/rune ({label}) -> unicity distance "
            f"{need / d:.0f} runes"
        )
    print(f"  the corpus is 12,956 runes, about {12956 / (need / 2.86):.0f}x that")
    print("  so the key is UNIQUELY DETERMINED many times over: not information-")
    print("  starved, only computationally hard. A correct key verifies instantly.")
    print("  The isomorph channel holds 5,343 bits of that, and is LOCAL in g --")
    print("  but marginalising the plaintext leaves the scalars above, and each")
    print("  short doublet word admits ~420 of 841 g-edges, so no CSP prunes.\n")

    print("HOW LONG A CRIB WOULD HAVE TO BE")
    per_rune = log2(M)
    base0 = log2(factorial(M))
    print(f"  each crib rune pins one point of base_0, worth {per_rune:.2f} bits")
    print(f"  base_0 itself absorbs the first {M} runes ({base0:.0f} bits)")
    remaining = need - supplied
    extra = remaining / per_rune
    print(f"  after the {supplied:.0f} bits above, {remaining:.0f} bits remain")
    print(
        f"  -> {extra:.0f} runes of over-determination, so about {M + extra:.0f} contiguous"
    )
    print(
        f"     crib runes in total, roughly {(M + extra) / 4.42:.0f} consecutive words"
    )
    print("\n  For scale: DIVINITY WITHIN is 13 runes and yields ~14 bits (the")
    print("  recorded 16,000x reduction), consistent with this accounting and far")
    print("  short of sufficient. A crib of ~15 words would close it outright.")


if __name__ == "__main__":
    main()
