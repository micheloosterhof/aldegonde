#!/usr/bin/env python3
"""Battery 11: mechanism kill-table.

Simulate candidate cipher mechanisms on Markov-runeglish plaintext and
compare their statistical fingerprint against the unsolved LP corpus.
"""
import collections
import math
import random
from lp_structure import parse, flat, nioc, N, R2I

random.seed(2026)
pages = parse("data/page0-58.txt")[:55]
LPs = flat(pages)
n = len(LPs)

# Markov-1 runeglish generator
big = collections.defaultdict(collections.Counter)
uni = collections.Counter()
with open("src/aldegonde/data/ngrams/runeglish/bigrams.txt") as f:
    for line in f:
        g, c = line.split()
        g = g.replace("ᛂ", "ᛄ")
        big[R2I[g[0]]][R2I[g[1]]] += int(c)
        uni[R2I[g[0]]] += int(c)

def gen_plain(total):
    out = [random.choices(range(N), weights=[uni[i] for i in range(N)])[0]]
    while len(out) < total:
        ws = [big[out[-1]][j] for j in range(N)]
        out.append(random.choices(range(N), weights=ws)[0])
    return out

def fingerprint(c):
    m = len(c)
    cnt = collections.Counter(c)
    chi_u = sum((cnt[i] - m / N) ** 2 / (m / N) for i in range(N))
    d0 = sum(1 for i in range(m - 1) if c[i] == c[i + 1])
    diffs = collections.Counter((c[i + 1] - c[i]) % N for i in range(m - 1))
    off = m - 1 - diffs[0]
    chi_off = sum((diffs[k] - off / 28) ** 2 / (off / 28) for k in range(1, N))
    d2 = sum(1 for i in range(m - 2) if c[i] == c[i + 2])
    z2 = (d2 - (m - 2) / N) / math.sqrt((m - 2) * (1 / N) * (1 - 1 / N))
    # max periodic avg-column IoC p=2..40
    mx = 0.0
    for p in range(2, 41):
        avg = sum(nioc(c[i::p]) for i in range(p)) / p
        mx = max(mx, avg)
    prs = [(c[i], c[i + 1]) for i in range(m - 1)]
    cc = collections.Counter(prs)
    dig = sum(v * (v - 1) for v in cc.values()) / (len(prs) * (len(prs) - 1)) * N * N
    return nioc(c), chi_u, 100 * d0 / (m - 1), chi_off, dig, z2, mx

def row(name, c):
    io, chi_u, dbl, chi_off, dig, z2, mx = fingerprint(c)
    print(f"{name:34s} {io:6.3f} {chi_u:7.1f} {dbl:6.2f} {chi_off:7.1f} {dig:6.3f} {z2:+5.1f} {mx:6.3f}")

print(f"{'mechanism':34s} {'nIoC':>6s} {'uniChi':>7s} {'dbl%':>6s} {'offChi':>7s} {'digIoC':>6s} {'lag2z':>5s} {'maxPer':>6s}")
print("-" * 86)
row("LP unsolved corpus (target)", LPs)
print("-" * 86)

plain = gen_plain(n)
key_text = gen_plain(n)  # for running-key
row("plaintext itself", plain)

# --- algebraic / classical families ---
perm1 = list(range(N)); random.shuffle(perm1)
perm2 = list(range(N)); random.shuffle(perm2)

row("OTP (control)", [(p + random.randrange(N)) % N for p in plain])
ks = [random.randrange(N)]
while len(ks) < n:
    x = random.randrange(N)
    if x != ks[-1]:
        ks.append(x)
row("no-repeat key OTP (k[i]!=k[i-1])", [(plain[i] + ks[i]) % N for i in range(n)])

# running key, plain Vigenere TR and mixed (quagmire) TR
row("running key Vigenere", [(plain[i] + key_text[i]) % N for i in range(n)])
row("running key quagmire s(p)+t(k)", [(perm1[plain[i]] + perm2[key_text[i]]) % N for i in range(n)])
row("running key Beaufort", [(key_text[i] - plain[i]) % N for i in range(n)])

# plaintext autokey, primer length L
for L in (1, 3, 7):
    primer = [random.randrange(N) for _ in range(L)]
    ext = primer + plain
    row(f"plaintext autokey L={L}", [(plain[i] + ext[i]) % N for i in range(n)])

# key autokey: k[i] = k[i-1] + p[i-1]
k = random.randrange(N)
out = []
for i, p in enumerate(plain):
    out.append((p + k) % N)
    k = (k + p) % N
row("key autokey k+=p", out)

# ciphertext-fed additive feedback + strong key  (popular proposal class)
prev = 0
out = []
for p in plain:
    c = (p + prev + random.randrange(N)) % N
    out.append(c)
    prev = c
row("c=p+c_prev+random k", out)

# ciphertext autokey mixed TR
prev = 0
out = []
for p in plain:
    c = perm1[(p + prev) % N]
    out.append(c)
    prev = c
row("ciphertext autokey mixed TR", out)

# progressive quagmire: c = perm(p) + i
row("progressive quagmire perm(p)+i", [(perm1[plain[i]] + i) % N for i in range(n)])

# Gromark-29: chain-addition digits, mixed alphabet
dig5 = [random.randrange(10) for _ in range(5)]
ks = dig5[:]
while len(ks) < n:
    ks.append((ks[-5] + ks[-4]) % 10)
row("Gromark (chain-addition digits)", [(perm1[plain[i]] + ks[i]) % N for i in range(n)])

# Hill 2x2 mod 29
while True:
    a, b, c_, d = (random.randrange(N) for _ in range(4))
    if (a * d - b * c_) % N != 0:
        break
out = []
for i in range(0, n - 1, 2):
    p1, p2 = plain[i], plain[i + 1]
    out.append((a * p1 + b * p2) % N)
    out.append((c_ * p1 + d * p2) % N)
row("Hill 2x2", out)

# Chaocipher-29
def chao_encrypt(plain):
    left = list(range(N)); random.shuffle(left)   # cipher wheel
    right = list(range(N)); random.shuffle(right) # plain wheel
    NAD = 14
    out = []
    for p in plain:
        i = right.index(p)
        c = left[i]
        out.append(c)
        # permute left: rotate c to zenith, extract pos1, insert at nadir
        j = left.index(c)
        left = left[j:] + left[:j]
        x = left.pop(1)
        left.insert(NAD, x)
        # permute right: rotate p to zenith, rotate 1 more, extract pos2, insert at nadir
        j = right.index(p)
        right = right[j:] + right[:j]
        right = right[1:] + right[:1]
        x = right.pop(2)
        right.insert(NAD, x)
    return out
row("Chaocipher-29", chao_encrypt(plain))

# --- selection / rejection family ---
# S1: skip key letter on collision (strong random key)
out = []
prev = None
ks = [random.randrange(N) for _ in range(2 * n)]
j = 0
for p in plain:
    c = (p + ks[j]) % N
    j += 1
    if c == prev:
        c = (p + ks[j]) % N
        j += 1
    out.append(c)
    prev = c
row("S1 skip-key-on-collision", out)

# S2: strict re-roll + 19% lapse
out = []
prev = None
for p in plain:
    c = (p + random.randrange(N)) % N
    if c == prev and random.random() < 0.81:
        while c == prev:
            c = (p + random.randrange(N)) % N
    out.append(c)
    prev = c
row("S2 reroll, 19% lapse", out)

# S3: two keys, use B if A collides
out = []
prev = None
for p in plain:
    c = (p + random.randrange(N)) % N
    if c == prev:
        c = (p + random.randrange(N)) % N
    out.append(c)
    prev = c
row("S3 two-stream choice", out)

# deletion: OTP then delete 81% of doublet partners
otp = [(p + random.randrange(N)) % N for p in gen_plain(int(n * 1.05))]
out = []
for x in otp:
    if out and x == out[-1] and random.random() < 0.81:
        continue
    out.append(x)
row("post-encryption deletion 81%", out[:n])
