#!/usr/bin/env python3

"""
Decode welcome message
"""

from aldegonde import c3301
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
) -> list[int]:
    """
    Plain Beaufort
    interruptors is list of positions where encryption (re)starts
    """
    output: list[int] = []
    keypos = 0
    azlen = 29
    keylen = len(primer)
    for pos in range(0, len(ciphertext)):
        if pos in interruptors:
            # output `F` rune and do not increase key position
            output.append(0)
        else:
            output.append((ciphertext[pos] + primer[keypos % keylen]) % azlen)
            keypos = keypos + 1
    return output


def beaufort_encrypt_interrupted(
    plaintext: list[int],
    primer: list[int] = [0],
    trace: bool = False,
) -> list[int]:
    """
    Plain Beaufort that interrupts on rune 0 in plaintext
    """
    output: list[int] = []
    keypos = 0
    azlen = 29
    keylen = len(primer)
    for pos in range(0, len(plaintext)):
        if plaintext[pos] == 0:
            # output `F` rune and do not increase key position
            output.append(0)
        else:
            output.append((plaintext[pos] - primer[keypos % keylen]) % azlen)
            keypos = keypos + 1
    return output


print(f"ciphertext: {welcome}")
ct = [c3301.r2i(e) for e in welcome]
# print(f"length: {len(seq)} runes")
# ioc.print_ioc_statistics(seq, alphabetsize=29)

pt = beaufort_decrypt_interrupted(
    ct, key, [48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514]
)

plaintext = "".join(c3301.i2r(i) for i in pt)

c3301.print_english(plaintext, limit=0)
ioc.print_ioc_statistics(plaintext, alphabetsize=29)

rct = beaufort_encrypt_interrupted(pt, key)

reciphertext = "".join(c3301.i2r(i) for i in rct)

print(f"reciphertext: {reciphertext}")

assert reciphertext == welcome
