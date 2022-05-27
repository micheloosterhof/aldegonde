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


def trigrams(runes: list[int]):
    """
    get the trigrams
    """
    return repeat(runes, min=3, max=3)


def quadgrams(runes: list[int]):
    """
    get the quadgrams
    """
    return repeat(runes, min=4, max=4)


def find(sequence: list[int], runes: list[int]) -> list[int]:
    """
    find `sequence` inside the list of `runes`, return array with indexes
    """
    N = len(runes)
    results = []
    for index in range(0, N - len(sequence) + 1):
        if sequence == runes[index : index + len(sequence)]:
            results.append(index)
    return results


def dist(runes: list[int]) -> None:
    """
    print frequency distribution
    """
    N = len(runes)
    freqs = Counter(runes)
    print("frequency distribution")
    for rune in range(0, MAX):
        print(f"{rune}: {freqs[rune]/N*100}")


def kappa(
    ciphertext: list[int],
    min: int = 1,
    max: int = 51,
    threshold: float = 1.3,
    trace: bool = False,
) -> None:
    """
    kappa test
    overlay text with itself and count the number of duplicate letters
    """
    if max == 0:
        max = int(len(ciphertext) / 2)
    for a in range(min, max):
        counter = 0
        dups = 0
        for i in range(0, len(ciphertext) - a):
            counter = counter + 1
            if ciphertext[i] == ciphertext[i + a]:
                dups = dups + 1
        if (dups / counter * MAX) > threshold or trace is True:
            print(f"offset={a:02d}, dups={dups:02d}, ioc={dups/counter*MAX:.3f} ")
    print()


def detect_plaintext_autokey(
    ciphertext: list[int],
    minkeysize: int = 1,
    maxkeysize: int = 20,
    trace: bool = False,
) -> None:
    """
    the way Caesar generalizes to Vigenere,
    a single-letter autokey generalizes to a multi-letter autokey
    to solve it, split it into multiple slices.
    """
    if trace is True:
        print(f"test for plaintext autokey, samplesize={len(ciphertext)}")
        print("#######################################################\n")

    for keysize in range(minkeysize, maxkeysize + 1):
        slices = {}
        vigiocs: float = 0
        miniocs: float = 0
        beaiocs: float = 0
        for start in range(0, keysize):
            slices[start] = ciphertext[start::keysize]
            if trace is True:
                print(f"\nslice={start}: ", end="")
            # Bruteforce Vigenere introductory key at this position
            for key in range(0, MAX):
                plain = plaintext_autokey_vigenere_decrypt(slices[start], [key])
                vigiocs += normalized_ioc(plain)
                if normalized_ioc(plain) > 1.3:
                    if trace is True:
                        print(f"vigenere ioc={normalized_ioc(plain):.2f} ", end="")
            # Bruteforce Beaufort introductory key at this position
            for key in range(0, MAX):
                plain = plaintext_autokey_beaufort_decrypt(slices[start], [key])
                beaiocs += normalized_ioc(plain)
                if normalized_ioc(plain) > 1.3:
                    if trace is True:
                        print(f"beaufort ioc={normalized_ioc(plain):.2f} ", end="")
            # Bruteforce Minuend introductory key at this position
            for key in range(0, MAX):
                plain = plaintext_autokey_beaufort_decrypt(slices[start], [key])
                miniocs += normalized_ioc(plain)
                if normalized_ioc(plain) > 1.3:
                    if trace is True:
                        print(f"minuend ioc={normalized_ioc(plain):.2f} ", end="")
        vigiocavg = vigiocs / MAX / keysize
        miniocavg = miniocs / MAX / keysize
        beaiocavg = beaiocs / MAX / keysize
        if trace is True:
            print(f"\nvigenere keysize={keysize} avgioc = {vigiocavg:0.3f}")
            print(f"\nbeaufort keysize={keysize} avgioc = {beaiocavg:0.3f}")
            print(f"\nminuend  keysize={keysize} avgioc = {miniocavg:0.3f}")
        if vigiocavg > 1.2 or miniocavg > 1.2 or beaiocavg > 1.2:
            print("Attempting bruteforce...")
            if keysize < 4:
                bruteforce_autokey(
                    ciphertext,
                    minkeylength=keysize,
                    maxkeylength=keysize,
                    iocthreshold=1.3,
                )


def detect_ciphertext_autokey_vigenere(
    ciphertext: list[int],
    minkeysize: int = 1,
    maxkeysize: int = 10,
    trace: bool = False,
):
    """
    the way Caesar generalizes to Vigenere,
    a single-letter autokey generalizes to a multi-letter autokey
    to solve it, split it into multiple segments

    split by previous letter and create MAX alphabets. run bigram/ioc on these
    """
    if trace is True:
        print(f"test for ciphertext autokey, samplesize={len(ciphertext)}")
        print("#######################################################\n")

    # length of autokey introductory key
    for a in range(minkeysize, maxkeysize + 1):
        if trace is True:
            print(f"Checking key size {a}")

        alphabet: dict[int, list[int]] = {}
        for i in range(0, MAX):
            alphabet[i] = []

        for i in range(0, len(ciphertext) - a - 1):
            alphabet[ciphertext[i]].append(ciphertext[i + a])

        tot = 0.0
        for i in alphabet.keys():
            tot += normalized_ioc(alphabet[i])
            if trace is True:
                print(f"IOC: key={i} {normalized_ioc(alphabet[i]):.3f}")
            # dist(alphabet[i])
            # bigram_diagram(alphabet[i])
        print(f"key={a} avgioc={tot/MAX:.3f}")


# assume fixed length key. find period
def detect_vigenere(
    ciphertext: list[int],
    minkeysize: int = 1,
    maxkeysize: int = 20,
    trace: bool = False,
):
    print("testing for periodicity using friedman test")
    for period in range(minkeysize, maxkeysize):
        slices = split_by_slice(ciphertext, period)

        iocsum: float = 0.0
        for k in slices.keys():
            ic = normalized_ioc(slices[k])
            iocsum += ic
            if trace is True:
                print(f"ioc of runes {k}/{period} = {ic:.3f}")
        if trace is True:
            print(f"avgioc period {period} = {iocsum/period:.2f}")


# assume 1 letter cipher autokey
# split by next letter and create MAX alphabets. run bigram on these
def run_test2a(ciphertext):

    for a in range(1, 20):
        alphabet = {}
        for i in range(0, MAX):
            alphabet[i] = []

        for i in range(0 + a, len(ciphertext)):
            alphabet[ciphertext[i]].append(ciphertext[i - a])

        tot = 0
        for i in alphabet.keys():
            tot += normalized_ioc(alphabet[i])
            # bigram_diagram(alphabet[i])
            # print("key={}: ioc of runes before {} = {}".format(a, i, ioc(alphabet[i])))
        print(f"key={a} avgioc={tot/MAX:.3f}")


# assume fixed length key. find period
def run_test3(ciphertext: list[int], trace: bool = False):
    print("testing for fixed size periodicity")
    for period in range(1, 30):
        group: dict[int, list[int]] = {}
        for i in range(period):
            group[i] = []

        for i in range(0, len(ciphertext)):
            group[i % period].append(ciphertext[i])

        iocsum = 0.0
        for k in group.keys():
            iocsum += float(normalized_ioc(group[k]))
            # print("ioc of runes {}/{} = {}".format(k, period, ioc(group[k])))

        if trace is True or iocsum / period > 1.0:
            print(f"avgioc period {period} = {iocsum/period:.2f}")


# test cipher autokey
def offset():
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
def offset_reverse():
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
def run_test4():
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


def ignore():
    for offset in range(1, 20):
        print(f"OFFSET: {offset}")
        x = autokey_vigenere(gl, offset=offset)
        print("number of dups: " + str(len(repeat(x).keys())))
        y = split_by_character(x)
        for k in y.keys():
            print(normalized_ioc(y[k]), end=" ")
        print()


def prime_factors(n: int) -> list[int]:
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


def primes(n):
    out = list()
    sieve = [True] * (n + 1)
    for p in range(2, n + 1):
        if sieve[p]:
            out.append(p)
            for i in range(p, n + 1, p):
                sieve[i] = False
    return out


"""
2vig are vigenere variants that look 2 characters back rather than one
"""


def ciphertext_autokey_vig2_encrypt(
    plaintext: list[int], primer: list[int] = [0, 0]
) -> list[int]:
    """
    2Vig primitive without any console output, C=P+K1+K
    """
    key: list[int] = primer.copy()
    output: list[int] = []
    for j in range(0, len(plaintext)):
        c = (plaintext[j] - key[j + 1] + key[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_vig2_decrypt(
    ciphertext: list[int], primer: list[int] = [0, 0]
) -> list[int]:
    """
    2Vig primitive without any console output, P=C-K
    """
    key: list[int] = primer + ciphertext
    output: list[int] = []
    for j in range(0, len(ciphertext)):
        output.append((ciphertext[j] + key[j + 1] - key[j]) % MAX)
    return output


def ciphertext_autokey_oddvig_encrypt(
    plaintext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    2Vig primitive without any console output, C=P+K1+K
    """
    key: list[int] = primer.copy()
    output: list[int] = []
    for j in range(0, len(plaintext)):
        if j % 2 == 0:
            c = (plaintext[j] + key[j]) % MAX
        else:
            c = (plaintext[j] - key[j]) % MAX
        output.append(c)
        key.append(c)
    return output


def ciphertext_autokey_oddvig_decrypt(
    ciphertext: list[int], primer: list[int] = [0]
) -> list[int]:
    """
    2Vig primitive without any console output, P=C-K
    """
    key: list[int] = primer + ciphertext
    output: list[int] = []
    for j in range(0, len(ciphertext)):
        if j % 2 == 0:
            p = (ciphertext[j] - key[j]) % MAX
        else:
            p = (ciphertext[j] + key[j]) % MAX
        output.append(p)
    return output


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


def gcd(p, q):
    # Create the gcd of two positive integers.
    while q != 0:
        p, q = q, p % q
    return p


def is_coprime(x, y):
    return gcd(x, y) == 1


def phi_func(x):
    """
    euler phi // totient
    """
    if x == 1:
        return 1
    else:
        n = [y for y in range(1, x) if is_coprime(x, y)]
        return len(n)
