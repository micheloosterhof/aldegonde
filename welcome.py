#!/usr/bin/env python3

"""
Decode welcome message
"""

import gematria

import aldegonde as ag

from aldegonde.structures import alphabet, sequence, cicada3301
from aldegonde.stats import ioc

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
MAX = 29

def beaufort_decrypt_interrupted(
    ciphertext: list[int],
    primer: list[int] = [0],
    interruptors: list[int] = [],
    trace: bool = False,
):
    """
    Plain Beaufort
    interruptors is list of positions where encryption (re)starts
    """
    output: list[int] = []
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

print(f"{welcome}")
seq = sequence.Sequence(welcome, alphabet=alphabet.CICADA_ALPHABET)
print(f"{seq}")

print(f"length: {len(runes)} runes")
print(f"alphabet size: {len(alphabet.alphabet(runes))}: {alphabet.alphabet(runes)}")
print(f"ioc={ioc.normalized_ioc(runes):.3f}")

plain = beaufort_decrypt_interrupted(
    runes, key, [48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514]
)

cicada3301.english_output(plain, limit=0)
