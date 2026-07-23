# ABOUTME: Scans the clean LP corpus for regions resembling English (runeglish)
# ABOUTME: via sliding-window nIoC and trigram fitness, vs shuffled null and Parable.
import re, random, math, statistics
from collections import Counter

RUNE = re.compile(r'[ᚠ-᛿]')
random.seed(7)

text = open('/Users/mich/src/aldegonde/data/page0-58.txt').read()
all_secs = [s for s in text.split('$') if RUNE.search(s)]
secs = [''.join(RUNE.findall(s)) for s in all_secs[:10]]
parable = ''.join(RUNE.findall(all_secs[11]))
full = ''.join(secs)

# trigram log-prob table
tri = {}
total = 0
for line in open('/Users/mich/src/aldegonde/src/aldegonde/data/ngrams/runeglish/trigrams.txt'):
    g, c = line.split()
    tri[g] = int(c)
    total += int(c)
floor = math.log10(0.01 / total)
logp = {g: math.log10(c / total) for g, c in tri.items()}

def fitness(s):
    return statistics.mean(logp.get(s[i:i+3], floor) for i in range(len(s) - 2))

def nioc(s):
    c = Counter(s)
    n = len(s)
    return 29 * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))

print("calibration: Parable (plaintext, 95 runes) fitness %.3f, nIoC %.2f" % (fitness(parable), nioc(parable)))
print("full clean corpus: fitness %.3f, nIoC %.3f" % (fitness(full), nioc(full)))

print("\nper-section (0-9, title excluded):")
for i, s in enumerate(secs):
    if len(s) < 100: continue
    print("  sec %d: %5d runes  nIoC %.3f  fitness %.3f" % (i, len(s), nioc(s), fitness(s)))

W, STEP = 500, 100
def scan(s):
    return [(i, nioc(s[i:i+W]), fitness(s[i:i+W])) for i in range(0, len(s) - W + 1, STEP)]

obs = scan(full)
obs_max_ioc = max(x[1] for x in obs); obs_max_fit = max(x[2] for x in obs)
obs_min_fit = min(x[2] for x in obs)
best = max(obs, key=lambda x: x[2])

null_max_ioc, null_max_fit, null_min_fit = [], [], []
sh = list(full)
for _ in range(25):
    random.shuffle(sh)
    ns = scan(''.join(sh))
    null_max_ioc.append(max(x[1] for x in ns))
    null_max_fit.append(max(x[2] for x in ns))
    null_min_fit.append(min(x[2] for x in ns))

def rank(v, null, hi=True):
    beat = sum(1 for x in null if (x >= v if hi else x <= v))
    return f"{v:.3f} (null max-dist mean {statistics.mean(null):.3f}, P={beat}/{len(null)}"+")"

print(f"\nsliding windows ({W} runes, step {STEP}, n={len(obs)}):")
print("  max window nIoC:    ", rank(obs_max_ioc, null_max_ioc))
print("  max window fitness: ", rank(obs_max_fit, null_max_fit))
print("  min window fitness: ", rank(obs_min_fit, null_min_fit, hi=False))
print(f"  best-fitness window starts at rune {best[0]} (nIoC {best[1]:.3f}, fitness {best[2]:.3f})")

# per-section significance vs shuffled null (same boundaries)
bounds = []
off = 0
for s in secs:
    bounds.append((off, off + len(s)))
    off += len(s)
null_best = []
sh = list(full)
sec_scores = {i: [] for i in range(len(bounds))}
for _ in range(40):
    random.shuffle(sh)
    j = ''.join(sh)
    scores = [fitness(j[a:b]) for a, b in bounds if b - a >= 100]
    null_best.append(max(scores))
    for k, (a, b) in enumerate(bounds):
        if b - a >= 100:
            sec_scores[k].append(fitness(j[a:b]))
obs5 = fitness(full[bounds[5][0]:bounds[5][1]])
mu, sd = statistics.mean(sec_scores[5]), statistics.stdev(sec_scores[5])
print("section 5 fitness %.3f vs its null %.3f +/- %.3f (z=%+.1f)" % (obs5, mu, sd, (obs5-mu)/sd))
print("best-section score across 40 shuffled corpora: mean %.3f, max %.3f; observed best %.3f"
      % (statistics.mean(null_best), max(null_best), obs5))
print("P(shuffled best-section >= observed best) = %d/40" % sum(1 for x in null_best if x >= obs5))

# order vs composition: within-section shuffle preserves unigram makeup
uni = {}
utot = 0
for line in open('/Users/mich/src/aldegonde/src/aldegonde/data/ngrams/runeglish/unigrams.txt'):
    g, c = line.split()
    uni[g] = int(c); utot += int(c)
ulogp = {g: math.log10(c / utot) for g, c in uni.items()}
ufloor = math.log10(0.01 / utot)

print("\norder vs composition:")
for k in range(len(secs)):
    s = full[bounds[k][0]:bounds[k][1]]
    if len(s) < 300: continue
    ufit = statistics.mean(ulogp.get(ch, ufloor) for ch in s)
    obs = fitness(s)
    within = []
    ls = list(s)
    for _ in range(60):
        random.shuffle(ls)
        within.append(fitness(''.join(ls)))
    mu, sd = statistics.mean(within), statistics.stdev(within)
    print("  sec %d: unigram-fitness %.4f, trigram obs %.3f vs within-shuffle %.3f+/-%.3f (order z=%+.1f)"
          % (k, ufit, obs, mu, sd, (obs - mu) / sd))
