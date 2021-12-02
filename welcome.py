#!/usr/bin/env pypy3

from typing import Dict, List
import gematria
from lib import *

g = gematria.gematria

welcome = "ᚢᛠᛝᛋᛇᚠᚳᚱᛇᚢᚷᛈᛠᛠᚠᚹᛉᛏᚳᛚᛠᚣᛗᛠᛇᛏᚳᚾᚫᛝᛗᛡᛡᛗᛗᚹᚫᛈᛞᛝᛡᚱᚩᛠᛡᛗᛁᚠᚠᛖᚢᛝᛇᚢᚫᚣᛈᚱᚫᛁᛈᚫᚳᚫᚫᚾᚹᛒᛉ\
ᛗᛞᚱᛡᛁᚠᛈᚳᛇᛇᚫᚳᚱᚦᛈᚠᛄᛗᚩᛇᚳᚹᛡᛒᚫᚹᛒᛠᛚᛋᚱᚣᛄᚫᚱᛗᚳᚦᛇᚫᛏᚳᛈᚹᛗᚷᛇᚳᛝᛈᚢᛇᚳᚱᛖᚹᛡᛈᛁᛒᚣᛒᛉᚠᛚᛁᚱᚱᛗᚳ\
ᚷᛒᚣᚱᚳᚠᚢᚦᛈᛡᛄᚹᛏᚠᛠᛄᚷᛒᚫᚦᚠᚠᛠᛈᚦᛈᚠᚪᛉᛄᛗᛖᛈᛝᛋᚩᛋᛗᚹᛇᛄᛚᚹᛉᚢᚦᚫᚹᛗᚦᛞᚣᛄᚳᛋᛡᛉᚩᛝᚱᛗᛒᚹᚱᛗᛁᛞᚣᛄᚳ\
ᛉᚻᚢᚣᛈᛚᛄᛝᚣᛗᚠᛄᛈᛇᚢᛡᚹᛇᛄᛞᚹᛉᚢᚪᛚᚪᛋᛗᛡᛇᛉᚫᛗᛡᛗᛁᛈᚣᚫᛗᚢᚠᛗᚣᚣᛇᚫᛉᚱᛄᛋᛖᛖᚹᚾᛞᛄᚢᛋᛉᚣᛏᛖᛏᛗᛇᚱᚣᛞᛋ\
ᚾᛖᚫᛞᛡᛈᛒᚢᚾᛠᛝᛄᛡᚫᛄᚷᛒᛈᚦᛉᛈᚾᚹᚹᛁᛚᛗᚫᛚᛈᛒᚢᚩᛠᛡᚱᛡᛠᚠᚱᚱᛇᛄᛗᚱᛗᛁᛞᚣᛄᚻᛚᚠᚢᛄᚢᛡᛚᚦᛠᛇᛄᚩᛇᚱᚱᛗᚢᛗᛋ\
ᚳᛠᛇᛚᛁᚫᚫᚳᛚᚹᛁᛚᛏᛈᛖᚢᛈᛠᛡᛈᚦᛏᛒᛏᛗᛖᚢᛚᚩᛚᛖᛇᛄᛈᚢᛠᛚᚳᚷᛠᚷᛋᛡᛏᛗᛒᛗᚱᚦᚠᛈᚹᚱᛄᚱᛉᚳᛝᛄᛠᛟᛄᛖᚣᛗᛞᚣᛄᚳᚫ\
ᛡᚢᚠᛈᚠᚪᚳᚳᛠᚱᚢᛄᚱᚪᛗᛒᛈᚷᛈᛒᚢᚾᛠᛝᚠᚾᛉᛖᚣᚷᛁᛠᛝᚢᛗᛏᚳᚷᛠᛠᛄᚫᛒᛈᚹᛞᚠᚣᛉᚫᚢᚠᛇᛄᛈᛉᛚᚦᛠᚪᛚᚦᚳᚣᚢᛡᚳᛖᛚᚫ\
ᛇᛁᛉᚦᛋᚫᚻᚫᚦᚣᚠᛚᚳᛖᚱᛈᚠᚪᛉᚱᛒᛖᚫᚳᛒᚠ"

key = [6, 19, 28, 19, 20, 19, 13, 3]


def beaufort_decrypt_interrupted(
    ciphertext: List[int],
    primer: List[int] = [0],
    interruptors: List[int] = [],
    trace: bool = False,
):
    """
    Plain Beaufort
    interruptors is list of positions where encryption (re)starts
    """
    output: List[int] = []
    keypos = 0
    keylen = len(primer)
    for pos in range(0, len(ciphertext)):
        if pos in interruptors:
            # output `F` rune and do not increase key position
            output.append(0)
        else:
            output.append((ciphertext[pos] + primer[keypos % keylen]) % MAX)
            keypos = keypos + 1
    return output


runes = []
for r in welcome:
    runes.append(g.rune_to_position_forward_dict[r])

print(f"runes size {len(runes)}")
print(f"alphabet size {len(alphabet(runes))}: {alphabet(runes)}")
print(f"ioc={ioc(runes):.3f}")
print(
    f"ioc2={ioc2(runes,cut=0):.3f} ioc2a={ioc2(runes,cut=1):.3f}, ioc2b={ioc2(runes,cut=2):.3f}"
)
print(
    f"ioc3={ioc3(runes,cut=0):.3f} ioc3a={ioc3(runes,cut=1):.3f}, ioc3b={ioc3(runes,cut=2):.3f}, ioc3c={ioc3(runes ,cut=3):.3f}"
)

detect_vigenere(runes, trace=True)

plain = beaufort_decrypt_interrupted(
    runes, key, [48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514]
)

english_output(plain, limit=0)
