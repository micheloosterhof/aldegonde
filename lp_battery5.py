#!/usr/bin/env python3
"""Battery 5: keystream sweep + feedback-cipher models, scored by IoC."""
import collections
import math
from lp_structure import parse, flat, nioc, N
from aldegonde.maths import primes as ald_primes

pages = parse("data/page0-58.txt")
pages = pages[:56]  # drop known-plaintext Parable page
s = flat(pages)
n = len(s)

def sieve(limit):
    pr = []
    is_c = bytearray(limit)
    for i in range(2, limit):
        if not is_c[i]:
            pr.append(i)
            for j in range(i * i, limit, i):
                is_c[j] = 1
    return pr

PR = sieve(200000)[: n + 10]

def totient_prime(p):  # phi(p) = p-1
    return p - 1

# digit streams
PI = "14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196"
E = "71828182845904523536028747135266249775724709369995957496696762772407663035354759457138217852516642742746639193200305992181741359662904357290033429526059563073813232862794349076323382988075319525101901"

streams = {}
streams["index"] = list(range(n))
streams["index+1"] = list(range(1, n + 1))
streams["primes"] = PR[:n]
streams["totient(primes)"] = [p - 1 for p in PR[:n]]
streams["prime gaps"] = [PR[i + 1] - PR[i] for i in range(n)]
fib = [1, 1]
while len(fib) < n:
    fib.append(fib[-1] + fib[-2])
streams["fibonacci"] = fib[:n]
streams["pi digits"] = [int(c) for c in (PI * (n // len(PI) + 1))[:n]]
streams["e digits"] = [int(c) for c in (E * (n // len(E) + 1))[:n]]
streams["triangular"] = [i * (i + 1) // 2 for i in range(n)]
streams["squares"] = [i * i for i in range(n)]
streams["2^i"] = [pow(2, i, N) for i in range(n)]
streams["3^i"] = [pow(3, i, N) for i in range(n)]

print("=== additive keystream sweep (whole corpus), flag nIoC>1.05 ===")
for name, k in streams.items():
    for sign, op in [("-", lambda c, kk: (c - kk) % N), ("+", lambda c, kk: (c + kk) % N)]:
        p = [op(s[i], k[i]) for i in range(n)]
        v = nioc(p)
        flag = "  <<<<" if v > 1.05 else ""
        print(f"{name:18s} c{sign}k: {v:.4f}{flag}", end="   ")
    print()

print("\n=== same, restarting stream at each page, scored per page (count pages nIoC>1.2) ===")
for name, k in streams.items():
    for sign in ("-", "+"):
        hits = 0
        tot_ioc = 0.0
        for pg in pages:
            ps = [r for w in pg for r in w]
            if len(ps) < 50:
                continue
            kk = k[: len(ps)]
            p = [(ps[i] - kk[i]) % N if sign == "-" else (ps[i] + kk[i]) % N for i in range(len(ps))]
            v = nioc(p)
            tot_ioc += v
            if v > 1.2:
                hits += 1
        print(f"{name:18s} c{sign}k: pages>1.2: {hits:2d} mean {tot_ioc/56:.3f}", end="   ")
    print()

print("\n=== feedback models: derive candidate plaintext, score nIoC ===")
models = {
    "p=c[i]-c[i-1]": [(s[i] - s[i - 1]) % N for i in range(1, n)],
    "p=c[i]+c[i-1]": [(s[i] + s[i - 1]) % N for i in range(1, n)],
    "p=c[i-1]-c[i]": [(s[i - 1] - s[i]) % N for i in range(1, n)],
    "p=c[i]-c[i-1]-1": [(s[i] - s[i - 1] - 1) % N for i in range(1, n)],
    "p=c[i]-2c[i-1]": [(s[i] - 2 * s[i - 1]) % N for i in range(1, n)],
    "p=2c[i]-c[i-1]": [(2 * s[i] - s[i - 1]) % N for i in range(1, n)],
    "p=c[i]-c[i-2]": [(s[i] - s[i - 2]) % N for i in range(2, n)],
    "p=c[i]+c[i-1]+c[i-2]": [(s[i] + s[i - 1] + s[i - 2]) % N for i in range(2, n)],
    "p=c[i]-c[i-1]+c[i-2]": [(s[i] - s[i - 1] + s[i - 2]) % N for i in range(2, n)],
}
for name, p in models.items():
    print(f"{name:22s}: nIoC={nioc(p):.4f}")

print("\n=== multiplicative: p = a*c+b sweep doesn't change IoC; skip. ===")
print("=== running-key with the book itself: page j decrypted by page j-1 ===")
tot = []
for a, b in zip(pages, pages[1:]):
    fa = [r for w in a for r in w]
    fb = [r for w in b for r in w]
    L = min(len(fa), len(fb))
    tot += [(fb[i] - fa[i]) % N for i in range(L)]
print(f"c[pg+1]-c[pg]: nIoC={nioc(tot):.4f} (n={len(tot)})")

print("\n=== Gematria-value (prime) domain: map rune i -> i-th prime, look at mod arith ===")
GP = sieve(200)[:29]  # 2..109
gvals = [GP[r] for r in s]
# sum of word gematria mod small numbers
words = [w for p in pages for w in p]
for m in (29, 59, 28, 30):
    d = collections.Counter(sum(GP[r] for r in w) % m for w in words)
    mm = len(words)
    chi2 = sum((d[k] - mm / m) ** 2 / (mm / m) for k in range(m))
    print(f"word gematria-sum mod {m}: chi2={chi2:.1f} (df={m-1})")
