#!/usr/bin/env python3

# IDEAS: steepest ascent (is practical? 28x27=756 evaluations)

import random
from collections.abc import Sequence
from typing import TypeVar

from simanneal import Annealer

from aldegonde import masc
from aldegonde.stats import compare, ngrams

T = TypeVar("T")

CIPHERTEXT = """D LKCJ QPFW DJK PC D JDLDXO MDI MDI DADO PQ PE D BDIR QPFW MKI QGW IWTWLLPKC DLQGKUJG QGW BWDQG EQDI GDE TWWC BWEQIKOWB PFNWIPDL QIKKNE GDYW BIPYWC QGW IWTWL MKIZWE MIKF QGWPI GPBBWC TDEW DCB NUIEUWB QGWF DZIKEE QGW JDLDXO WYDBPCJ QGW BIWDBWB PFNWIPDL EQDIMLWWQ D JIKUN KM MIWWBKF MPJGQWIE LWB TO LURW EROADLRWI GDE WEQDTLPEGWB D CWA EWZIWQ TDEW KC QGW IWFKQW PZW AKILB KM GKQG QGW WYPL LKIB BDIQG YDBWI KTEWEEWB APQG MPCBPCJ OKUCJ EROADLRWI GDE BPENDQZGWB QGKUEDCBE KM IWFKQW NIKTWE PCQK QGW MDI IWDZGWE KM ENDZW"""

AFFINE = """LREKMEPQOCPCBOYGYWPPEHFIWPFZYQGDZERGYPWFYWECYOJEQCMYEGFGYPWFCYMJ
YFGFMFGWPQGDZERGPGFFZEYCIEDBCGPFEHFBEFFERQCPJEEPQRODFEXFWCPOWPEWLY
ETERCBXGLLEREPFQGDZERFEHFBEFFERYXEDEPXGPSWPGFYDWYGFGWPGPFZEIEYYCSE"""

S = """JTQTIRVRBOZNVLBOTGWYZSBAFVPYZRNJAPEPVFATNLROMROSBAGNJRBONEBWJRJNVUTQQNVYBOJAREWJROMJBJZTOTTLSBARJNQSATLZRJYZYBYX"""

S2 = """Z XIAY NYBNXZQYP. Z XZFY WCY SCIIPCZQM PIVQN WCYO KBFY BP WCYO GXO RO.  NIVMXBP BNBKP"""

S9 = """TQJYZRCKX JIGC VR CIXVCK RQ HQ I BQR QP RLVENX, OZR JQXR QP RLC RLVENX RLCU JIGC VR CIXVCK RQ HQ HQER ECCH RQ OC HQEC.  IEHU KQQECU"""

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

CT = "".join(c for c in S9 if c in alphabet)


def startermapping(ciphertext: Sequence[str]) -> dict[str, str]:
    """find a good starting point based on unigram distribution"""
    dist: dict[str, int] = ngrams.ngram_distribution(ciphertext, length=1)
    # dist needs to be padded in case not all letters exist
    for e in set(compare.unigrams.keys()) - set(dist.keys()):
        dist[e] = 0

    sorted_unigrams: list[tuple[str, int]] = sorted(
        compare.unigrams.items(), key=lambda x: x[1],
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


class crack_with_simanneal(Annealer):
    """
    local class that uses simanneal
    """

    state: list[str]

    def move(self):
        """
        swap two letters
        """
        a, b = random.sample(range(len(self.state)), 2)
        self.state[a], self.state[b] = self.state[b], self.state[a]

    def energy(self):
        """
        calculate score
        """
        plaintext = "".join(masc.masc_decrypt(CT, pos2mapping(self.state, alphabet)))
        return -compare.quadgramscore(plaintext)


def solve_anneal(ciphertext: str) -> None:
    initial_state = mapping2pos(startermapping(ciphertext), alphabet)

    tsp = crack_with_simanneal(initial_state)
    tsp.copy_strategy = "slice"
    auto_schedule = tsp.auto(minutes=0.15)
    # {'tmin': ..., 'tmax': ..., 'steps': ...}
    print(auto_schedule)
    tsp.set_schedule(auto_schedule)

    # tsp.Tmax = 600
    # tsp.Tmin = 0.1
    # tsp.steps = 80000
    out, score = tsp.anneal()
    plaintext = "".join(masc.masc_decrypt(ciphertext, pos2mapping(out, alphabet)))
    print(out)
    print(score)
    print(plaintext)


if __name__ == "__main__":
    solve_anneal(CT)
