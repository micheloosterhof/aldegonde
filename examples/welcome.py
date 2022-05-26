#!/usr/bin/env python3

"""
Decode welcome message
"""

from aldegonde.structures import alphabet, sequence, cicada3301
from aldegonde.stats import ioc

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
    azlen = len(ciphertext.alphabet)
    keylen = len(primer)
    for pos in range(0, len(ciphertext)):
        if pos in interruptors:
            # output `F` rune and do not increase key position
            output.append(0)
        else:
            output.append((ciphertext[pos] + primer[keypos % keylen]) % azlen)
            keypos = keypos + 1
    return output


print(f"source: {welcome}")
seq = sequence.Sequence(welcome, alphabet=alphabet.CICADA_ALPHABET)
print(f"alphabet: {seq.alphabet}")
print(f"ciphertext: {seq.elements}")
print(f"length: {len(seq)} runes")
print(f"ioc={ioc.ioc(seq):.3f} nioc={ioc.normalized_ioc(seq):.3f}")

plain = beaufort_decrypt_interrupted(
    seq, key, [48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514]
)

cicada3301.english_output(plain, limit=0)
