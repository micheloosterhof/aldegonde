#!/usr/bin/env python3
"""Broad anomaly scan of the unsolved Liber Primus (data/page0-58.txt).

Looks for structure beyond the known doublet suppression:
- position-in-word effects
- word-level statistics (repeated words, word sums, aligned coincidences)
- delta distributions conditioned on boundary type
- per-section / per-page statistics
- layout (line) effects
- mirror / atbash symmetry
- isomorph statistics
"""

from collections import Counter, defaultdict
import math
import random

from scipy.stats import chisquare, chi2_contingency, norm

from aldegonde import c3301

ALPH = c3301.CICADA_ALPHABET
N = 29


def parse(path: str = "data/page0-58.txt"):
    """Return (stream, seps, words, lines, pages, sections).

    stream: list[int] all rune indices in order
    seps: list[str] separator type between rune i and i+1:
          '' none (adjacent in word), 'w' word, 's' sentence,
          'p' page, 'S' section, 'x' other (numbers/latin gap)
    """
    data = open(path).read().replace("\n", "")
    stream: list[int] = []
    seps: list[str] = []
    pending = ""  # strongest separator seen since last rune
    rank = {"": 0, "l": 1, "w": 2, "s": 3, "p": 4, "S": 5, "x": 6}
    words: list[list[int]] = []
    lines: list[list[int]] = []
    pages: list[list[int]] = []
    sections: list[list[int]] = []
    cur_word: list[int] = []
    cur_line: list[int] = []
    cur_page: list[int] = []
    cur_section: list[int] = []

    def close_word():
        nonlocal cur_word
        if cur_word:
            words.append(cur_word)
            cur_word = []

    def close_line():
        nonlocal cur_line
        if cur_line:
            lines.append(cur_line)
            cur_line = []

    def close_page():
        nonlocal cur_page
        close_word()
        close_line()
        if cur_page:
            pages.append(cur_page)
            cur_page = []

    def close_section():
        nonlocal cur_section
        close_page()
        if cur_section:
            sections.append(cur_section)
            cur_section = []

    for ch in data:
        if ch in ALPH:
            idx = c3301.r2i(ch)
            if stream:
                seps.append(pending)
            if pending in ("w", "s", "p", "S", "x"):
                close_word()
            pending = ""
            stream.append(idx)
            cur_word.append(idx)
            cur_line.append(idx)
            cur_page.append(idx)
            cur_section.append(idx)
        elif ch == "-":
            if rank["w"] > rank[pending]:
                pending = "w"
        elif ch == ".":
            if rank["s"] > rank[pending]:
                pending = "s"
        elif ch == "/":
            close_line()
            if rank["l"] > rank[pending]:
                pending = "l"
        elif ch == "%":
            close_page()
            if rank["p"] > rank[pending]:
                pending = "p"
        elif ch in "&$":
            close_section()
            if rank["S"] > rank[pending]:
                pending = "S"
        else:  # digits, latin letters: non-rune content
            if rank["x"] > rank[pending]:
                pending = "x"
    close_section()
    return stream, seps, words, lines, pages, sections


def ioc(seq) -> float:
    c = Counter(seq)
    n = len(seq)
    if n < 2:
        return 0.0
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def chisq_uniform(counts, label):
    tot = sum(counts)
    if tot < 50:
        return
    exp = [tot / len(counts)] * len(counts)
    stat, p = chisquare(counts, exp)
    flag = " ***" if p < 0.001 else (" *" if p < 0.01 else "")
    print(f"  {label}: n={tot} chi2={stat:.1f} p={p:.4f}{flag}")
    return p


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    print(f"runes={len(stream)} words={len(words)} lines={len(lines)} "
          f"pages={len(pages)} sections={len(sections)}")
    print(f"sep counts: {Counter(seps)}")

    print("\n=== 1. POSITION-IN-WORD ===")
    overall = Counter(stream)
    overall_counts = [overall[i] for i in range(N)]
    bypos = defaultdict(list)
    byend = defaultdict(list)
    for w in words:
        for j, r in enumerate(w):
            bypos[j].append(r)
            byend[len(w) - 1 - j].append(r)
    for j in range(8):
        if len(bypos[j]) < 100:
            break
        c = Counter(bypos[j])
        counts = [c[i] for i in range(N)]
        # compare against overall distribution
        rest = [overall_counts[i] - counts[i] for i in range(N)]
        stat, p, dof, _ = chi2_contingency([counts, rest])
        print(f"  pos {j}: n={len(bypos[j])} ioc={ioc(bypos[j])*N:.3f} "
              f"chi2-vs-rest p={p:.4f}{' ***' if p < 0.001 else ''}")
    for j in range(8):
        if len(byend[j]) < 100:
            break
        c = Counter(byend[j])
        counts = [c[i] for i in range(N)]
        rest = [overall_counts[i] - counts[i] for i in range(N)]
        stat, p, dof, _ = chi2_contingency([counts, rest])
        print(f"  endpos {j}: n={len(byend[j])} ioc={ioc(byend[j])*N:.3f} "
              f"chi2-vs-rest p={p:.4f}{' ***' if p < 0.001 else ''}")

    print("\n=== 2. WORD-LEVEL ===")
    # repeated words vs analytic expectation
    bylen = defaultdict(list)
    for w in words:
        bylen[len(w)].append(tuple(w))
    tot_obs_pairs = 0
    tot_exp_pairs = 0.0
    for L in sorted(bylen):
        ws = bylen[L]
        n = len(ws)
        cnt = Counter(ws)
        obs_pairs = sum(v * (v - 1) // 2 for v in cnt.values())
        exp_pairs = n * (n - 1) / 2 / (N ** L)
        tot_obs_pairs += obs_pairs
        tot_exp_pairs += exp_pairs
        if exp_pairs > 0.01 or obs_pairs > 0:
            print(f"  len {L}: {n} words, identical pairs obs={obs_pairs} "
                  f"exp={exp_pairs:.2f}")
    print(f"  TOTAL identical word pairs: obs={tot_obs_pairs} exp={tot_exp_pairs:.2f}")

    # word sums mod 29 (index based)
    sums = [sum(w) % N for w in words]
    chisq_uniform([Counter(sums)[i] for i in range(N)], "word sums mod 29 (idx)")
    # word sums of GP prime values mod 29
    vals = [sum(c3301.r2v(ALPH[r]) for r in w) % N for w in words]
    chisq_uniform([Counter(vals)[i] for i in range(N)], "word sums mod 29 (GP primes)")

    # aligned coincidence between consecutive words
    hits = opp = 0
    for a, b in zip(words, words[1:]):
        for x, y in zip(a, b):
            opp += 1
            hits += x == y
    exp = opp / N
    sd = math.sqrt(opp * (1 / N) * (1 - 1 / N))
    print(f"  consecutive-word aligned coincidences: obs={hits} exp={exp:.1f} "
          f"z={(hits - exp) / sd:+.2f}")
    # same for words at distance 2..5
    for d in range(2, 6):
        hits = opp = 0
        for a, b in zip(words, words[d:]):
            for x, y in zip(a, b):
                opp += 1
                hits += x == y
        exp = opp / N
        sd = math.sqrt(opp * (1 / N) * (1 - 1 / N))
        print(f"  word-dist {d} aligned coincidences: obs={hits} exp={exp:.1f} "
              f"z={(hits - exp) / sd:+.2f}")

    print("\n=== 3. DELTAS BY BOUNDARY TYPE ===")
    for kind, name in [("", "within-word"), ("w", "word-boundary"),
                       ("s", "sentence-boundary"), ("l", "line-break"),
                       ("p", "page-boundary"), ("S", "section-boundary")]:
        deltas = [ (stream[i + 1] - stream[i]) % N
                   for i in range(len(stream) - 1) if seps[i] == kind ]
        if len(deltas) < 100:
            print(f"  {name}: n={len(deltas)} (too few)")
            continue
        c = Counter(deltas)
        counts = [c[i] for i in range(N)]
        zero = counts[0]
        exp0 = len(deltas) / N
        chisq_uniform(counts, f"{name} deltas")
        # excluding zero
        chisq_uniform(counts[1:], f"{name} deltas (excl 0)")
        print(f"    delta=0: obs={zero} exp={exp0:.1f}")

    print("\n=== 4. PER-SECTION / PER-PAGE ===")
    for si, s in enumerate(sections):
        dbl = sum(1 for a, b in zip(s, s[1:]) if a == b)
        print(f"  section {si}: n={len(s)} ioc={ioc(s)*N:.3f} doublets={dbl} "
              f"(exp {len(s)/N:.1f})")
    iocs = [ioc(p) * N for p in pages if len(p) > 100]
    print(f"  page nIoC: min={min(iocs):.3f} max={max(iocs):.3f} "
          f"mean={sum(iocs)/len(iocs):.3f} (n={len(iocs)} pages)")

    print("\n=== 5. LINE LAYOUT ===")
    linestart = [l[0] for l in lines if l]
    lineend = [l[-1] for l in lines if l]
    c = Counter(linestart)
    chisq_uniform([c[i] for i in range(N)], "line-initial runes")
    c = Counter(lineend)
    chisq_uniform([c[i] for i in range(N)], "line-final runes")
    wordstart = [w[0] for w in words]
    wordend = [w[-1] for w in words]
    c = Counter(wordstart)
    chisq_uniform([c[i] for i in range(N)], "word-initial runes")
    c = Counter(wordend)
    chisq_uniform([c[i] for i in range(N)], "word-final runes")
    chisq_uniform(overall_counts, "overall rune distribution")
    llen = Counter(len(l) for l in lines)
    print(f"  line lengths: {sorted(llen.items())[:10]} ...")

    print("\n=== 6. MIRROR / ATBASH SYMMETRY ===")
    def mirror_test(seq, label):
        n = len(seq)
        half = n // 2
        eq = sum(1 for i in range(half) if seq[i] == seq[n - 1 - i])
        at = sum(1 for i in range(half) if (seq[i] + seq[n - 1 - i]) % N == N - 1)
        exp = half / N
        sd = math.sqrt(half * (1 / N) * (1 - 1 / N))
        if abs(eq - exp) > 3 * sd or abs(at - exp) > 3 * sd:
            print(f"  {label}: eq z={(eq-exp)/sd:+.2f} atbash z={(at-exp)/sd:+.2f} ***")
    mirror_test(stream, "whole text")
    for si, s in enumerate(sections):
        mirror_test(s, f"section {si}")
    for pi, p in enumerate(pages):
        if len(p) > 100:
            mirror_test(p, f"page {pi}")
    print("  (only >3 sigma shown)")

    print("\n=== 7. SENTENCES ===")
    print(f"  sentence separators: {seps.count('s')}")


if __name__ == "__main__":
    main()
