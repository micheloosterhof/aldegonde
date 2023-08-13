#!/usr/bin/env python3

# solve simple vigenere
# IDEA: use threading

import random
from typing import TypeVar

from simanneal import Annealer

from aldegonde.stats import compare
from aldegonde import pasc

T = TypeVar("T")

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
VIG = """DAZFI SFSPA VQLSN PXYSZ WXALC DAFGQ UISMT PHZGA MKTTF TCCFX
KFCRG GLPFE TZMMM ZOZDE ADWVZ WMWKV GQSOH QSVHP WFKLS LEASE
PWHMJ EGKPU RVSXJ XVBWV POSDE TEQTX OBZIK WCXLW NUOVJ MJCLL
OEOFA ZENVM JILOW ZEKAZ EJAQD ILSWW ESGUG KTZGQ ZVRMN WTQSE
OTKTK PBSTA MQVER MJEGL JQRTL GFJYG SPTZP GTACM OECBX SESCI
YGUFP KVILL TWDKS ZODFW FWEAA PQTFS TQIRG MPMEL RYELH QSVWB
AWMOS DELHM UZGPG YEKZU KWTAM ZJMLS EVJQT GLAWV OVVXH KWQIL
IEUYS ZWXAH HUSZO GMUZQ CIMVZ UVWIF JJHPW VXFSE TZEDF"""
CT = "".join(c for c in VIG if c in alphabet)

TR = pasc.vigenere_tr(alphabet)
LEN = 14


class crack_with_simanneal(Annealer):
    """
    local class that uses simanneal
    """

    state: list[str]

    def move(self):
        """
        randomly change one letter
        """
        self.state[random.randrange(len(self.state))] = random.randrange(len(alphabet))

    def energy(self):
        """
        calculate score
        """
        keyword = [alphabet[i] for i in self.state]
        plaintext = "".join(pasc.pasc_decrypt(CT, keyword, TR))
        return -compare.quadgramscore(plaintext)


def solve_anneal(ciphertext: str) -> None:
    initial_state = [random.randrange(len(alphabet)) for idx in range(0, LEN)]

    tsp = crack_with_simanneal(initial_state)
    tsp.copy_strategy = "slice"
    auto_schedule = tsp.auto(minutes=0.1)
    # {'tmin': ..., 'tmax': ..., 'steps': ...}
    print(auto_schedule)
    tsp.set_schedule(auto_schedule)

    # tsp.Tmax = 600
    # tsp.Tmin = 0.1
    # tsp.steps = 80000
    out, score = tsp.anneal()
    keyword = [alphabet[i] for i in out]
    plaintext = "".join(pasc.pasc_decrypt(CT, keyword, TR))
    print(out)
    print(score)
    print(plaintext)


if __name__ == "__main__":
    solve_anneal(CT)
