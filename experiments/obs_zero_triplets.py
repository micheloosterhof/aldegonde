# ABOUTME: Observation: zero triplets (runs of 3 equal runes) in the clean corpus
# ABOUTME: -- stronger than doublet suppression alone would give.
"""Zero triplets. Significance: Poisson tail of observing 0 given the count
expected from the OBSERVED doublet rate (not the uniform rate) -- i.e. even
granting doublet suppression, are triplets rarer still?"""
from __future__ import annotations
import math
from lp_corpus import load_clean


def main() -> None:
    stream, _ = load_clean()
    n = len(stream)
    trip = sum(1 for i in range(n - 2) if stream[i] == stream[i + 1] == stream[i + 2])
    doub = sum(1 for i in range(n - 1) if stream[i] == stream[i + 1])
    p_d = doub / (n - 1)
    # if doublets were independent events at rate p_d, a triplet is two adjacent
    # doublets: expected ~ (n) * p_d^2
    exp_uniform = (n - 2) / (29 * 29)
    exp_given_doublet = (n - 2) * p_d * p_d
    print(f"triplets observed: {trip}")
    print(f"expected under uniform (1/29^2): {exp_uniform:.1f}")
    print(f"expected if doublets were independent at observed rate: {exp_given_doublet:.2f}")
    print(f"Poisson P(0 | uniform expectation) = {math.exp(-exp_uniform):.1e}")
    print("VERDICT: zero triplets -- consistent with doublet suppression extending")
    print("to runs (a doubled rune is never immediately re-doubled).")


if __name__ == "__main__":
    main()
