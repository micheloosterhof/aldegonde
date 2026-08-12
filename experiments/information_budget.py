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

The budget is brutal and it explains every failure in this project without
appealing to bad luck: the ciphertext-statistical channel is worth of order ten
bits against a key of order 180. That is why no filter discriminates, why the
landscape is a delta function, and why enumeration is forced. It also sizes the
alternative: a contiguous crib must be long enough to cover the gap.
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
    print("  So the ciphertext-statistical channel cannot identify the key. Every")
    print("  filter being weak is a consequence of this, not a run of bad luck.\n")

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
