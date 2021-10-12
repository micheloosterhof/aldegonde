from collections import Counter, defaultdict
import math
import random
import sys
from typing import Dict, List

import gematria
import lp_section_data as lp

g = gematria.gematria

# There are 29 runes. Generally counted 0-28
MAX = 29


class colors:
    reset = "\033[0m"

    # Black
    fgBlack = "\033[30m"
    fgBrightBlack = "\033[30;1m"
    bgBlack = "\033[40m"
    bgBrightBlack = "\033[40;1m"

    # Red
    fgRed = "\033[31m"
    fgBrightRed = "\033[31;1m"
    bgRed = "\033[41m"
    bgBrightRed = "\033[41;1m"

    # Green
    fgGreen = "\033[32m"
    fgBrightGreen = "\033[32;1m"
    bgGreen = "\033[42m"
    bgBrightGreen = "\033[42;1m"

    # Yellow
    fgYellow = "\033[33m"
    fgBrightYellow = "\033[33;1m"
    bgYellow = "\033[43m"
    bgBrightYellow = "\033[43;1m"

    # Blue
    fgBlue = "\033[34m"
    fgBrightBlue = "\033[34;1m"
    bgBlue = "\033[44m"
    bgBrightBlue = "\033[44;1m"

    # Magenta
    fgMagenta = "\033[35m"
    fgBrightMagenta = "\033[35;1m"
    bgMagenta = "\033[45m"
    bgBrightMagenta = "\033[45;1m"

    # Cyan
    fgCyan = "\033[36m"
    fgBrightCyan = "\033[36;1m"
    bgCyan = "\033[46m"
    bgBrightCyan = "\033[46;1m"

    # White
    fgWhite = "\033[37m"
    fgBrightWhite = "\033[37;1m"
    bgWhite = "\033[47m"
    bgBrightWhite = "\033[47;1m"


def isomorph(
    ciphertext: List[int], min: int = 2, max: int = 10
):  # -> Dict(List[int], int):
    """
    Find repeating sequences in the list, up to `max`. Max defaults to 10
    Returns dictionary with as key the sequence as a string, and as value the number of occurences
    """
    sequences = {}
    for length in range(min, max + 1):
        l = []
        for index in range(0, len(ciphertext) - length):
            k = "-".join([str(x) for x in ciphertext[index : index + length]])
            l.append(k)
        f = Counter(l)
        for k in f.keys():
            if f[k] > 1:
                sequences[k] = f[k]

    return sequences


def trigrams(runes: List[int]):
    """
    get the trigrams
    """
    return isomorph(runes, min=3, max=3)


def quadgrams(runes: List[int]):
    """
    get the quadgrams
    """
    return isomorph(runes, min=4, max=4)


def isomorph2(
    ciphertext: List[int], min: int = 2, max: int = 10
):  # -> Dict(List[int], int):
    """
    Find repeating sequences in the list, up to `max`. Max defaults to 10
    Returns dictionary with as key the sequence as a string, and as value the list of starting positions of that substring
    """
    sequences = {}
    for length in range(min, max + 1):
        l = {}
        for index in range(0, len(ciphertext) - length):
            k = "-".join([str(x) for x in ciphertext[index : index + length]])
            if k in l.keys():
                l[k].append(index)
            else:
                l[k] = [index]

        for k in l.keys():
            if len(l[k]) > 1:
                sequences[k] = l[k].copy()

    return sequences


def find(sequence: List[int], runes: List[int]) -> List[int]:
    """
    find `sequence` inside the list of `runes`, return array with indexes
    """
    N = len(runes)
    results = []
    for index in range(0, N - len(sequence)):
        if sequence == runes[index : index + len(sequence)]:
            results.append(index)
    return results


def triplets(runes: List[int]) -> int:
    """
    find number of triplet. triplet is X followed by XX for any X
    """
    N = len(runes)
    triplets: int = 0
    for index in range(0, N - 2):
        if runes[index] == runes[index + 1] and runes[index] == runes[index + 2]:
            triplets += 1
    print(f"triplets = {triplets}")
    expected = N / MAX / MAX
    print(f"expected = {expected:.2f}")
    return triplets


def doublets(runes: List[int], skip: int = 1) -> int:
    """
    find number of doublets. doublet is X followed by X for any X
    """
    N = len(runes)
    doublets: int = 0
    for index in range(0, N - skip):
        if runes[index] == runes[index + skip]:
            doublets += 1
    expected: float = N / MAX
    sigmage = abs(doublets - expected) / math.sqrt(expected)
    print(f"doublets={doublets} expected={N/MAX:.2f} σ={sigmage:.2f}")
    return doublets


def dist(runes: List[int]) -> str:
    """
    print frequency distribution
    """
    N = len(runes)
    freqs = Counter(runes)
    print("frequency distribution")
    for rune in range(0, MAX):
        print(f"{rune}: {freqs[rune]/N*100}")


def ioc(runes: List[int]) -> float:
    """
    Input is a list of integers, from 0 to MAX-1
    Output is the Index of Coincidence formatted as a float, normalized to to alphabet size
    """
    N = len(runes)
    if N < 2:
        return 0
    freqs = Counter(runes)
    freqsum = 0.0
    for rune in range(0, MAX):
        freqsum += freqs[rune] * (freqs[rune] - 1)
    IC = freqsum / (N * (N - 1)) * MAX
    return IC
    # return "{0:.3f}".format(IC)


def ioc2(runes: List[int], cut: int = 0) -> float:
    """
    digraph ioc - This IOC calculation runs on pairs of runes

    Input is a list of integers, with values from 0 to MAX-1
    Output is the Index of Coincidence formatted as a float, normalized to to alphabet size

    Specify `cut=0` and it will operate on sliding blocks of 2 runes: AB, BC, CD, DE
    Specify `cut=1` and it will operate on non-overlapping blocks of 2 runes: AB, CD, EF
    Specify `cut=2` and it will operate on non-overlapping blocks of 2 runes: BC, DE, FG
    """
    if cut == 0:
        l: list = []
        for i in range(0, len(runes) - 1):
            l.append(f"{runes[i]}-{runes[i+1]}")
        freqs = Counter(l)
        freqsum = 0.0
        for r in freqs.keys():
            freqsum += freqs[r] * (freqs[r] - 1)
        IC = freqsum / (len(l) * (len(l) - 1)) * MAX * MAX
    elif cut == 1 or cut == 2:
        l: list = []
        for i in range(cut, len(runes) - 1, 2):
            l.append(f"{runes[i]}-{runes[i+1]}")
        freqs = Counter(l)
        freqsum = 0.0
        for r in freqs.keys():
            freqsum += freqs[r] * (freqs[r] - 1)
        IC = freqsum / (len(l) * (len(l) - 1)) * MAX * MAX
    else:
        raise Exception

    return IC


def ioc3(runes: List[int], cut: int = 0) -> float:
    """
    trigraph ioc - This IOC calculation runs on three runes

    Input is a list of integers, with values from 0 to MAX-1
    Output is the Index of Coincidence formatted as a float, normalized to to alphabet size

    Specify `cut=0` and it will operate on sliding blocks of 2 runes: ABC, BCD, CDE, ...
    Specify `cut=1` and it will operate on non-overlapping blocks of 2 runes: ABC, DEF, ...
    Specify `cut=2` and it will operate on non-overlapping blocks of 2 runes: BCD, EFG, ...
    Specify `cut=3` and it will operate on non-overlapping blocks of 2 runes: CDE, FGH, ...
    """
    if cut == 0:
        l: list = []
        for i in range(0, len(runes) - 2):
            l.append(f"{runes[i]}-{runes[i+1]}-{runes[i+2]}")
        freqs = Counter(l)
        freqsum = 0.0
        for r in freqs.keys():
            freqsum += freqs[r] * (freqs[r] - 1)
        IC = freqsum / (len(l) * (len(l) - 1)) * MAX * MAX * MAX
    elif cut == 1 or cut == 2 or cut == 3:
        l: list = []
        for i in range(cut, len(runes) - 2, 2):
            l.append(f"{runes[i]}-{runes[i+1]}-{runes[i+2]}")
        freqs = Counter(l)
        freqsum = 0.0
        for r in freqs.keys():
            freqsum += freqs[r] * (freqs[r] - 1)
        IC = freqsum / (len(l) * (len(l) - 1)) * MAX * MAX * MAX
    else:
        raise Exception
    return IC


def chi(text1: List[int], text2: List[int]) -> float:
    """
    Calculate chi test of 2 texts
    """
    N1 = len(text1)
    N2 = len(text2)
    freqs1 = Counter(text1)
    freqs2 = Counter(text2)
    sum: float = 0.0
    for rune in range(0, MAX - 1):
        sum += freqs1[rune] * freqs2[rune] / (N1 * N2)
    return sum


def banbury(runes: List[int]) -> None:
    """
    Banbury test. Overlay text with itself, count number of same characters
    Output is printed
    """
    print("banbury")
    N: int = len(runes)
    for offset in range(1, N - 50):
        matches = 0
        for i in range(0, N - offset):
            if runes[i] == runes[i + offset]:
                matches += 1
        print(f"offset: {offset} matches {matches}")


def kappa(ciphertext: List[int], max: int = 51) -> None:
    """
    kappa test
    max -> max offset. if
    """
    if max == 0:
        max = int(len(ciphertext) / 2)
    for a in range(1, max):
        counter = 0
        dups = 0
        for i in range(0, len(ciphertext) - a):
            counter = counter + 1
            if ciphertext[i] == ciphertext[i + a]:
                dups = dups + 1
        print(f"offset={a}, dups={dups}, ioc={dups/counter*MAX:.3f}")


def bigram_diagram(runes: List[int]) -> None:
    """
    Input is a list of integers, from 0 to MAX-1
    Output is the bigram frequency diagram printed to stdout
    """
    count = Counter(runes)
    ioc = 0.0
    res = Counter(
        "{:02d}-{:02d}".format(runes[idx], runes[idx + 1])
        for idx in range(len(runes) - 1)
    )
    bigram = defaultdict(dict)

    for i in res.keys():
        x, y = i.split("-")
        bigram[int(x)][int(y)] = res[i]

    print(
        "   | 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 | IOC"
    )
    print(
        "---+----------------------------------------------------------------------------------------+----"
    )

    # for i in sorted(bigram.keys()):
    for i in range(0, MAX):
        print(f"{i:02} | ", end="")
        for j in range(0, MAX):
            # for j in sorted(bigram[i]):
            try:
                v = bigram[i][j]
            except:
                v = 0
            if v == 0:
                print(colors.bgRed, end="")
            elif v < 5:
                print(colors.bgBlue, end="")
            print(f"{v:02}", end="")
            print(colors.reset, end=" ")

        # partial IOC (one rune), and total IOC
        pioc = (
            (count[int(i)] * (count[int(i)] - 1))
            / (len(runes) * (len(runes) - 1))
            * MAX
        )
        ioc += pioc
        print("| {0:.3f}".format(pioc))

    print(
        "--------------------------------------------------------------------------------------------+----"
    )
    print(
        "                                                                                            | {0:.3f}".format(
            ioc
        )
    )
    print("\n")


def bigram_diagram_skip(runes: List[int], skip: int = 1) -> None:
    """
    Input is a list of integers, from 0 to MAX-1
    Output is the bigram frequency diagram printed to stdout
    """
    count = Counter(runes)
    ioc = 0.0
    res = Counter(
        "{:02d}-{:02d}".format(runes[idx], runes[idx + skip])
        for idx in range(len(runes) - skip)
    )
    bigram = defaultdict(dict)

    for i in res.keys():
        x, y = i.split("-")
        bigram[int(x)][int(y)] = res[i]

    print(
        "   | 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 | IOC"
    )
    print(
        "---+----------------------------------------------------------------------------------------+----"
    )

    # for i in sorted(bigram.keys()):
    for i in range(0, MAX):
        print(f"{i:02} | ", end="")
        for j in range(0, MAX):
            # for j in sorted(bigram[i]):
            try:
                v = bigram[i][j]
            except:
                v = 0
            if v == 0:
                print(colors.bgRed, end="")
            elif v < 5:
                print(colors.bgBlue, end="")
            print(f"{v:02}", end="")
            print(colors.reset, end=" ")

        # partial IOC (one rune), and total IOC
        pioc = (
            (count[int(i)] * (count[int(i)] - 1))
            / (len(runes) * (len(runes) - 1))
            * MAX
        )
        ioc += pioc
        print("| {0:.3f}".format(pioc))

    print(
        "--------------------------------------------------------------------------------------------+----"
    )
    print(
        "                                                                                            | {0:.3f}".format(
            ioc
        )
    )
    print("\n")


def split_by_period(ciphertext: List[int], period: int) -> List[List[int]]:
    """
    split functions, split by position
    """
    alphabet = {}
    for i in range(0, period):
        alphabet[i] = []
    for i in range(0, len(ciphertext) - 1):
        alphabet[ciphertext[i] % period].append(ciphertext[i])
    return alphabet


def split_by_character(ciphertext: List[int]) -> Dict[int, List[int]]:
    """
    by previous character
    """
    alphabet = {}
    for i in range(0, MAX):
        alphabet[i] = []
    for i in range(0, len(ciphertext) - 2):
        alphabet[ciphertext[i]].append(ciphertext[i + 1])

    # for i in alphabet.keys():
    #    #bigram_diagram(alphabet[i])
    #    print("key={}: ioc of runes following {} = {}".format(a, i, ioc(alphabet[i])))
    return alphabet


# ciphertext autokey variations
# we can do 3 operations, 2 subtractions and 1 addition, addition=vigenere, subtraction=beaufort, minuend
# C=P+K C=P-K, C=K-P


def ciphertext_autokey_vigenere_encrypt(
    plaintext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Vigenere primitive without any console output, C=P+K
    """
    key: List[int] = primer.copy()
    output: List[int] = []
    for j in range(0, len(plaintext)):
        c = (plaintext[j] + key[j] + MAX) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_vigenere_decrypt(
    ciphertext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Vigenere primitive without any console output, P=C-K
    """
    key: List[int] = primer + ciphertext
    output: List[int] = []
    for j in range(0, len(ciphertext)):
        output.append((ciphertext[j] - key[j] + MAX) % MAX)
    return output


def ciphertext_autokey_minuend_encrypt(
    plaintext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Minuend primitive without any console output, C=K-P
    """
    key: List[int] = primer.copy()
    output: List[int] = []
    for j in range(0, len(plaintext)):
        c = (key[j] - plaintext[j] + MAX) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_minuend_decrypt(
    ciphertext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Minuend primitive without any console output, P=K-C
    """
    key: List[int] = primer + ciphertext
    output: List[int] = []
    for j in range(0, len(ciphertext)):
        output.append((key[j] - ciphertext[j] + MAX) % MAX)
    return output


def ciphertext_autokey_beaufort_encrypt(
    plaintext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Beafort primitive without any console output, C=P-K
    """
    key: List[int] = primer.copy()
    output: List[int] = []
    for j in range(0, len(plaintext)):
        c = (plaintext[j] - key[j] + MAX) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_beaufort_decrypt(
    ciphertext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Beafort primitive without any console output, P=C+K
    """
    key: List[int] = primer + ciphertext
    output: List[int] = []
    for j in range(0, len(ciphertext)):
        output.append((ciphertext[j] + key[j] + MAX) % MAX)
    return output


# plaintext autokey variations
# we can do 3 operations, 2 subtractions and 1 addition, addition=vigenere, subtraction=beaufort, minuend
# C=P+K C=P-K, C=K-P


def plaintext_autokey_vigenere_encrypt(
    plaintext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Vigenere primitive without any console output, C=P+K
    """
    key: List[int] = primer + plaintext
    output: List[int] = []
    for j in range(0, len(plaintext)):
        c = (plaintext[j] + key[j] + MAX) % MAX
        output.append(c)
    return output


def plaintext_autokey_vigenere_decrypt(
    ciphertext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Vigenere primitive without any console output, P=C-K
    """
    key: List[int] = primer.copy()
    output: List[int] = []
    for j in range(0, len(ciphertext)):
        c = (ciphertext[j] - key[j] + MAX) % MAX
        output.append(c)
        key.append(c)
    return output


def plaintext_autokey_minuend_encrypt(
    plaintext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Minuend primitive without any console output, C=K-P
    """
    key: List[int] = primer + plaintext
    output: List[int] = []
    for j in range(0, len(plaintext)):
        c = (key[j] - plaintext[j] + MAX) % MAX
        output.append(c)
    return output


def plaintext_autokey_minuend_decrypt(
    ciphertext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Minuend primitive without any console output, P=K-C
    """
    key: List[int] = primer.copy()
    output: List[int] = []
    for j in range(0, len(ciphertext)):
        c = (key[j] - ciphertext[j] + MAX) % MAX
        output.append(c)
        key.append(c)
    return output


def plaintext_autokey_beaufort_encrypt(
    plaintext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Beafort primitive without any console output, C=P-K
    """
    key: List[int] = primer + plaintext
    output: List[int] = []
    for j in range(0, len(plaintext)):
        c = (plaintext[j] - key[j] + MAX) % MAX
        output.append(c)
    return output


def plaintext_autokey_beaufort_decrypt(
    ciphertext: List[int], primer: List[int] = [0]
) -> List[int]:
    """
    Beafort primitive without any console output, P=C+K
    """
    key: List[int] = primer.copy()
    output: List[int] = []
    for j in range(0, len(ciphertext)):
        p = (key[j] + ciphertext[j] + MAX) % MAX
        output.append(p)
        key.append(p)
    return output


# assume 1 letter cipher autokey
# split by previous letter and create MAX alphabets. run bigram on these
def test2(ciphertext):
    print("test for autokey, test for IOC after specific character")

    # length of autokey introductory key
    for a in range(1, 10):

        alphabet = {}
        for i in range(0, MAX):
            alphabet[i] = []

        for i in range(0, len(ciphertext) - a - 1):
            alphabet[ciphertext[i]].append(ciphertext[i + a])

        tot = 0.0
        for i in alphabet.keys():
            tot += ioc(alphabet[i])
            print(f"IOC: {ioc(alphabet[i])}")
            dist(alphabet[i])
            # bigram_diagram(alphabet[i])
            # print("key={}: ioc of runes following {} = {}".format(a, i, ioc(alphabet[i])))
        print(f"key={a} avgioc={tot/MAX}")


# assume 1 letter cipher autokey
# split by next letter and create MAX alphabets. run bigram on these
def test2a(ciphertext):

    for a in range(1, 20):
        alphabet = {}
        for i in range(0, MAX):
            alphabet[i] = []

        for i in range(0 + a, len(ciphertext)):
            alphabet[ciphertext[i]].append(ciphertext[i - a])

        tot = 0
        for i in alphabet.keys():
            tot += ioc(alphabet[i])
            # bigram_diagram(alphabet[i])
            # print("key={}: ioc of runes before {} = {}".format(a, i, ioc(alphabet[i])))
        print(f"key={a} avgioc={tot/MAX}")


# assume fixed length key. find period
def test3(ciphertext):
    print("testing for fixed size periodicity")
    for period in range(1, 30):
        group = {}
        for i in range(period):
            group[i] = []

        for i in range(0, len(ciphertext)):
            group[i % period].append(ciphertext[i])

        iocsum = 0.0
        for k in group.keys():
            iocsum += float(ioc(group[k]))
            # print("ioc of runes {}/{} = {}".format(k, period, ioc(group[k])))

        print("average ioc period {} = {}".format(period, iocsum / period))


# test cipher autokey
def offset():
    # offset is the main variable, how much we are overlaying the data
    print(f"OFFSET: 1\n")

    output = []
    for j in range(0, len(gl)):
        transform = (gl[j] + MAX - gl[(j + 1) % len(gl)]) % MAX

        output.append((gl[j] + MAX - gl[(j + 1) % len(gl)]) % MAX)

    # print sample
    samplesize = 10
    print("CIPHER: ", end="")
    for i in range(0, samplesize):
        print("{:2} ".format(gl[i]), end="")
    print()
    print("OFFSET: ", end="")
    for i in range(0, samplesize):
        print("{:2} ".format(gl[(1 + i) % len(gl)]), end="")
    print()
    print("OUTPUT: ", end="")
    for i in range(0, samplesize):
        print("{:2} ".format(output[i]), end="")

    # print("\nOUTPUT: ", end="")
    # for i in range(0,samplesize*3):
    #    print("{:2} ".format(g.position_to_latin_forward_dict[output[i]]), end="")

    print("IOC: " + ioc(output))
    bigram_diagram(output)


# test cipher autokey
def offset_reverse():
    # offset is the main variable, how much we are overlaying the data
    offset = 5
    print(f"OFFSET: {offset}\n")

    output = []
    for j in range(0, len(gl)):
        transform = (gl[j - 1] + MAX - gl[(j) % len(gl)]) % MAX

        output.append((gl[j] + MAX + offset - gl[(j - 1) % len(gl)]) % MAX)

    # print sample
    samplesize = 10
    print("CIPHER: ", end="")
    for i in range(0, samplesize):
        print("{:2} ".format(gl[i]), end="")
    print()
    print("OFFSET: ", end="")
    for i in range(0, samplesize):
        print("{:2} ".format(gl[(offset + i) % len(gl)]), end="")
    print()
    print("OUTPUT: ", end="")
    for i in range(0, samplesize):
        print("{:2} ".format(output[i]), end="")

    # print("\nOUTPUT: ", end="")
    # for i in range(0,samplesize*3):
    #    print("{:2} ".format(g.position_to_latin_forward_dict[output[i]]), end="")

    print("IOC: " + ioc(output))
    bigram_diagram(output)


# test cipher autokey
def test4():
    print("\n\n\nLP\n")
    print("IOC: " + ioc(gl))
    bigram_diagram(gl)

    # now overlay list with itself
    # offset is the main variable, how much we are overlaying the data
    for offset in range(0, MAX):

        print(f"\n\n\nOFFSET: {offset}\n")

        output = []
        for j in range(0, len(gl)):
            output.append((gl[j] + MAX + offset - gl[(j - 1) % len(gl)]) % MAX)

        # print sample
        samplesize = 10
        print("CIPHER: ", end="")
        for i in range(0, samplesize):
            print("{:2} ".format(gl[i]), end="")
        print()
        print("OFFSET: ", end="")
        for i in range(0, samplesize):
            print("{:2} ".format(gl[(1 + i) % len(gl)]), end="")
        print()
        print("OUTPUT: ", end="")
        for i in range(0, samplesize):
            print("{:2} ".format(output[i]), end="")

        print("\nOUTPUT: ", end="")
        for i in range(0, samplesize * 3):
            print("{:2} ".format(g.position_to_latin_forward_dict[output[i]]), end="")

        print()

        print("IOC: " + ioc(output))
        bigram_diagram(output)


def ignore():
    for offset in range(1, 20):
        print(f"OFFSET: {offset}")
        x = autokey_vigenere(gl, offset=offset)
        print("number of dups: " + str(len(isomorph(x).keys())))
        y = split_by_character(x)
        for k in y.keys():
            print(ioc(y[k]), end=" ")
        print()


def prime_factors(n: int) -> List[int]:
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors
