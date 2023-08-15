#!/usr/bin/env python3

# solve simple vigenere
# IDEA: use threading

from collections import defaultdict
import multiprocessing
import random
from typing import TypeVar

from simanneal import Annealer

from aldegonde.stats import compare
from aldegonde import pasc

T = TypeVar("T")

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# (key len= 14)
VIG = """DAZFI SFSPA VQLSN PXYSZ WXALC DAFGQ UISMT PHZGA MKTTF TCCFX
KFCRG GLPFE TZMMM ZOZDE ADWVZ WMWKV GQSOH QSVHP WFKLS LEASE
PWHMJ EGKPU RVSXJ XVBWV POSDE TEQTX OBZIK WCXLW NUOVJ MJCLL
OEOFA ZENVM JILOW ZEKAZ EJAQD ILSWW ESGUG KTZGQ ZVRMN WTQSE
OTKTK PBSTA MQVER MJEGL JQRTL GFJYG SPTZP GTACM OECBX SESCI
YGUFP KVILL TWDKS ZODFW FWEAA PQTFS TQIRG MPMEL RYELH QSVWB
AWMOS DELHM UZGPG YEKZU KWTAM ZJMLS EVJQT GLAWV OVVXH KWQIL
IEUYS ZWXAH HUSZO GMUZQ CIMVZ UVWIF JJHPW VXFSE TZEDF"""

# key = "FOUNDATION" # (key len= 10)
BEAU = """EKFNKSPVVUXDJUWWIIWUOAINQIRUUAMXWBZNTVLCRTQWLTPIXBBJGWRCRIUVBOHKCWBADJSVBGDHVUUBFQNJDJSEDFBTQBZVFRCFSKNZQMZROACHUSZJPQZJDVBZRSGEHZSAAWKTTPQZLCUPCWIAKSBMQALGCECJXBWZJJXAWKRCUAAAXIEJHAAWLWGQKVMHUUFMZWOPMHQMZHAEXELLOJVVABKWBNQNQCLVVGXWUVLWHHDPFBWKZACDXFBBRZYYTEWNOWBZWSHAWNHVNNKZCOVTNDGSZHFGOJNODRDIGUDJNWBGDNMAWFAVNJQHMIVIOGQAAXPWOACSNPCJZPUVOACJDUTABVMMUJLACPHFNGCBFAGQSJOBGUKTTPGCRTQKBAPQOWUKCVCGAPHNMGJZIWQRABBCGWZTTFQZLXUUWWCGOJNODRZJPXGSXBONQXQAKNUDCCDFPQVGFBBGDHRIKVFXYJMWQEOKMAJFIWTXDIOKQBZNTQMNBWUWSMYELBBGYJZLOUXGXCUVWWXIWIRXBTQAAEGWBFGFBWTPGUFWNJHABNOCXOHUVTFVATOHMBCGAIWGBSUVDOSAVFRUCFLPPMHFTVNJMWLQVJFXCIPJMAWCRTQEPCOUXGXWPZMHZVKGRBGTMVFRHFNTUCPGCIBKCKUUWVFRHFNOIMVHLUBRYAMVWWCEWZEOCJKTTPSZLDRMZASUBKTOHFYAGKWYBOKIPJMACGFTQFPVOEBKBLYGPSBBKWBWGWJXPPHNMSGTSXGUVMBODZRAGAJNSQCYZAJDAWYGIGDFPAAIAKHKZXXBAFNHQWZIFNGCBVNNKELXDARVJZIWMAWLRUHUMCLDOAHWFJDQOUXGXCNNIWLUJIBBRJASEIUVBJGWDJPTDPMHQAQMGEHNKKMZYVPVLJCGNNIWQUBJSAIZMWAUMNBWUWKTTVQZLWNNSPQUVZEXAUJIABKXLKCUVMGUJGXWRJDHMAWJSXGCSWQABUYKSNOSAUDGXWOCPJVVAUBRBJQGTPKKJHQWZSGBKRFWYZMHMKBZOHMVPVOEBLBWQAYMCGKKAADRWSRBHJNUPIZJPFLJFVNGZJPGABBWNFLZFFQBRUDAZXSKCNOEUAKMGKSGRVNZJUMBKGFLHZWAGFGAYGCKZAABWGFDJWZYPATJMHQMZNPDGURJNFLXVABHFZJNBWLVVGBMGBRMGMKNUVNNLEMAMGRJWZJIMIDCSABRVHMPHFNGRJOACPVGFVUVVIIESBHNQVKPFNKWAADUWWNUAKRJDZRWLBOSBVNJLAHELNZIQWYMCWQVBDPRWWGAVVYOJCOPPIWJTQSZJNARQURBQJAOVFKNMH"""

VARBEAU = """WQVNQILFFGDXRGEESSEGMASNKSJGGAODEZBNHFPYJHKEPHLSDZZRUEJYJSGFZMTQYEZAXRIFZUXTFGGZVKNRXRIWXVZHKZBFVJYVIQNBKOBJMAYTGIBRLKBRXFZBJIUWTBIAAEQHHLKBPYGLYESAQIZOKAPUYWYRDZEBRRDAEQJYGAAADSWRTAAEPEUKQFOTGGVOBEMLOTKOBTAWDWPPMRFFAZQEZNKNKYPFFUDEGFPETTXLVZEQBAYXDVZZJBCCHWENMEZBEITAENTFNNQBYMFHNXUIBTVUMRNMXJXSUGXRNEZUXNOAEVAFNRKTOSFSMUKAADLEMAYINLYRBLGFMAYRXGHAZFOOGRPAYLTVNUYZVAUKIRMZUGQHHLUYJHKQZALKMEGQYFYUALTNOURBSEKJAZZYUEBHHVKBPDGGEEYUMRNMXJBRLDUIDZMNKDKAQNGXYYXVLKFUVZZUXTJSQFVDCROEKWMQOARVSEHDXSMQKZBNHKONZEGEIOCWPZZUCRBPMGDUDYGFEEDSESJDZHKAAWUEZVUVZEHLUGVENRTAZNMYDMTGFHVFAHMTOZYUASEUZIGFXMIAFVJGYVPLLOTVHFNROEPKFRVDYSLROAEYJHKWLYMGDUDELBOTBFQUJZUHOFVJTVNHGYLUYSZQYQGGEFVJTVNMSOFTPGZJCAOFEEYWEBWMYRQHHLIBPXJOBAIGZQHMTVCAUQECZMQSLROAYUVHKVLFMWZQZPCULIZZQEZEUERDLLTNOIUHIDUGFOZMXBJAUARNIKYCBARXAECUSUXVLAASAQTQBDDZAVNTKEBSVNUYZFNNQWPDXAJFRBSEOAEPJGTGOYPXMATEVRXKMGDUDYNNSEPGRSZZJRAIWSGFZRUEXRLHXLOTKAKOUWTNQQOBCFLFPRYUNNSEKGZRIASBOEAGONZEGEQHHFKBPENNILKGFBWDAGRSAZQDPQYGFOUGRUDEJRXTOAERIDUYIEKAZGCQINMIAGXUDEMYLRFFAGZJZRKUHLQQRTKEBIUZQJVECBOTOQZBMTOFLFMWZPZEKACOYUQQAAXJEIJZTRNGLSBRLVPRVFNUBRLUAZZENVPBVVKZJGXABDIQYNMWGAQOUQIUJFNBRGOZQUVPTBEAUVUACUYQBAAZEUVXREBCLAHROTKOBNLXUGJRNVPDFAZTVBRNZEPFFUZOUZJOUOQNGFNNPWOAOUJREBRSOSXYIAZJFTOLTVNUJRMAYLFUVFGFFSSWIZTNKFQLVNQEAAXGEENGAQJRXBJEPZMIZFNRPATWPNBSKECOYEKFZXLJEEUAFFCMRYMLLSERHKIBRNAJKGJZKRAMFVQNOT"""


CT = "".join(c for c in VARBEAU if c in alphabet)

VIG = pasc.vigenere_tr(alphabet)
LEN = 10


class simple_vigenere_solver(Annealer):
    """
    This is a simple Vigenere solver, with a normal ciphertext alphabet
    """

    state: list[str]

    def move(self):
        """
        randomly change one letter
        """
        self.state[random.randrange(len(self.state))] = random.randrange(len(alphabet))

    def energy(self):
        """
        calculate score
        """
        keyword = [alphabet[i] for i in self.state]
        plaintext = "".join(pasc.pasc_decrypt(CT, keyword, VIG))
        return -compare.quadgramscore(plaintext)


class custom_vigenere_solver(Annealer):
    """
    Vigenere solver with custom ciphertext alphabet with period N
    There is 1 alphabet that's not a normal alphabet (could be any
    MASC) but is shifted for each period with a custom ammount.

    This should work on vigenere (normal alphabet), beaufort, variant
    beaufort and any mixed alphabet
    """

    # the state consists of two components: the custom alphabet, and the shifts
    # the length of the alphabet is the number of letters (often 26)
    # the length of the shifts is the period of the cipher (N)
    state: tuple[list[int], list[int]]

    def move(self):
        """
        we can change 2 things: either a swap in the alphabet, similar to MASC
        or we shift one of the periods by a random amount
        """
        if bool(random.getrandbits(1)):
            # swap two letters in the alphabet mapping
            a, b = random.sample(range(len(self.state[0])), 2)
            self.state[0][a], self.state[0][b] = self.state[0][b], self.state[0][a]
        else:
            # change random row shift by random amount:
            self.state[1][random.randrange(LEN)] = random.randrange(len(alphabet))

    def state2tr(self, state) -> dict[T, dict[T, T]]:
        """
        turn state into a TR
        """
        TR: dict[T, dict[T, T]] = defaultdict(dict)
        keyword = "".join(alphabet[i] for i in range(LEN))
        mixalf = state[0]
        shifts = state[1]
        for i, k in enumerate(keyword):
            for j, a in enumerate(alphabet):
                shift = shifts[i]
                char = mixalf[j]
                TR[k][a] = alphabet[(char + shift) % len(alphabet)]
        return TR

    def energy(self):
        # KEYWORD = "ABCDEFGH...." Note: this will fail if LEN>len(alphabet)
        keyword = "".join(alphabet[i] for i in range(LEN))
        TR = self.state2tr(self.state)
        plaintext = "".join(pasc.pasc_decrypt(CT, keyword, TR))
        return -compare.quadgramscore(plaintext)


def determine_schedule(ciphertext: str) -> dict:
    # tsp.Tmax = 600
    # tsp.Tmin = 0.1
    # tsp.steps = 80000
    initial_state = [random.randrange(len(alphabet)) for idx in range(0, LEN)]
    tsp = simple_vigenere_solver(initial_state)
    tsp.copy_strategy = "slice"
    auto_schedule = tsp.auto(minutes=0.1)
    del tsp
    print(auto_schedule)
    return auto_schedule


def threaded_simple_solver(
    ciphertext: str, schedule: dict
) -> tuple[list[int], int, str]:
    """
    this can run inside a thread
    """
    initial_state = [random.randrange(len(alphabet)) for idx in range(0, LEN)]
    tsp = simple_vigenere_solver(initial_state)
    tsp.copy_strategy = "slice"
    # tsp.set_schedule(schedule)
    out, score = tsp.anneal()
    keyword = [alphabet[i] for i in out]
    plaintext = "".join(pasc.pasc_decrypt(CT, keyword, VIG))
    return (out, score, plaintext)


def threaded_custom_solver(
    ciphertext: str, schedule: dict
) -> tuple[list[int], int, str]:
    """
    this can run inside a thread
    """
    mixalf = [i for i in range(len(alphabet))]
    shifts = [i for i in range(LEN)]
    initial_state = (mixalf, shifts)
    tsp = custom_vigenere_solver(initial_state)
    tsp.Tmax = 3000
    tsp.Tmin = 0.1
    tsp.steps = 80000
    # tsp.copy_strategy = "slice"
    # tsp.set_schedule(schedule)
    out, score = tsp.anneal()
    TR = tsp.state2tr(out)
    keyword = "".join(alphabet[i] for i in range(LEN))
    plaintext = "".join(pasc.pasc_decrypt(CT, keyword, TR))
    return (out, score, plaintext)


def solve_anneal(ciphertext: str) -> None:
    # schedule = determine_schedule(ciphertext)
    schedule = {}

    with multiprocessing.Pool() as pool:
        results = pool.starmap(threaded_custom_solver, [[ciphertext, schedule]] * 1)
        for r in results:
            print(r)

    # key, score, plaintext = threaded_solver(ciphertext, auto_schedule)

    # pool.close()


if __name__ == "__main__":
    solve_anneal(CT)
