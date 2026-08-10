# ABOUTME: Per-section word/sentence-length analysis of the unsolved LP lattice
# ABOUTME: vs the author's solved register: distributions, sentences, ordering.
import re, random, math, statistics
RUNE = re.compile(r'[ᚠ-᛿]')
random.seed(3)

def words_and_marks(txt):
    txt = txt.replace('/', '').replace('\n', '')
    words, sent_lens, cur = [], [], 0
    w = []
    for ch in txt + '-':
        if RUNE.match(ch):
            w.append(ch)
        elif ch in '①-.%&$':
            if w:
                words.append(len(w)); cur += 1; w = []
            if ch == '.' and cur:
                sent_lens.append(cur); cur = 0
    return words, sent_lens

def ks(a, b):
    sa, sb = sorted(a), sorted(b)
    allv = sorted(set(sa + sb))
    D = max(abs(sum(1 for x in sa if x <= v)/len(sa) - sum(1 for x in sb if x <= v)/len(sb)) for v in allv)
    lam = (D + 0) * math.sqrt(len(sa)*len(sb)/(len(sa)+len(sb)))
    p = 2 * sum((-1)**(k-1) * math.exp(-2*k*k*lam*lam) for k in range(1, 101))
    return D, max(min(p, 1.0), 0.0)

def lag1(ws, nperm=300):
    if len(ws) < 30: return 0.0, 0.0
    def ac(v):
        m = statistics.mean(v)
        num = sum((v[i]-m)*(v[i+1]-m) for i in range(len(v)-1))
        den = sum((x-m)**2 for x in v)
        return num/den
    obs = ac(ws)
    null = []
    c = ws[:]
    for _ in range(nperm):
        random.shuffle(c)
        null.append(ac(c))
    return obs, (obs - statistics.mean(null)) / statistics.stdev(null)

# references
m = open('/Users/mich/src/aldegonde/data/liber-primus__transcription--master.txt').read()
count = cut = 0
for i, ch in enumerate(m):
    if RUNE.match(ch):
        count += 1
        if count == 2797: cut = i+1; break
solved_w, solved_s = words_and_marks(m[:cut])

text = open('/Users/mich/src/aldegonde/data/page0-58.txt').read()
secs = [s for s in text.split('$') if RUNE.search(s)][:10]
uns_w_all = []
for s in secs: uns_w_all += words_and_marks(s)[0]

def row(name, ws, ss):
    short = sum(1 for x in ws if x <= 2)/len(ws)
    D1, p1 = ks(ws, solved_w)
    D2, p2 = ks(ws, uns_w_all)
    a, z = lag1(ws)
    sent = statistics.mean(ss) if ss else float('nan')
    print(f"{name:>10}: {len(ws):4d} words, mean {statistics.mean(ws):.2f}, short {short:.0%}, "
          f"KSvsSolved D={D1:.3f} p={p1:.3f}, KSvsRest p={p2:.2f}, "
          f"lag1 ac {a:+.3f} (z={z:+.1f}), sent {sent:.1f}w x{len(ss)}")

print(f"    solved: {len(solved_w)} words, mean {statistics.mean(solved_w):.2f}, "
      f"short {sum(1 for x in solved_w if x<=2)/len(solved_w):.0%}, "
      f"sentences mean {statistics.mean(solved_s):.1f} words x{len(solved_s)}")
print()
for i, s in enumerate(secs):
    ws, ss = words_and_marks(s)
    if len(ws) < 30: continue
    row(f"sec {i}", ws, ss)
