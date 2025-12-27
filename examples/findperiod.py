#!/usr/bin/env python3

from typing import TypeVar

from aldegonde.analysis import friedman, twist
from aldegonde.stats import kappa, repeats

T = TypeVar("T")

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ZBAROL = "THZBAROLASYZFKHFNYCEYXOQMWHXLELXLAUHNPMIAZTLVDWNNHRDOWSIHUCCMGNTTTCWSIHUCCMHTEEDCBUGMHZBAROLTSONNSHUDWQFZXRPNABMHTZDPRYHUCMMNTWADUBUKAOCCMUKELRSDREHULXIAYPECDPNZROFVTRTWOCCMUKLAWGILYHNLCBRGWYNYCEYXTLVSGUFIDDMEKW"

MAD1 = "BUHMKLRASCKBLRZQQHRZMVVZBZLXWBNHOMKKEBTQWTUEMPLWLBQAGIUWSFSFVPLHBVPHGXVOHYPMQWSCQAGXEMCHVFWQRJXXRUMLLVFTLTLDPMPNEIQQPVYYAGLXRBVRRZQCKIOBUHFBAGZEVBBXWBBUHMKLRASCKBLRZQQHRZMGRJFVQWLBXRUMLLVVXLKHWXEMPLTEMEWIUBVQXLAYLGBANQHXDRUEDMGKIFWPRJQPRVPFKRVMCBUHESMEDKBQBFMPKYRWBBBWLXBBIIKOYLWEBUHRQPRQYJJRUSCAYLGBAVVPFSROCQWOHXEMCHVFWQ"

CT = MAD1.replace(" ", "").replace(",", "").replace(".", "").replace("\n", "")


def findperiod(ciphertext):
    """
    bruteforce all shifts
    """
    kappa.print_kappa(ciphertext, alphabetsize=29, trace=True)
    friedman.friedman_test(ciphertext, maxperiod=34)
    twist.twist_test(ciphertext, maxperiod=34)
    repeats.print_repeat_statistics(ciphertext, minimum=2)
    repeats.print_repeat_positions(ciphertext, minimum=5)


if __name__ == "__main__":
    findperiod(CT)
