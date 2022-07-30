def primes(n):
    out = list()
    sieve = [True] * (n + 1)
    for p in range(2, n + 1):
        if sieve[p]:
            out.append(p)
            for i in range(p, n + 1, p):
                sieve[i] = False
    return out
