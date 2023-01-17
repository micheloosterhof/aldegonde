#!/usr/bin/env python3

"""
Decode welcome message
"""

from aldegonde.structures import alphabet, sequence, cicada3301
from aldegonde.stats import ioc, doublets

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


print(f"ciphertext: {welcome}")
seq = sequence.Sequence.fromstr(welcome, alphabet=cicada3301.CICADA_ALPHABET)
print(f"alphabet: {seq.alphabet}")
# print(f"ciphertext: {seq.data}")
print(f"length: {len(seq)} runes")
ioc.print_ioc_statistics(seq)

plain = beaufort_decrypt_interrupted(
    seq, key, [48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514]
)

plainseq = sequence.Sequence.fromlist(plain, alphabet=cicada3301.CICADA_ALPHABET)

doublets.print_doublets_statistics(plainseq)
ioc.print_ioc_statistics(plainseq)

cicada3301.print_english(plain, limit=0)
