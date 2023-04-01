# """
# ciphertext autokey variations
# """
#
#
# from aldegonde.structures.sequence import Sequence
# from aldegonde.stats.ioc import ioc, nioc
# from aldegonde.analysis.split import split_by_character
# from aldegonde.algorithm.auto import
#
#
# def detect_plaintext_autokey(
#     ciphertext: list[int],
#     minkeysize: int = 1,
#     maxkeysize: int = 20,
#     alphabetsize: int = 26,
#     trace: bool = False,
# ) -> None:
#     """
#     the way Caesar generalizes to Vigenere,
#     a single-letter autokey generalizes to a multi-letter autokey
#     to solve it, split it into multiple slices.
#     """
#     if trace is True:
#         print(f"test for plaintext autokey, samplesize={len(ciphertext)}")
#         print("#######################################################\n")
#
#     for keysize in range(minkeysize, maxkeysize + 1):
#         slices = {}
#         vigiocs: float = 0
#         miniocs: float = 0
#         beaiocs: float = 0
#         for start in range(0, keysize):
#             slices[start] = ciphertext[start::keysize]
#             if trace is True:
#                 print(f"\nslice={start}: ", end="")
#             # Bruteforce Vigenere introductory key at this position
#             for key in range(0, alphabetsize):
#                 plain = plaintext_autokey_vigenere_decrypt(slices[start], [key])
#                 vigiocs += nioc(plain)[1]
#                 if nioc(plain)[1] > 1.3:
#                     if trace is True:
#                         print(f"vigenere ioc={nioc(plain)[1]:.2f} ", end="")
#             # Bruteforce Beaufort introductory key at this position
#             for key in range(0, alphabetsize):
#                 plain = plaintext_autokey_beaufort_decrypt(slices[start], [key])
#                 beaiocs += nioc(plain)[1]
#                 if nioc(plain)[1] > 1.3:
#                     if trace is True:
#                         print(f"beaufort ioc={nioc(plain)[1]:.2f} ", end="")
#             # Bruteforce Minuend introductory key at this position
#             for key in range(0, alphabetsize):
#                 plain = plaintext_autokey_beaufort_decrypt(slices[start], [key])
#                 miniocs += nioc(plain)[1]
#                 if nioc(plain)[1] > 1.3:
#                     if trace is True:
#                         print(f"minuend ioc={nioc(plain)[1]:.2f} ", end="")
#         vigiocavg = vigiocs / alphabetsize / keysize
#         miniocavg = miniocs / alphabetsize / keysize
#         beaiocavg = beaiocs / alphabetsize / keysize
#         if trace is True:
#             print(f"\nvigenere keysize={keysize} avgioc = {vigiocavg:0.3f}")
#             print(f"\nbeaufort keysize={keysize} avgioc = {beaiocavg:0.3f}")
#             print(f"\nminuend  keysize={keysize} avgioc = {miniocavg:0.3f}")
#         if vigiocavg > 1.2 or miniocavg > 1.2 or beaiocavg > 1.2:
#             print("Attempting bruteforce...")
#             if keysize < 4:
#                 bruteforce_autokey(
#                     ciphertext,
#                     minkeylength=keysize,
#                     maxkeylength=keysize,
#                     iocthreshold=1.3,
#                 )
#
#
# def detect_ciphertext_autokey_vigenere(
#     ciphertext: list[int],
#     minkeysize: int = 1,
#     maxkeysize: int = 10,
#     alphabetsize: int = 26,
#     trace: bool = False,
# ) -> None:
#     """
#     the way Caesar generalizes to Vigenere,
#     a single-letter autokey generalizes to a multi-letter autokey
#     to solve it, split it into multiple segments
#
#     split by previous letter and create MAX alphabets. run bigram/ioc on these
#     """
#     if trace is True:
#         print(f"test for ciphertext autokey, samplesize={len(ciphertext)}")
#         print("#######################################################\n")
#
#     # length of autokey introductory key
#     for a in range(minkeysize, maxkeysize + 1):
#         if trace is True:
#             print(f"Checking key size {a}")
#
#         alphabet: dict[int, list[int]] = {}
#         for i in range(0, alphabetsize):
#             alphabet[i] = []
#
#         for i in range(0, len(ciphertext) - a - 1):
#             alphabet[ciphertext[i]].append(ciphertext[i + a])
#
#         tot = 0.0
#         for k, v in alphabet.items():
#             tot += nioc(v)[1]
#             if trace is True:
#                 print(f"IOC: key={k} {nioc(v)[1]:.3f}")
#             # dist(v)
#             # bigram_diagram(v)
#         print(f"key={a} avgioc={tot/alphabetsize:.3f}")
#
#
# # assume 1 letter cipher autokey
# # split by next letter and create MAX alphabets. run bigram on these
# def run_test2a(ciphertext, MAX=26):
#     for a in range(1, 20):
#         alphabet = {}
#         for i in range(0, MAX):
#             alphabet[i] = []
#
#         for i in range(0 + a, len(ciphertext)):
#             alphabet[ciphertext[i]].append(ciphertext[i - a])
#
#         tot = 0
#         for i in alphabet.keys():
#             tot += nioc(alphabet[i])[1]
#             # bigram_diagram(alphabet[i])
#             # print("key={}: ioc of runes before {} = {}".format(a, i, ioc(alphabet[i])))
#         print(f"key={a} avgioc={tot/MAX:.3f}")
#
#
# def detect_autokey(
#     ciphertext: Sequence,
#     minkeysize: int = 1,
#     maxkeysize: int = 20,
#     trace: bool = False,
# ) -> None:
#     print("testing for 1 letter autokey using friedman test")
#     slices = split_by_character(ciphertext)
#
#     iocsum: float = 0.0
#     for k, v in slices.items():
#         ic = ioc(v)[1]
#         iocsum += ic
#         if trace is False:
#             print(f"ioc of runes {k}/{len(ciphertext.alphabet)} = {ic:.3f}")
#     print(f"avgioc {len(ciphertext.alphabet)} = {iocsum/len(ciphertext.alphabet):.2f}")
