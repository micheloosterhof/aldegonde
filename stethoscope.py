#!/usr/bin/env pypy3

from collections import Counter, defaultdict
import math
import random
import sys
from typing import Dict, List

import gematria
import lp_section_data as lp

from lib import *

g = gematria.gematria

s1="".join(lp.section1["all_words"])
s2="".join(lp.section2["all_words"])
s3="".join(lp.section3["all_words"])
s4="".join(lp.section4["all_words"])
s5="".join(lp.section5["all_words"])
s6="".join(lp.section6["all_words"])
s7="".join(lp.section7["all_words"])
s8="".join(lp.section8["all_words"])
s9="".join(lp.section9["all_words"])
s10="".join(lp.section10["all_words"])
s11="".join(lp.section11["all_words"])
s12="".join(lp.section12["all_words"])
s13="".join(lp.section13["all_words"])
s=s1+s2+s3+s4+s5+s6+s7+s8+s9+s10+s11+s12+s13
sl = list(s)
segments = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13]

# RL is a random rune list same size as all the other runes
rl = []
for i in range(0, len(s)):
   rl.append(random.randrange(0,MAX))

# rsegments are random lists, same size as the LP
rsegments = []
for i in segments:
    l = len(i)
    f = prime_factors(l)
    r = []
    for i in range(0, l):
        r.append(random.randrange(0,MAX))
    rsegments.append(r)

# GL are the runes in 0-28 format, in one big list
gl = []
for i in sl:
     gl.append(g.rune_to_position_forward_dict[i])

# SGL are the runes in 0-28 format by segment, list of a list by chapter
sgl = []
for i in segments:
    bgl = []
    for j in i:
        bgl.append(g.rune_to_position_forward_dict[j])
    sgl.append(bgl)


N=len(sgl)
for i in range(0,N):
  gl = sgl[i]
  rg = rsegments[i]

  print(f"#### segment {i+1} ######")
  print(f"len {len(gl)} factors:{prime_factors(len(gl))}" )
  print(f"ioc={ioc(gl):.3f}, random ic={ioc(rg):.3f}")

  print("kappa test")
  kappa(gl)

  doublets(gl)

  # calculate some random data ic's
  ar = []
  for i in range(0,10000):
      ar.append(random.randrange(0,MAX))
  rioc2 = ioc2(ar)
  rioc3 = ioc3(ar)

  print(f"ioc2={ioc2(gl,cut=0):.3f} ioc2a={ioc2(gl,cut=1):.3f}, ioc2b={ioc2(gl,cut=2):.3f}, avg rnd ioc2={rioc2:.3f}")
  print(f"ioc3={ioc3(gl,cut=0):.3f} ioc3a={ioc3(gl,cut=1):.3f}, ioc3b={ioc3(gl,cut=2):.3f}, ioc3c={ioc3(gl,cut=3):.3f}, avg rnd ioc3={rioc3:.3f}")
  print(f"isomorphs length 3: {isomorph2(gl,min=3,max=3)}")
  print(f"isomorphs length 4: {isomorph2(gl,min=4,max=4)}")
  print(f"isomorphs length 5: {isomorph2(gl,min=5,max=5)}")

