#!/usr/bin/env python3
"""Gorod Krovi Cipher 12 analysis script.

This script performs cryptanalysis on Gorod Krovi Cipher 12, which is
believed to be a 26-letter autokey cipher with a scrambled alphabet.

Ciphertext:
  Rc qipv jhx vld plson fhceuh itp jui gh qhzu dg sq xie dhw.
  U gbfl lf fluz pcag wrgkv zw, dinyg zw, qge gnvm L fhx.
"""

import random
from collections import defaultdict
from collections.abc import Callable, Sequence
from string import ascii_uppercase
from typing import Any

from aldegonde import auto, masc, pasc
from aldegonde.analysis.friedman import friedman_test
from aldegonde.maths.factor import factor_pairs, prime_factors
from aldegonde.stats.compare import quadgramscore
from aldegonde.stats.dist import print_dist
from aldegonde.stats.entropy import shannon_entropy
from aldegonde.stats.ioc import ioc as calc_ioc
from aldegonde.stats.ioc import print_ioc_statistics
from aldegonde.stats.kappa import print_kappa
from aldegonde.stats.repeats import print_repeat_positions, print_repeat_statistics

CIPHERTEXT_RAW = (
    "Rc qipv jhx vld plson fhceuh itp jui gh qhzu dg sq xie dhw. "
    "U gbfl lf fluz pcag wrgkv zw, dinyg zw, qge gnvm L fhx."
)

ALPHABET = ascii_uppercase

# Keywords related to Gorod Krovi / Call of Duty Black Ops 3 Zombies
KEYWORDS = [
    "GORODKROVI",
    "NIKOLAI",
    "RICHTOFEN",
    "DEMPSEY",
    "TAKEO",
    "PRIMIS",
    "SOPHIA",
    "DRAGON",
    "GERSH",
    "ZOMBIES",
    "STALINGRAD",
    "ASCENSION",
    "MAXIS",
    "SAMANTHA",
    "ORIGINS",
    "KRONORIUM",
    "SHADOWMAN",
    "APOTHICON",
    "KEEPER",
    "MONTY",
    "TREYARCH",
    "ELEMENT",
    "AETHER",
    "CIPHER",
    "SECRET",
    "BLOOD",
    "IRON",
    "SERGEI",
    "BELINSKI",
    "GROPH",
    "PETER",
    "MCCAIN",
    "ZETSUBOU",
    "DERRIESE",
    "KINO",
    "LUNA",
    "VALKYRIE",
    "MANGLER",
    "MARK",
    "SHIELD",
    "GAUNTLET",
]


def strip_to_alpha(text: str) -> str:
    """Strip non-alphabetic characters and uppercase."""
    return "".join(c for c in text.upper() if c in ALPHABET)


def print_header(title: str) -> None:
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def basic_statistics(ct: str) -> None:
    """Run basic statistical analysis on the ciphertext."""
    print_header("BASIC STATISTICS")
    print(f"Raw ciphertext: {CIPHERTEXT_RAW}")
    print(f"Stripped:       {ct}")
    print(f"Length:         {len(ct)} characters")
    print(f"Unique symbols: {len(set(ct))} / {len(ALPHABET)}")
    print(f"Prime factors:  {prime_factors(len(ct))}")
    print(f"Factor pairs:   {factor_pairs(len(ct))}")
    print()

    print_dist(ct)
    print()
    shannon_entropy(ct)
    print()
    print_ioc_statistics(ct, alphabetsize=26)


def kappa_analysis(ct: str) -> None:
    """Run kappa test for period detection."""
    print_header("KAPPA TEST")
    print_kappa(ct, alphabetsize=26, maximum=min(30, len(ct)))


def friedman_analysis(ct: str) -> None:
    """Run Friedman test for period detection."""
    print_header("FRIEDMAN TEST")
    friedman_test(ct, maxperiod=min(20, len(ct) // 3))


def repeat_analysis(ct: str) -> None:
    """Run repeat analysis."""
    print_header("REPEAT ANALYSIS")
    print_repeat_statistics(ct, minimum=2, maximum=6, alphabetsize=26)
    print()
    print_repeat_positions(ct, minimum=3, maximum=6)


def mixed_vigenere_tr(mixed_alphabet: Sequence[str]) -> pasc.TR[str]:
    """Build a Vigenere-like TR from a mixed alphabet.

    Each row is the mixed alphabet shifted by the position of the key letter.
    """
    tr: pasc.TR[str] = defaultdict(dict)
    n = len(mixed_alphabet)
    for i, key in enumerate(mixed_alphabet):
        for j, pt in enumerate(mixed_alphabet):
            tr[key][pt] = mixed_alphabet[(i + j) % n]
    return tr


def mixed_beaufort_tr(mixed_alphabet: Sequence[str]) -> pasc.TR[str]:
    """Build a Beaufort-like TR from a mixed alphabet."""
    tr: pasc.TR[str] = defaultdict(dict)
    n = len(mixed_alphabet)
    for i, key in enumerate(mixed_alphabet):
        for j, pt in enumerate(mixed_alphabet):
            tr[key][pt] = mixed_alphabet[(i - j) % n]
    return tr


def mixed_variant_beaufort_tr(mixed_alphabet: Sequence[str]) -> pasc.TR[str]:
    """Build a Variant Beaufort-like TR from a mixed alphabet."""
    tr: pasc.TR[str] = defaultdict(dict)
    n = len(mixed_alphabet)
    for i, key in enumerate(mixed_alphabet):
        for j, pt in enumerate(mixed_alphabet):
            tr[key][pt] = mixed_alphabet[(j - i) % n]
    return tr


def try_autokey_decrypt(
    ct: str,
    autokey_func: Callable[..., Any],
    tr: pasc.TR[str],
    label: str,
) -> list[tuple[float, str, str]]:
    """Try all single-letter primers for an autokey variant.

    Returns list of (score, primer, plaintext) sorted by score descending.
    """
    results: list[tuple[float, str, str]] = []
    for primer_char in ALPHABET:
        pt = "".join(autokey_func(ct, primer=primer_char, tr=tr))
        score = quadgramscore(pt)
        results.append((score, primer_char, pt))
    results.sort(key=lambda x: x[0], reverse=True)
    return results


def autokey_bruteforce_standard(ct: str) -> None:
    """Try all autokey variants with standard TRs and single-letter primers."""
    VIG = pasc.vigenere_tr(ALPHABET)
    BEA = pasc.beaufort_tr(ALPHABET)
    VAR = pasc.variantbeaufort_tr(ALPHABET)

    variants: list[tuple[str, Callable[..., Any], pasc.TR[str]]] = [
        ("Plaintext Autokey + Vigenere TR", auto.plaintext_autokey_decrypt, VIG),
        ("Plaintext Autokey + Beaufort TR", auto.plaintext_autokey_decrypt, BEA),
        ("Plaintext Autokey + Variant Beaufort TR", auto.plaintext_autokey_decrypt, VAR),
        ("Ciphertext Autokey + Vigenere TR", auto.ciphertext_autokey_decrypt, VIG),
        ("Ciphertext Autokey + Beaufort TR", auto.ciphertext_autokey_decrypt, BEA),
        ("Ciphertext Autokey + Variant Beaufort TR", auto.ciphertext_autokey_decrypt, VAR),
    ]

    all_results: list[tuple[float, str, str, str]] = []

    for label, decrypt_func, tr in variants:
        print_header(f"STANDARD AUTOKEY: {label}")
        results = try_autokey_decrypt(ct, decrypt_func, tr, label)
        for score, primer, pt in results[:3]:
            print(f"  Primer={primer}  score={score:8.2f}  PT={pt}")
            all_results.append((score, primer, pt, label))
        print()

    all_results.sort(key=lambda x: x[0], reverse=True)
    print_header("TOP 5 STANDARD TR RESULTS")
    for i, (score, primer, pt, label) in enumerate(all_results[:5]):
        ic = calc_ioc(pt)
        print(f"  #{i+1}  score={score:8.2f}  IOC={ic:.4f}  primer={primer}  {label}")
        print(f"     PT={pt}")
        print()


def autokey_bruteforce_keyword(ct: str) -> None:
    """Try autokey with keyword-based mixed alphabet TRs."""
    print_header("KEYWORD-BASED MIXED ALPHABET AUTOKEY SEARCH")
    print(f"Testing {len(KEYWORDS)} keywords x 3 TR types x 2 autokey types x 26 primers")
    print()

    all_results: list[tuple[float, str, str, str, str]] = []

    for keyword in KEYWORDS:
        mixed_al = masc.mixedalphabet(ALPHABET, keyword)

        tr_types: list[tuple[str, pasc.TR[str]]] = [
            ("Mixed Vigenere", mixed_vigenere_tr(mixed_al)),
            ("Mixed Beaufort", mixed_beaufort_tr(mixed_al)),
            ("Mixed Variant Beaufort", mixed_variant_beaufort_tr(mixed_al)),
        ]

        autokey_types: list[tuple[str, Callable[..., Any]]] = [
            ("PT Autokey", auto.plaintext_autokey_decrypt),
            ("CT Autokey", auto.ciphertext_autokey_decrypt),
        ]

        for tr_label, tr in tr_types:
            for ak_label, decrypt_func in autokey_types:
                for primer_char in ALPHABET:
                    pt = "".join(decrypt_func(ct, primer=primer_char, tr=tr))
                    score = quadgramscore(pt)
                    label = f"{ak_label} + {tr_label} (kw={keyword})"
                    all_results.append((score, primer_char, pt, label, keyword))

    all_results.sort(key=lambda x: x[0], reverse=True)
    print_header("TOP 20 KEYWORD-BASED RESULTS")
    for i, (score, primer, pt, label, keyword) in enumerate(all_results[:20]):
        ic = calc_ioc(pt)
        formatted = reconstruct_with_spaces(CIPHERTEXT_RAW, pt)
        print(f"  #{i+1:2d}  score={score:8.2f}  IOC={ic:.4f}  primer={primer}  {label}")
        print(f"       PT={pt}")
        print(f"       => {formatted}")
        print()


def autokey_bruteforce_keyword_2letter(ct: str) -> None:
    """Try keyword-based autokey with 2-letter primers for top keywords."""
    print_header("2-LETTER PRIMER + KEYWORD SEARCH (TOP KEYWORDS)")

    # First find the top keywords with 1-letter primers
    keyword_scores: dict[str, float] = {}
    for keyword in KEYWORDS:
        mixed_al = masc.mixedalphabet(ALPHABET, keyword)
        best = float("-inf")
        for tr_func in [mixed_vigenere_tr, mixed_beaufort_tr, mixed_variant_beaufort_tr]:
            tr = tr_func(mixed_al)
            for func in [auto.plaintext_autokey_decrypt, auto.ciphertext_autokey_decrypt]:
                for p in ALPHABET:
                    pt = "".join(func(ct, primer=p, tr=tr))
                    score = quadgramscore(pt)
                    if score > best:
                        best = score
        keyword_scores[keyword] = best

    # Take top 10 keywords
    top_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    print("Top keywords by single-letter primer score:")
    for kw, sc in top_keywords:
        print(f"  {kw:20s} best_score={sc:.2f}")
    print()

    all_results: list[tuple[float, str, str, str, str]] = []
    for keyword, _ in top_keywords:
        mixed_al = masc.mixedalphabet(ALPHABET, keyword)
        for tr_label, tr_func in [
            ("Mixed Vigenere", mixed_vigenere_tr),
            ("Mixed Beaufort", mixed_beaufort_tr),
            ("Mixed Variant Beaufort", mixed_variant_beaufort_tr),
        ]:
            tr = tr_func(mixed_al)
            for ak_label, decrypt_func in [
                ("PT Autokey", auto.plaintext_autokey_decrypt),
                ("CT Autokey", auto.ciphertext_autokey_decrypt),
            ]:
                for p1 in ALPHABET:
                    for p2 in ALPHABET:
                        primer = p1 + p2
                        pt = "".join(decrypt_func(ct, primer=primer, tr=tr))
                        score = quadgramscore(pt)
                        label = f"{ak_label} + {tr_label} (kw={keyword})"
                        all_results.append((score, primer, pt, label, keyword))

    all_results.sort(key=lambda x: x[0], reverse=True)
    print_header("TOP 20 RESULTS (2-LETTER PRIMER + KEYWORD)")
    for i, (score, primer, pt, label, keyword) in enumerate(all_results[:20]):
        ic = calc_ioc(pt)
        formatted = reconstruct_with_spaces(CIPHERTEXT_RAW, pt)
        print(f"  #{i+1:2d}  score={score:8.2f}  IOC={ic:.4f}  primer={primer:4s}  {label}")
        print(f"       PT={pt}")
        print(f"       => {formatted}")
        print()


def hill_climb_autokey(ct: str, iterations: int = 5000, restarts: int = 30) -> None:
    """Hill-climbing attack on scrambled-alphabet autokey cipher.

    Simultaneously optimizes the scrambled alphabet and primer letter
    by random swaps and scoring with quadgram fitness.
    """
    print_header("HILL-CLIMBING ATTACK ON SCRAMBLED ALPHABET AUTOKEY")
    print(f"Restarts: {restarts}, Iterations per restart: {iterations}")
    print()

    best_overall_score = float("-inf")
    best_overall_pt = ""
    best_overall_alpha = ""
    best_overall_primer = ""
    best_overall_label = ""

    autokey_types: list[tuple[str, Callable[..., Any]]] = [
        ("PT Autokey", auto.plaintext_autokey_decrypt),
        ("CT Autokey", auto.ciphertext_autokey_decrypt),
    ]

    tr_builders: list[tuple[str, Callable[..., pasc.TR[str]]]] = [
        ("Mixed Vigenere", mixed_vigenere_tr),
        ("Mixed Beaufort", mixed_beaufort_tr),
        ("Mixed Variant Beaufort", mixed_variant_beaufort_tr),
    ]

    for ak_label, decrypt_func in autokey_types:
        for tr_label, tr_builder in tr_builders:
            combo_label = f"{ak_label} + {tr_label}"
            combo_best_score = float("-inf")
            combo_best_pt = ""
            combo_best_alpha = ""
            combo_best_primer = ""

            for restart in range(restarts):
                # Start with a random alphabet
                alpha_list = list(ALPHABET)
                random.shuffle(alpha_list)
                current_alpha = "".join(alpha_list)

                # Find best primer for current alphabet
                tr = tr_builder(list(current_alpha))
                best_primer = "A"
                best_score = float("-inf")
                for p in ALPHABET:
                    pt = "".join(decrypt_func(ct, primer=p, tr=tr))
                    score = quadgramscore(pt)
                    if score > best_score:
                        best_score = score
                        best_primer = p

                current_score = best_score
                current_primer = best_primer

                for _iteration in range(iterations):
                    # Swap two random positions in the alphabet
                    new_alpha_list = list(current_alpha)
                    i, j = random.sample(range(26), 2)
                    new_alpha_list[i], new_alpha_list[j] = (
                        new_alpha_list[j],
                        new_alpha_list[i],
                    )
                    new_alpha = "".join(new_alpha_list)

                    tr = tr_builder(list(new_alpha))

                    # Try current primer and a few random ones
                    new_best_score = float("-inf")
                    new_best_primer = current_primer
                    for p in [current_primer] + random.sample(
                        list(ALPHABET), min(3, 26)
                    ):
                        pt = "".join(decrypt_func(ct, primer=p, tr=tr))
                        score = quadgramscore(pt)
                        if score > new_best_score:
                            new_best_score = score
                            new_best_primer = p

                    if new_best_score > current_score:
                        current_alpha = new_alpha
                        current_score = new_best_score
                        current_primer = new_best_primer

                if current_score > combo_best_score:
                    combo_best_score = current_score
                    combo_best_alpha = current_alpha
                    combo_best_primer = current_primer
                    tr = tr_builder(list(current_alpha))
                    combo_best_pt = "".join(
                        decrypt_func(ct, primer=current_primer, tr=tr)
                    )

            ic = calc_ioc(combo_best_pt) if combo_best_pt else 0.0
            formatted = reconstruct_with_spaces(CIPHERTEXT_RAW, combo_best_pt)
            print(f"  {combo_label}:")
            print(f"    Score:    {combo_best_score:.2f}  IOC={ic:.4f}")
            print(f"    Alphabet: {combo_best_alpha}")
            print(f"    Primer:   {combo_best_primer}")
            print(f"    PT:       {combo_best_pt}")
            print(f"    =>        {formatted}")
            print()

            if combo_best_score > best_overall_score:
                best_overall_score = combo_best_score
                best_overall_pt = combo_best_pt
                best_overall_alpha = combo_best_alpha
                best_overall_primer = combo_best_primer
                best_overall_label = combo_label

    print_header("BEST HILL-CLIMBING RESULT")
    formatted = reconstruct_with_spaces(CIPHERTEXT_RAW, best_overall_pt)
    ic = calc_ioc(best_overall_pt) if best_overall_pt else 0.0
    print(f"  Method:    {best_overall_label}")
    print(f"  Score:     {best_overall_score:.2f}  IOC={ic:.4f}")
    print(f"  Alphabet:  {best_overall_alpha}")
    print(f"  Primer:    {best_overall_primer}")
    print(f"  PT:        {best_overall_pt}")
    print(f"  =>         {formatted}")


def reconstruct_with_spaces(ct_raw: str, pt_stripped: str) -> str:
    """Reconstruct plaintext with original spacing and punctuation."""
    result = []
    pt_idx = 0
    for c in ct_raw:
        if c.upper() in ALPHABET:
            if pt_idx < len(pt_stripped):
                if c.islower():
                    result.append(pt_stripped[pt_idx].lower())
                else:
                    result.append(pt_stripped[pt_idx])
                pt_idx += 1
        else:
            result.append(c)
    return "".join(result)


def main() -> None:
    """Main analysis function."""
    ct = strip_to_alpha(CIPHERTEXT_RAW)

    print("Gorod Krovi Cipher 12 Analysis")
    print("Cipher type: 26-letter scrambled autokey")
    print(f"Ciphertext: {CIPHERTEXT_RAW}")

    # Phase 1: Basic statistics
    basic_statistics(ct)

    # Phase 2: Period detection
    kappa_analysis(ct)
    friedman_analysis(ct)

    # Phase 3: Repeat analysis
    repeat_analysis(ct)

    # Phase 4: Standard autokey brute force
    autokey_bruteforce_standard(ct)

    # Phase 5: Keyword-based mixed alphabet autokey
    autokey_bruteforce_keyword(ct)

    # Phase 6: 2-letter primers with top keywords
    autokey_bruteforce_keyword_2letter(ct)

    # Phase 7: Hill-climbing attack on scrambled alphabet
    hill_climb_autokey(ct, iterations=5000, restarts=30)


if __name__ == "__main__":
    main()
