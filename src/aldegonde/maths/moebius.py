# This code is contributed by Manish Shaw(manishshaw1)
# Python Program to
# evaluate Mobius def
# M(N) = 1 if N = 1
# M(N) = 0 if any
# prime factor of
# N is contained twice
# M(N) = (-1)^(no of
# distinct prime factors)


# def to check if
# n is prime or not
def isPrime(n: int) -> bool:
    if n < 2:
        return False
    return all(not (i * i <= n and n % i == 0) for i in range(2, n + 1))


def moebius(N: int) -> int:
    # Base Case
    if N == 1:
        return 1

    # For a prime factor i
    # check if i^2 is also
    # a factor.
    p = 0
    for i in range(1, N + 1):
        if N % i == 0 and isPrime(i):
            # Check if N is
            # divisible by i^2
            if N % (i * i) == 0:
                return 0
            # i occurs only once,
            # increase p
            p = p + 1

    # All prime factors are
    # contained only once
    # Return 1 if p is even
    # else -1
    if p % 2 != 0:
        return -1
    return 1


if __name__ == "__main__":
    N = 17
    print(f"Möbius defs M(N) at N = {N} is: {moebius(N)}", end="\n")
    print(f"Möbius defs M(N) at N = {25} is: {moebius(25)}", end="\n")
    print(f"Möbius defs M(N) at N = {6} is: {moebius(6)}", end="\n")
