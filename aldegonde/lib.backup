from collections import Counter

# There are 29 runes. Generally counted 0-28
MAX = 29


def detect_gronsfeld(runes: list[int]) -> None:
    """
    compare frequency of the 4 most common runes with the 2 least common runes
    """
    freqs = Counter(runes)
    val = sorted(freqs.values())
    p: float = (val[-1] + val[-2] + val[-3] + val[-4]) / (val[0] + val[1])
    print(f"gronsfeld ratio: {p:.2f}")


def diffstream(runes: list[int]) -> list[int]:
    """
    diffstream mod MAX
    DIFF = C_K+1 - C_K % MAX
    """
    diff = []
    for i in range(0, len(runes) - 1):
        diff.append((runes[i + 1] - runes[i]) % MAX)
    return diff


def diffstream1(runes: list[int]) -> list[int]:
    """
    diffstream mod MAX
    DIFF = C_K - C_K+1 % MAX
    """
    diff = []
    for i in range(0, len(runes) - 1):
        diff.append((runes[i] - runes[i + 1]) % MAX)
    return diff


def addstream(runes: list[int]) -> list[int]:
    """
    diffstream mod MAX
    DIFF = C_K + C_K+1 % MAX
    """
    diff = []
    for i in range(0, len(runes) - 1):
        diff.append((runes[i + 1] + runes[i]) % MAX)
    return diff


# test cipher autokey
def offset(gl):
    # offset is the main variable, how much we are overlaying the data
    print("OFFSET: 1\n")

    output = []
    for j in range(0, len(gl)):
        transform = (gl[j] - gl[(j + 1) % len(gl)]) % MAX

        output.append((gl[j] - gl[(j + 1) % len(gl)]) % MAX)

    # print sample
    samplesize = 10
    print("CIPHER: ", end="")
    for i in range(0, samplesize):
        print(f"{gl[i]:2} ", end="")
    print()
    print("OFFSET: ", end="")
    for i in range(0, samplesize):
        print(f"{gl[(1 + i) % len(gl)]:2} ", end="")
    print()
    print("OUTPUT: ", end="")
    for i in range(0, samplesize):
        print(f"{output[i]:2} ", end="")

    # print("\nOUTPUT: ", end="")
    # for i in range(0,samplesize*3):
    #    print("{:2} ".format(g.position_to_latin_forward_dict[output[i]]), end="")

    print("IOC: " + normalized_ioc(output))
    bigram_diagram(output)


# test cipher autokey
def offset_reverse(gl):
    # offset is the main variable, how much we are overlaying the data
    offset = 5
    print(f"OFFSET: {offset}\n")

    output = []
    for j in range(0, len(gl)):
        transform = (gl[j - 1] - gl[(j) % len(gl)]) % MAX

        output.append((gl[j] + offset - gl[(j - 1) % len(gl)]) % MAX)

    # print sample
    samplesize = 10
    print("CIPHER: ", end="")
    for i in range(0, samplesize):
        print(f"{gl[i]:2} ", end="")
    print()
    print("OFFSET: ", end="")
    for i in range(0, samplesize):
        print(f"{gl[(offset + i) % len(gl)]:2} ", end="")
    print()
    print("OUTPUT: ", end="")
    for i in range(0, samplesize):
        print(f"{output[i]:2} ", end="")

    # print("\nOUTPUT: ", end="")
    # for i in range(0,samplesize*3):
    #    print("{:2} ".format(g.position_to_latin_forward_dict[output[i]]), end="")

    print("IOC: " + normalized_ioc(output))
    bigram_diagram(output)


# test cipher autokey
def run_test4(gl):
    print("\n\n\nLP\n")
    print("IOC: " + normalized_ioc(gl))
    bigram_diagram(gl)

    # now overlay list with itself
    # offset is the main variable, how much we are overlaying the data
    for offset in range(0, MAX):

        print(f"\n\n\nOFFSET: {offset}\n")

        output = []
        for j in range(0, len(gl)):
            output.append((gl[j] + offset - gl[(j - 1) % len(gl)]) % MAX)

        # print sample
        samplesize = 10
        print("CIPHER: ", end="")
        for i in range(0, samplesize):
            print(f"{gl[i]:2} ", end="")
        print()
        print("OFFSET: ", end="")
        for i in range(0, samplesize):
            print(f"{gl[(1 + i) % len(gl)]:2} ", end="")
        print()
        print("OUTPUT: ", end="")
        for i in range(0, samplesize):
            print(f"{output[i]:2} ", end="")

        print("\nOUTPUT: ", end="")
        for i in range(0, samplesize * 3):
            print(f"{g.position_to_latin_forward_dict[output[i]]:2} ", end="")

        print()

        print("IOC: " + normalized_ioc(output))
        bigram_diagram(output)


def ignore(gl):
    for offset in range(1, 20):
        print(f"OFFSET: {offset}")
        x = autokey_vigenere(gl, offset=offset)
        print("number of dups: " + str(len(repeat(x).keys())))
        y = split_by_character(x)
        for k in y.keys():
            print(normalized_ioc(y[k]), end=" ")
        print()


def bruteforce_autokey(
    ciphertext: list[int],
    minkeylength: int = 1,
    maxkeylength: int = 1,
    iocthreshold: float = 1.2,
    trace: bool = False,
) -> None:
    """
    bruteforce vigenere autokey and variants
    """
    algs = {
        "ciphertext_vigenere": ciphertext_autokey_vigenere_decrypt,
        "ciphertext_beaufort": ciphertext_autokey_beaufort_decrypt,
        "ciphertext_minuend": ciphertext_autokey_minuend_decrypt,
        "plaintext_vigenere": plaintext_autokey_vigenere_decrypt,
        "plaintext_beaufort": plaintext_autokey_beaufort_decrypt,
        "plaintext_minuend": plaintext_autokey_minuend_decrypt,
    }
    for keylength in range(minkeylength, maxkeylength + 1):
        for key in RuneIterator(keylength):
            for a in algs.keys():
                p = algs[a](ciphertext, key)
                ic = normalized_ioc(p)
                if ic > iocthreshold or trace:
                    print(f"key {key}: {ic}: ")
                    english_output(p, limit=30)

    return
