#!/usr/bin/env python3
"""Structural analysis of the unsolved Liber Primus (page0-58.txt).

Parses the corpus preserving word boundaries (- = word sep, / = line break
within word stream, % = page break, . = sentence end, & = paragraph?,
$ = segment, 0-9 etc = annotations).
"""
import collections
import math
import random
import sys

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
assert len(RUNES) == 29
R2I = {r: i for i, r in enumerate(RUNES)}
N = 29

def parse(path: str):
    with open(path) as f:
        raw = f.read()
    pages = []  # list of pages; each page = list of words; word = list of ints
    cur_words = []
    cur_word = []
    for ch in raw:
        if ch in R2I:
            cur_word.append(R2I[ch])
        elif ch in "-.,;:!?&$\n":
            if cur_word:
                cur_words.append(cur_word)
                cur_word = []
        elif ch == "/":
            continue  # line break, not word break
        elif ch == "%":
            if cur_word:
                cur_words.append(cur_word)
                cur_word = []
            if cur_words:
                pages.append(cur_words)
                cur_words = []
        # digits/letters: annotations, ignore (treat as word break to be safe)
        elif ch.isalnum():
            continue
    if cur_word:
        cur_words.append(cur_word)
    if cur_words:
        pages.append(cur_words)
    return pages

def flat(pages):
    return [r for page in pages for w in page for r in w]

def ioc(seq):
    n = len(seq)
    if n < 2:
        return 0.0
    c = collections.Counter(seq)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))

def nioc(seq):
    return ioc(seq) * N

if __name__ == "__main__":
    pages = parse("data/page0-58.txt")
    words = [w for p in pages for w in p]
    s = flat(pages)
    print(f"pages: {len(pages)}, words: {len(words)}, runes: {len(s)}")
    print(f"global IoC (norm): {nioc(s):.4f}  (random=1.0, english-ish~1.78)")
    cnt = collections.Counter(s)
    print("unigram counts:", [cnt[i] for i in range(N)])
    chi2 = sum((cnt[i] - len(s)/N)**2 / (len(s)/N) for i in range(N))
    print(f"chi2 vs uniform: {chi2:.1f} (df=28, expect ~28, p05~41.3)")
    wl = collections.Counter(len(w) for w in words)
    print("word lengths:", dict(sorted(wl.items())))
