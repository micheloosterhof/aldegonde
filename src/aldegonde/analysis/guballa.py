"""
Jens Guballa's algorithm using piecemeal bigram scoring to break PASC
"""

from typing import TypeVar

from aldegonde import pasc
from aldegonde.stats import compare

T = TypeVar("T")

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def bigram_break_pasc(
    ciphertext: str,
    tabularecta: pasc.TR[str],
    key_len: int,
) -> tuple[str, float]:
    """
    Guballa's algorithm in PHP

    function break_vigenere ($cipher_text, $key_len) {
        global $vigenere_square, $bigram_log;
        $key = array();
        for ($key_idx = 0; $key_idx < $key_len; $key_idx++) {
            $best_fitness = 0;
            for ($key_ch1 = 0; $key_ch1 < 26; $key_ch1++) {
                for ($key_ch2 = 0; $key_ch2 < 26; $key_ch2++) {
                    $fitness = 0;
                    for ($text_idx = $key_idx; $text_idx < (count($cipher_text) - 1); $text_idx += $key_len) {
                        $clear_ch1 = $vigenere_square[$cipher_text[$text_idx  ]][$key_ch1];
                        $clear_ch2 = $vigenere_square[$cipher_text[$text_idx+1]][$key_ch2];
                        $fitness += $bigram_log[$clear_ch1][$clear_ch2];
                    }
                    if ($fitness > $best_fitness) {
                        $best_fitness = $fitness;
                        $best_key_ch1 = $key_ch1;
                        $best_key_ch2 = $key_ch2;
                    }
                }
            }
            if ($key_idx == 0) {
                $best_score_0   = $best_fitness;
                $best_key_ch1_0 = $best_key_ch1;
                $best_key_ch2_0 = $best_key_ch2;
                array_push($key, 0); # just a placeholder
            }
            else {
                array_push($key, ($prev_best_score > $best_fitness) ? $prev_best_key_ch2 : $best_key_ch1);
            }
            $prev_best_score = $best_fitness;
            $prev_best_key_ch2 = $best_key_ch2;
        }
        $key[0] = ($best_fitness > $best_score_0) ? $best_key_ch2 : $best_key_ch1_0 ;

        return $key;
    }
    """
    key: list[str] = []

    # take all keys of the second index, the first one may not have the full alphabet
    alphabet = tabularecta[list(tabularecta.keys())[0]].keys()

    rtr = pasc.reverse_tr(tabularecta)

    for key_idx in range(key_len):
        best_fitness: float = -10000000.0
        prev_best_score: float = best_fitness - 1.0
        prev_best_key_ch2: str = ""
        for key_ch1 in alphabet:
            for key_ch2 in alphabet:
                fitness: float = 0.0
                for text_idx in range(key_idx, len(ciphertext) - 1, key_len):
                    clear_ch1 = rtr[key_ch1][ciphertext[text_idx]]
                    clear_ch2 = rtr[key_ch2][ciphertext[text_idx + 1]]
                    fitness = fitness + compare.bigramscore(clear_ch1 + clear_ch2)

                if fitness > best_fitness:
                    best_fitness = fitness
                    best_key_ch1: str = key_ch1
                    best_key_ch2: str = key_ch2

        if key_idx == 0:
            best_score_0: float = best_fitness
            best_key_ch1_0: str = best_key_ch1
            # best_key_ch2_0: str = best_key_ch2
            key.append("#")
        else:
            if prev_best_score > best_fitness:
                key.append(prev_best_key_ch2)
            else:
                key.append(best_key_ch1)

        prev_best_score = best_fitness
        prev_best_key_ch2 = best_key_ch2

    if best_fitness > best_score_0:
        key[0] = best_key_ch2
    else:
        key[0] = best_key_ch1_0

    return ("".join(key), best_fitness)
