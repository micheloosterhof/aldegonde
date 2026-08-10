# ABOUTME: Tests text-direction via '.' marks: compares word lengths BEFORE vs
# ABOUTME: AFTER each mark against a random-word null, unsolved vs solved pages.
import random
import re
import statistics
from pathlib import Path

from aldegonde import c3301

BOUNDARY_CHARS = frozenset(
    c3301.MARK_CHARS + "%&$" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS
)

RUNE = re.compile(r"[ᚠ-᛿]")
random.seed(1)


def tokens(txt):
    """Return list of (word, followed_by_mark) preserving order; merge across / and newline."""
    txt = txt.replace("/", "").replace("\n", "")
    out = []
    word = []
    for ch in txt:
        if RUNE.match(ch):
            word.append(ch)
        elif ch in BOUNDARY_CHARS:
            if word:
                out.append(["".join(word), ch in c3301.CLUSTER_MARKS])
                word = []
            elif ch in c3301.CLUSTER_MARKS and out:
                out[-1][1] = True  # mark directly after another delimiter
    if word:
        out.append(["".join(word), False])
    return out


def analyze(name, toks):
    words = [w for w, _ in toks]
    lens = [len(w) for w in words]
    before = [len(toks[i][0]) for i in range(len(toks)) if toks[i][1]]
    after = [len(toks[i + 1][0]) for i in range(len(toks) - 1) if toks[i][1]]

    def z(sample):
        n = len(sample)
        obs = statistics.mean(sample)
        means = [statistics.mean(random.sample(lens, n)) for _ in range(5000)]
        mu, sd = statistics.mean(means), statistics.stdev(means)
        return obs, (obs - mu) / sd

    ob, zb = z(before)
    oa, za = z(after)
    short_b = sum(1 for x in before if x <= 2) / len(before)
    short_a = sum(1 for x in after if x <= 2) / len(after)
    base_short = sum(1 for x in lens if x <= 2) / len(lens)
    print(
        f"{name}: {len(words)} words, mean {statistics.mean(lens):.2f}, "
        f"{len(before)} marks; short-word baseline {base_short:.1%}"
    )
    print(f"  before-mark: mean {ob:.2f}  z={zb:+.2f}  short {short_b:.1%}")
    print(f"  after-mark:  mean {oa:.2f}  z={za:+.2f}  short {short_a:.1%}")


# unsolved clean corpus: sections 0-9 of page0-58
text = Path("/Users/mich/src/aldegonde/data/page0-58.txt").read_text()
secs = [s for s in text.split("$") if RUNE.search(s)][:10]
toks = []
for s in secs:
    toks.extend(tokens(s))
analyze("unsolved (clean 0-9)", toks)

# solved pages: first 2797 runes of the master transcription
m = Path(
    "/Users/mich/src/aldegonde/data/liber-primus__transcription--master.txt"
).read_text()
count = 0
cut = 0
for i, ch in enumerate(m):
    if RUNE.match(ch):
        count += 1
        if count == 2797:
            cut = i + 1
            break
analyze("solved (first 2797 runes)", tokens(m[:cut]))
