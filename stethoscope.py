#!/usr/bin/env python3
# #pypy3

import math
import random

import gematria
import lp_section_data as lp

# import totient() method from sympy
# import sympy
# from sympy.ntheory.factor_ import totient, reduced_totient

from lib import *

import aldegonde

g = gematria.gematria

def first_letter_of_word():
    for i in [
        lp.section1,
        lp.section2,
        lp.section3,
        lp.section4,
        lp.section5,
        lp.section6,
        lp.section7,
        lp.section8,
        lp.section9,
        lp.section10,
        lp.section11,
        lp.section12,
        lp.section13,
    ]:
        firstrune = []
        for j in i["all_words"]:
            firstrune.append(j[0])
        print(firstrune)
        firstletter = []
        for r in firstrune:
            firstletter.append(g.rune_to_position_forward_dict[r])
        print(ioc(firstletter))


s1 = "".join(lp.section1["all_words"])
s2 = "".join(lp.section2["all_words"])
s3 = "".join(lp.section3["all_words"])
s4 = "".join(lp.section4["all_words"])
s5 = "".join(lp.section5["all_words"])
s6 = "".join(lp.section6["all_words"])
s7 = "".join(lp.section7["all_words"])
s8 = "".join(lp.section8["all_words"])
s9 = "".join(lp.section9["all_words"])
s10 = "".join(lp.section10["all_words"])
s11 = "".join(lp.section11["all_words"])
s12 = "".join(lp.section12["all_words"])
s13 = "".join(lp.section13["all_words"])
s = s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9 + s10 + s11 + s12 + s13
sl = list(s)
segments = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13]

# RL is a random rune list same size as all the other runes
rl = []
for i in range(0, len(s)):
    rl.append(random.randrange(0, MAX))

# rsegments are random lists, same size as the LP
rsegments = []
for i in segments:
    l = len(i)
    f = prime_factors(l)
    r = []
    for i in range(0, l):
        r.append(random.randrange(0, MAX))
    rsegments.append(r)

# GL are the runes in 0-28 format, in one big list
gl = []
for i in sl:
    gl.append(g.rune_to_position_forward_dict[i])

# SGL are the runes in 0-28 format by segment, list of a list by chapter
sgl = []
for i in segments:
    bgl = []
    for j in i:
        bgl.append(g.rune_to_position_forward_dict[j])
    sgl.append(bgl)

# for l in range(1,30):
#    gl = ciphertext_autokey_minuend_decrypt(gl,[1]*l)
#    print(l)
#    print(f"len {len(gl)} factors:{prime_factors(len(gl))}" )
#    print(f" ioc={ioc(gl):.3f}")
#    print(f" ioc2={ioc2(gl,cut=0):.3f} ioc2a={ioc2(gl,cut=1):.3f}, ioc2b={ioc2(gl,cut=2):.3f}")
#    print(f" ioc3={ioc3(gl,cut=0):.3f} ioc3a={ioc3(gl,cut=1):.3f}, ioc3b={ioc3(gl,cut=2):.3f}, ioc3c={ioc3(gl,cut=3):.3f}")
#    bigram_diagram(gl)
#    kappa(gl)
# exit(1)


def split_and_chi(ciphertext: list[int]):
    """
    split text in some way and run chi2 on splits with itself
    """
    print("### SPLIT AND CHI")
    spl = split_by_character(ciphertext)
    for s in range(0, MAX):
        for t in range(s, MAX):
            print(f"chi {s}-{t}: {chi(spl[s],spl[t])*MAX}")


def find_words_with_doublets():
    """
    find isomorphs containing doublets or long isomorphs
    """
    words = (
        lp.section1["all_words"]
        + lp.section2["all_words"]
        + lp.section3["all_words"]
        + lp.section4["all_words"]
        + lp.section5["all_words"]
        + lp.section6["all_words"]
        + lp.section7["all_words"]
        + lp.section8["all_words"]
        + lp.section9["all_words"]
        + lp.section10["all_words"]
        + lp.section11["all_words"]
        + lp.section12["all_words"]
        + lp.section13["all_words"]
    )
    isos = {}

    for word in words:
        numbers = []
        for rune in word:
            numbers.append(g.rune_to_position_forward_dict[rune])

        iso = isomorph(numbers)
        string = f"{word} {numbers}"
        if len(doublets(numbers)) > 0 or len(numbers) > 9:
            if iso in isos:
                isos[iso].append(string)
            else:
                isos[iso] = [string]

    for key in isos.keys():
        if len(isos[key]) > 2:
            for l in range(0, len(isos[key])):
                print(f"{key} {isos[key][l]}")


def find_words_before_single_rune():
    """
    find isomorphs containing doublets or long isomorphs
    """
    words = (
        lp.section1["all_words"]
        + lp.section2["all_words"]
        + lp.section3["all_words"]
        + lp.section4["all_words"]
        + lp.section5["all_words"]
        + lp.section6["all_words"]
        + lp.section7["all_words"]
        + lp.section8["all_words"]
        + lp.section9["all_words"]
        + lp.section10["all_words"]
        + lp.section11["all_words"]
        + lp.section12["all_words"]
        + lp.section13["all_words"]
    )

    prev = None
    print(f"A  word = ")
    counter = 0
    wc = 0
    sums = []
    diff1 = []
    diff2 = []
    for word in words:
        current = []
        for rune in word:
            current.append(g.rune_to_position_forward_dict[rune])
            counter += 1
        if len(current) == 1:
            print(
                f"c={counter%29:4d} sum={(prev[-1]+current[0])%29:02d} diff={(current[0]-prev[-1])%29:02d} diff={(prev[-1]-current[0])%29:02d} {prev[-1]:2d} {current[0]:2d} =  --  {prev} {current} ctr={counter}"
            )
            sums.append((prev[-1] + current[0]) % 29)
            diff1.append((prev[-1] - current[0]) % 29)
            diff2.append((current[0] - prev[-1]) % 29)
        prev = current

    print(dist(sums))
    print(dist(diff1))
    print(dist(diff2))


def analyze_segment(ciphertext: list[int]):
    print(f"ciphertext size {len(ciphertext)}")
    print(f"alphabet size {len(alphabet(ciphertext))}: {alphabet(ciphertext)}")
    print()
    print(f" ioc={ioc(ciphertext):.3f}")
    print(
        f" ioc2={ioc2(ciphertext,cut=0):.3f} ioc2a={ioc2(ciphertext,cut=1):.3f}, ioc2b={ioc2(ciphertext,cut=2):.3f}"
    )
    print(
        f" ioc3={ioc3(ciphertext,cut=0):.3f} ioc3a={ioc3(ciphertext,cut=1):.3f}, ioc3b={ioc3(ciphertext,cut=2):.3f}, ioc3c={ioc3(ciphertext,cut=3):.3f}"
    )
    # print(f" ioc4={ioc4(ciphertext,cut=0):.4f} ioc4a={ioc4(ciphertext,cut=1):.4f}, ioc4b={ioc4(ciphertext,cut=2):.4f}, ioc4c={ioc4(ciphertext,cut=4):.4f}")
    print()
    # print(f" repeats length 3: {repeat2(ciphertext,min=3,max=3)}")
    print(f" repeats length 4: {repeat2(ciphertext,min=4,max=4)}")
    print(f" repeats length 5: {repeat2(ciphertext,min=5,max=5)}")
    print(f" repeats length 6: {repeat2(ciphertext,min=6,max=6)}")
    print(f" repeats length 7: {repeat2(ciphertext,min=7,max=17)}")

    iso = repeat2(ciphertext, min=4, max=7)
    for k in iso.keys():
        for r in range(1, len(iso[k])):
            distance = iso[k][r] - iso[k][r - 1]
            factors = prime_factors(distance)
            print(f"{k} distance={distance} factors={factors} ", end="")
        print()

    bigram_diagram(ciphertext)

    print(f"len {len(ciphertext)} factors:{prime_factors(len(ciphertext))}")
    english_output(ciphertext, limit=20)

    # print("chi test")
    # for j in range(i,N):
    #     print(f"chi {i}-{j}: {chi(sgl[i],sgl[j])*MAX}")
    #    print(f"rand chi {i}-{j}: {chi(sgl[i],rsegments[j])*MAX}")

    print("doublet test")
    db = doublets(ciphertext, trace=True)
    print(db)
    # pattern_finder(db)

    print("kappa test")
    kappa(ciphertext)

    print("testing for vigenere")
    run_test3(ciphertext)

    print("plaintext and ciphertext autokey test")
    detect_plaintext_autokey(ciphertext, trace=False)
    detect_ciphertext_autokey_vigenere(ciphertext, trace=False)

    # print(f"#### segment {i+1} bruteforce autokey ######")
    # bruteforce_autokey(ciphertext,     maxkeylength=3)


print("Full liber primus")
analyze_segment(gl)
print("slice analysis")

N = len(sgl)
for i in range(0, N):
    gl = sgl[i]
    print(f"\n\n\n#### segment {i+1} ######")
    analyze_segment(gl)
