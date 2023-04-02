#!/usr/bin/env python

# Cohort 1st challenge
# 1. Detect Monoalphabetic Substitution Cipher
# 2. Assume shift cipher/atbash or combo and give most likely answer

# Implementation
# 1. Score with IOC to detect MASC, check if in range of normal language
# 2. Test shift/atbash combos and score with chisquare test
# 3. Print results

import sys
from aldegonde.stats import ioc
from aldegonde.stats import compare
from aldegonde.algorithm import masc

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

test = "THISISATESTOFTHEEMERGENCYBROADCASTSYSTEM"
ekey = masc.shiftedkey(alphabet, 3)
string = "".join(masc.masc_encrypt(test, ekey))

# if len(sys.argv) < 2:
#    print(f"Usage: {sys.argv[0]} <string>")
#    sys.exit()
#
# string = sys.argv[1]
#
print(f"INPUT: {string}")

str2 = "".join(string.split())

print(f"WHITESPACE REMOVED: {str2}")

ic = ioc.ioc(str2)

# ENGLISH = 0.0667
# FRENCH = 0.0778
# GERMAN = 0.0762
# SPANISH = 0.0770
# ITALIAN = 0.0738
# RUSSIAN = 0.0529

print(f"IOC={ic}")
print(f"English = 0.0667")

if abs(ic - 0.0667) < 0.003:
    print("close to english")
else:
    print("not close to english")

for shift in range(1, 26):
    print(f"{shift:02d}: ", end="")
    key = masc.shiftedkey(alphabet, shift)
    out = "".join(masc.masc_decrypt(str2, key))
    print(out, end=" ")
    score = compare.quadgramscore(out)
    print(f"score={score:05f}")
