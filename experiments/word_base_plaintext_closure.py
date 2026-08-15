# ABOUTME: Closes the last word-level-autokey variant: a per-word base keyed on
# ABOUTME: the PREVIOUS WORD's plaintext, via the plaintext word-bigram repeat census.
"""Does a per-word base keyed on the previous word's plaintext survive?

`word-level-autokey.md` closes a keyed base for every OBSERVABLE tap (14-tap
battery) but explicitly defers the base keyed on the previous word's PLAINTEXT
to `plaintext-autokey.md`, whose closure is a fixed-lag RUNE-stream argument. A
base that steps once per word as an injective function of the whole previous
word is neither a fixed-lag rune tap nor an observable-word tap, so neither
closure reaches it.

It has a direct signature. With c = base_w(g^j(p)) and base_w = f(previous
plaintext word), an injective f gives: two occurrences of the same current
plaintext word Q that share the same PREVIOUS plaintext word P land on the same
base and the same within-word phases, so Q enciphers to identical ciphertext --
a forced repeated ciphertext WORD. So under this model the forced repeated
ciphertext words are exactly the recurrences of the plaintext adjacent word
bigram (P, Q), independent of g and of f. (Different P -> different base ->
only chance agreement; those are the null.)

We measure the plaintext word-bigram recurrence on the same-author register
(the recovered solved sections, position-preserving systems only so word
boundaries are exact), scale it to the corpus as pair counts scale --
quadratically in word count, the `plaintext_autokey_closure.py` convention --
and compare, by current-word length, against the observed ciphertext word
repeats and the doublet-preserving null. The discriminating cells are lengths
>= 4, where chance repeats are ~0.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402, I001
from lp_corpus import load_clean  # noqa: E402
from word_repeat_census import extra_pairs  # noqa: E402

M = 29
RUNES = set(c3301.CICADA_ALPHABET)
R2I = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
BOUNDARY = c3301.WORD_BOUNDARY
SOLVED_RUNES = 2797

# Per-segment decryption for the position-preserving systems (per-rune bijections
# that keep word boundaries). The two Vigenere segments (1+2, 10) drop F-interrupts
# and so lose position alignment -- excluded from the word register.
IDENTITY = lambda c: c  # noqa: E731
ATBASH = lambda c: (28 - c) % M  # noqa: E731
AFFINE = lambda c: (28 * c + 2) % M  # noqa: E731
SEGMENT_SYSTEM = {
    0: ATBASH,
    3: IDENTITY,
    4: IDENTITY,
    5: AFFINE,
    6: AFFINE,
    7: IDENTITY,
    8: IDENTITY,
    9: IDENTITY,
    11: IDENTITY,
    12: IDENTITY,
}  # segments 1, 2, 10 (Vigenere) intentionally absent


def register_segments_with_words() -> list[list[tuple[int, ...]]]:
    """Parse the solved prefix into segments, each a list of plaintext words.

    Only position-preserving segments are decrypted and returned; the word
    boundaries are the transcription's separators, exact for these systems.
    """
    text = (ROOT / "data/liber-primus__transcription--master.txt").read_text()
    seg_words: list[list[tuple[int, ...]]] = [[]]
    cur: list[int] = []
    count = 0
    for ch in text:
        if count >= SOLVED_RUNES:
            break
        if ch in RUNES:
            cur.append(R2I[ch])
            count += 1
        elif ch in "&$":
            if cur:
                seg_words[-1].append(tuple(cur))
                cur = []
            if seg_words[-1]:
                seg_words.append([])
        elif ch in BOUNDARY:
            if cur:
                seg_words[-1].append(tuple(cur))
                cur = []
    if cur:
        seg_words[-1].append(tuple(cur))
    segs = [s for s in seg_words if s]
    # decrypt in place by segment index, keep only position-preserving systems
    out: list[list[tuple[int, ...]]] = []
    for i, words in enumerate(segs):
        sysf = SEGMENT_SYSTEM.get(i)
        if sysf is None:
            continue
        out.append([tuple(sysf(c) for c in w) for w in words])
    return out


def bigram_pairs_by_curr_len(segments: list[list[tuple[int, ...]]]) -> dict[int, int]:
    """Recurring adjacent plaintext word-bigrams, counted by the second word's length.

    Bigrams are formed within a segment only (a section break is not a word
    adjacency). A bigram class of k occurrences contributes k*(k-1)/2 pairs.
    """
    by_len_classes: dict[int, dict[tuple, int]] = defaultdict(lambda: defaultdict(int))
    for words in segments:
        for a, b in zip(words, words[1:]):
            by_len_classes[len(b)][(a, b)] += 1
    out: dict[int, int] = {}
    for L, classes in by_len_classes.items():
        out[L] = sum(n * (n - 1) // 2 for n in classes.values() if n >= 2)
    return out


def self_check() -> None:
    """Guard the core claim: a repeated plaintext word-bigram forces a repeated
    ciphertext word under base=f(prev word), for ANY injective g and f."""
    import random

    rng = random.Random(0)

    def rand_perm() -> list[int]:
        p = list(range(M))
        rng.shuffle(p)
        return p

    g = rand_perm()
    gp = [list(range(M))]
    for _ in range(4):
        gp.append([g[x] for x in gp[-1]])
    base_of: dict[tuple, list[int]] = {}

    def base_for(prev_word: tuple) -> list[int]:
        if prev_word not in base_of:
            base_of[prev_word] = (
                rand_perm()
            )  # f injective by construction (fresh per key)
        return base_of[prev_word]

    def encipher_word(prev_word: tuple, word: tuple) -> tuple:
        base = base_for(prev_word)
        return tuple(base[gp[j % 5][p]] for j, p in enumerate(word))

    prev = (1, 2, 3)
    q = (4, 5, 6, 7)
    other = (8, 9)
    # two occurrences of bigram (prev, q); one occurrence of (other, q)
    c1 = encipher_word(prev, q)
    c2 = encipher_word(prev, q)
    c3 = encipher_word(other, q)
    assert c1 == c2, "same prev word must force identical ciphertext for Q"
    assert c1 != c3, "different prev word must (here) give different ciphertext"
    print("self-check: base=f(prev word) forces a ciphertext word-repeat exactly on")
    print("            plaintext word-bigram recurrence -- confirmed.\n")


def observed_by_len() -> tuple[dict[int, int], int]:
    stream, wid = load_clean()
    d: dict[int, list[int]] = defaultdict(list)
    for r, w in zip(stream, wid):
        d[w].append(r)
    words = [tuple(d[k]) for k in sorted(d)]
    obs: dict[int, int] = {}
    for L in range(1, 15):
        wl = [w for w in words if len(w) == L]
        obs[L] = extra_pairs(wl, L) if wl else 0
    return obs, len(words)


def main() -> None:
    self_check()

    segs = register_segments_with_words()
    reg_words = sum(len(s) for s in segs)
    reg_bigrams = sum(max(0, len(s) - 1) for s in segs)
    reg_pairs = bigram_pairs_by_curr_len(segs)

    obs, corp_words = observed_by_len()
    scale = (corp_words / reg_words) ** 2

    print(
        f"register (same-author, position-preserving segments): "
        f"{reg_words} words, {reg_bigrams} adjacent word-bigrams"
    )
    print(
        f"corpus: {corp_words} words; pair-count scale (corpus/reg)^2 = {scale:.1f}\n"
    )
    print("forced ciphertext word-repeats predicted by base=f(prev plaintext word):")
    print(f"  {'len':>4}{'reg bigram pairs':>18}{'predicted':>11}{'observed':>10}")
    total_pred_hi = 0.0
    for L in range(1, 15):
        rp = reg_pairs.get(L, 0)
        pred = rp * scale
        if L >= 4:
            total_pred_hi += pred
        flag = "  <-- 0 observed at zero background" if (L >= 4 and pred > 0.5) else ""
        print(f"  {L:>4}{rp:>18}{pred:>11.1f}{obs.get(L, 0):>10}{flag}")
    print(
        f"\nlengths >=4 (chance ~0): predicted forced {total_pred_hi:.0f} vs observed "
        f"{sum(obs.get(L, 0) for L in range(4, 15))}"
    )


if __name__ == "__main__":
    main()
