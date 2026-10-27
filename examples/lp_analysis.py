#!/usr/bin/env python3
"""Liber Primus analysis script.

Prints the basic cryptodiagnostics of every section of the clean corpus:
frequency distribution, index of coincidence, kappa at every skip, the
Friedman period test and the repeated n-grams. Nothing here is a result; it
is the first look a new section or a decryption candidate gets.

    python examples/lp_analysis.py
"""

from collections import Counter
from pathlib import Path

from aldegonde import c3301
from aldegonde.analysis import friedman_test
from aldegonde.grams import bigram_diagram
from aldegonde.maths import factor_pairs, prime_factors
from aldegonde.stats import (
    print_ioc_statistics,
    print_kappa,
    print_repeat_positions,
    print_repeat_statistics,
    shannon_entropy,
)

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-56.txt"


def main() -> None:
    """Run the diagnostics on each section of the clean corpus."""
    tok = c3301.tokenize(CORPUS.read_text(encoding="utf-8"))
    sections = sorted(set(tok.section))
    print(
        f"{len(tok.stream)} runes in {tok.word[-1] + 1} words and {len(sections)} sections"
    )
    for s in sections:
        seg = [r for r, sec in zip(tok.stream, tok.section, strict=True) if sec == s]
        runes = "".join(c3301.RUNES.decode(seg))
        print(f"\n\nSECTION {s} **************")
        c3301.print_all(runes, limit=30)
        print(f"length: {len(seg)} runes, {len(set(seg))} distinct")
        print(f"   prime factors = {prime_factors(len(seg))}")
        print(f"   factor pairs  = {factor_pairs(len(seg))[1:-1]}")
        counts = Counter(seg)
        print("frequencies:", " ".join(f"{c3301.i2r(r)}{counts[r]}" for r in range(29)))
        print(f"shannon entropy: {shannon_entropy(seg):.4f} bits")
        print_ioc_statistics(seg, alphabetsize=29)
        bigram_diagram.print_auto_bigram_diagram(runes, alphabet=c3301.CICADA_ALPHABET)
        print_kappa(seg, trace=True)
        friedman_test(seg, maxperiod=34)
        print_repeat_statistics(seg, minimum=2)
        print_repeat_positions(seg, minimum=5)


if __name__ == "__main__":
    main()
