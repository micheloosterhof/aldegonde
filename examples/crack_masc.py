#!/usr/bin/env python3

from collections.abc import Callable, Sequence
import random
import copy
from typing import NamedTuple, TypeVar

from aldegonde.stats import compare, ngrams
from aldegonde.algorithm import masc

T = TypeVar("T")

CIPHERTEXT = """D LKCJ QPFW DJK PC D JDLDXO MDI MDI DADO PQ PE D BDIR QPFW MKI QGW IWTWLLPKC DLQGKUJG QGW BWDQG EQDI GDE TWWC BWEQIKOWB PFNWIPDL QIKKNE GDYW BIPYWC QGW IWTWL MKIZWE MIKF QGWPI GPBBWC TDEW DCB NUIEUWB QGWF DZIKEE QGW JDLDXO WYDBPCJ QGW BIWDBWB PFNWIPDL EQDIMLWWQ D JIKUN KM MIWWBKF MPJGQWIE LWB TO LURW EROADLRWI GDE WEQDTLPEGWB D CWA EWZIWQ TDEW KC QGW IWFKQW PZW AKILB KM GKQG QGW WYPL LKIB BDIQG YDBWI KTEWEEWB APQG MPCBPCJ OKUCJ EROADLRWI GDE BPENDQZGWB QGKUEDCBE KM IWFKQW NIKTWE PCQK QGW MDI IWDZGWE KM ENDZW"""

AFFINE = """LREKMEPQOCPCBOYGYWPPEHFIWPFZYQGDZERGYPWFYWECYOJEQCMYEGFGYPWFCYMJ
YFGFMFGWPQGDZERGPGFFZEYCIEDBCGPFEHFBEFFERQCPJEEPQRODFEXFWCPOWPEWLY
ETERCBXGLLEREPFQGDZERFEHFBEFFERYXEDEPXGPSWPGFYDWYGFGWPGPFZEIEYYCSE"""

S = """JTQTIRVRBOZNVLBOTGWYZSBAFVPYZRNJAPEPVFATNLROMROSBAGNJRBONEBWJRJNVUTQQNVYBOJAREWJROMJBJZTOTTLSBARJNQSATLZRJYZYBYX"""

S2 = """Z XIAY NYBNXZQYP. Z XZFY WCY SCIIPCZQM PIVQN WCYO KBFY BP WCYO GXO RO.  NIVMXBP BNBKP"""

S9 = """TQJYZRCKX JIGC VR CIXVCK RQ HQ I BQR QP RLVENX, OZR JQXR QP RLC RLVENX RLCU JIGC VR CIXVCK RQ HQ HQER ECCH RQ OC HQEC.  IEHU KQQECU"""

VIG = """DAZFI SFSPA VQLSN PXYSZ WXALC DAFGQ UISMT PHZGA MKTTF TCCFX
KFCRG GLPFE TZMMM ZOZDE ADWVZ WMWKV GQSOH QSVHP WFKLS LEASE
PWHMJ EGKPU RVSXJ XVBWV POSDE TEQTX OBZIK WCXLW NUOVJ MJCLL
OEOFA ZENVM JILOW ZEKAZ EJAQD ILSWW ESGUG KTZGQ ZVRMN WTQSE
OTKTK PBSTA MQVER MJEGL JQRTL GFJYG SPTZP GTACM OECBX SESCI
YGUFP KVILL TWDKS ZODFW FWEAA PQTFS TQIRG MPMEL RYELH QSVWB
AWMOS DELHM UZGPG YEKZU KWTAM ZJMLS EVJQT GLAWV OVVXH KWQIL
IEUYS ZWXAH HUSZO GMUZQ CIMVZ UVWIF JJHPW VXFSE TZEDF"""

CT = S9.replace(" ", "").replace(",", "").replace(".", "").replace("\n", "")

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def take_step(pos: list[int]) -> list[int]:
    """take small step by shuffling 2 vars"""
    idx = range(len(pos))
    i1, i2 = random.sample(idx, 2)
    pos[i1], pos[i2] = pos[i2], pos[i1]
    return pos


def startermapping(ciphertext: Sequence[str]) -> dict[str, str]:
    """find a good starting point based on unigram distribution"""
    dist: dict[str, int] = ngrams.ngram_distribution(ciphertext, length=1)
    # dist needs to be padded in case not all letters exist
    for e in set(compare.unigrams.keys()) - set(dist.keys()):
        dist[e] = 0

    sorted_unigrams: list[tuple[str, int]] = sorted(
        compare.unigrams.items(), key=lambda x: x[1]
    )
    sorted_ngrams: list[tuple[str, int]] = sorted(dist.items(), key=lambda x: x[1])
    assert len(sorted_unigrams) == len(sorted_ngrams)

    key: dict[str, str] = {}
    for i, e in enumerate(sorted_unigrams):
        key[e[0]] = sorted_ngrams[i][0]

    return key


def pos2mapping(pos: Sequence[int], alphabet: Sequence[T]) -> dict[T, T]:
    """turn position list into mapping dictionary"""
    mapping: dict[T, T] = {}
    for i in range(len(alphabet)):
        mapping[alphabet[i]] = alphabet[pos[i]]
    return mapping


def mapping2pos(mapping: dict[T, T], alphabet: Sequence[T]) -> list[int]:
    """turn mapping dict into position list"""
    pos: list[int] = []
    for i in range(len(alphabet)):
        pos.append(alphabet.index(mapping[alphabet[i]]))
    return pos


def scorer(pos: Sequence[int]) -> float:
    """scorer function"""
    dec = masc.masc_decrypt(CT, pos2mapping(pos, alphabet))
    score = float(compare.quadgramscore(dec))
    return score


"""Automated breaking of the Simple Substitution Cipher."""


class Decryption(NamedTuple):
    plaintext: str
    node: Sequence[int]
    node_score: float


def crack(ciphertext, *fitness_functions, ntrials=6, nswaps=300):
    """Break ``ciphertext`` using hill climbing.

    Note:
        Currently ntrails and nswaps default to magic numbers.
        Generally the trend is, the longer the text, the lower the number of trials
        you need to run, because the hill climbing will lead to the best answer faster.
        Because randomness is involved, there is the possibility of the correct decryption
        not being found. In this circumstance you just need to run the code again.

    Example:
        >>> decryptions = crack("XUOOB", fitness.english.quadgrams)
        >>> print(decryptions[0])
        HELLO

    Args:
        ciphertext (str): The text to decrypt
        *fitness_functions (variable length argument list): Functions to score decryption with

    Keyword Args:
        ntrials (int): The number of times to run the hill climbing algorithm
        nswaps (int): The number of rounds to find a local maximum

    Returns:
        Sorted list of decryptions

    Raises:
        ValueError: If nswaps or ntrails are not positive integers
        ValueError: If no fitness_functions are given
    """
    if ntrials <= 0 or nswaps <= 0:
        raise ValueError("ntrials and nswaps must be positive integers")

    # starter node can be based on english frequencies E, T, A, O, I, N, S, R, H, and L.
    starter_node = mapping2pos(startermapping(ciphertext), alphabet)
    # starter_node = list(range(0, 26))

    # Find a local maximum by swapping two letters and scoring the decryption
    def next_node_inner_climb(node: list[int]) -> tuple[list[int], float, Decryption]:
        # Swap 2 characters in the key
        a, b = random.sample(range(len(node)), 2)
        node[a], node[b] = node[b], node[a]
        plaintext = "".join(masc.masc_decrypt(CT, pos2mapping(node, alphabet)))
        node_score = compare.quadgramscore(plaintext)
        # node_score = score(plaintext, *fitness_functions)
        return node, node_score, Decryption(plaintext, node, node_score)

    # Outer climb reruns hill climb ntrials number of times each time at a different start location
    def next_node_outer_climb(node: list[int]) -> tuple[list[int], float, Decryption]:
        # random.shuffle(node)
        key, best_score, outputs = hill_climb(nswaps, node[:], next_node_inner_climb)
        print("*", end="")
        return (
            key,
            best_score,
            outputs[-1],
        )  # The last item in this list is the item with the highest score

    _, _, decryptions = hill_climb(ntrials, starter_node, next_node_outer_climb)
    return sorted(
        decryptions, reverse=True
    )  # We sort the list to ensure the best results are at the front of the list


"""Algorithms for searching and optimisation."""


def hill_climb(
    nsteps: int, start_node: list[int], get_next_node: Callable
) -> tuple[list[int], float, list[Decryption]]:
    """Modular hill climbing algorithm.

    Example:
        >>> def get_next_node(node):
        ...     a, b = random.sample(range(len(node)), 2)
        ...     node[a], node[b] = node[b], node[a]
        ...     plaintext = decrypt(node, ciphertext)
        ...     score = lantern.score(plaintext, *fitness_functions)
        ...     return node, score, Decryption(plaintext, ''.join(node), score)
        >>> final_node, best_score, outputs = hill_climb(10, "ABC", get_next_node)

    Args:
        nsteps (int): The number of neighbours to visit
        start_node: The starting node
        get_next_node (function): Function to return the next node
            the score of the current node and any optional output from the current node

    Returns:
        The highest node found, the score of this node and the outputs from the best nodes along the way
    """
    outputs = []
    best_score = -float("inf")

    for _step in range(nsteps):
        next_node, score, output = get_next_node(
            copy.deepcopy(start_node)
        )  # this must be deepcopy

        # Keep track of best score and the start node becomes finish node
        if score > best_score:
            # start_node = copy.deepcopy(next_node)
            start_node = next_node  # shallow copy should be sufficcient
            best_score = score
            outputs.append(output)

    return start_node, best_score, outputs


def climb():
    print(f"ciphertext: {CT}")
    print(f"ciphertext score: {compare.trigramscore(CT)}")

    out = crack(CT, scorer, ntrials=30, nswaps=5000)
    print()

    for e in sorted(out, key=lambda x: x.node_score):
        print(f"{e.node_score:.5f}: {e.plaintext}")


if __name__ == "__main__":
    climb()
