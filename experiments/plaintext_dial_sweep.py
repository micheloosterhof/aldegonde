# ABOUTME: Sweeps the odometer Quagmire with its inner dial moved to the plaintext
# ABOUTME: side, the one shift-dial family that passes the word-position test.
"""The odometer with the inner dial on the plaintext side.

`quagmire-odometer.md` puts both dials inside the keyed alphabet's coordinates:

    c = ( K[ (pos_K(p) + a_w + S_k) mod 29 ] + b_w ) mod 29

so the inner dial cancels from every within-word relation, and the relation is one of
five shifts conjugated by K. `within-word-relation-is-position-flat.md` (row C9) finds
the body's within-word coincidences carry no word-position structure, and that family
reads H 70 on start-end classes against the body's 29 (0 of 100 draws). Moving the
inner dial to the plaintext,

    c = ( K[ (pos_K((p + a_w) mod 29) + S_k) mod 29 ] + b_w ) mod 29

conjugates the relation by a different shift in every word, and the family reads
H 21 / 45 (P = 0.13 / 0.05): it fits. Everything else is the odometer: the dials on a
carry, the clock running on through word breaks, the doublet preventer advancing the
clock on a would-be repeat, and exactly one zero offset in the schedule.

The sweep is `dodge_priority_sweep` with one change. Its kernel indexes the log table
by (clock phase, inner dial, candidate), so the cipher lives entirely in the table:

    original   tab[k][a][z] = log f( K[ pos_K(z) - a - S_k ] )
    here       tab[k][a][z] = log f( K[ pos_K(z) - S_k ] - a )

Self-test (`--selftest`): the table decrypts a planted variant ciphertext exactly, the
planted schedule is in the generator, and the planted key ranks first against sampled
wrong schedules. `--nproc N` runs the sweep over 3301's own vocabulary.
"""

from __future__ import annotations

import heapq
import json
import random
import sys
import tempfile
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import dodge_priority_sweep as base  # noqa: E402
from base_free_verifier import log_frequencies  # noqa: E402
from dodge_priority_sweep import (  # noqa: E402
    KEEP,
    KEEP_PER_TASK,
    TASKS,
    Corpus,
    _lens,
    _prepare,
    surviving_schedules,
)
from pure_quagmire_restart import running  # noqa: E402

M = 29
OUT = ROOT / "experiments" / "plaintext_dial_candidates.jsonl"


def encipher(plain, K, offsets, start, phases: list[int] | None = None):
    """c = K[pos_K(p + a_w) + S_k] + b_w; dials on a carry, clock running on, dodge.

    `phases`, if given, receives the clock phase each rune was finally emitted at.
    """
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    a, b = start
    out, previous, clock = [], None, 0
    for word in plain:
        cipher_word = []
        for p in word:
            c = (K[(pos[(p + a) % M] + S[clock % 5]) % M] + b) % M
            if c == previous:
                clock += 1
                c = (K[(pos[(p + a) % M] + S[clock % 5]) % M] + b) % M
            if phases is not None:
                phases.append(clock % 5)
            cipher_word.append(c)
            previous = c
            clock += 1
        out.append(cipher_word)
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    return out


def log_table(K, offsets, logf) -> np.ndarray:
    """tab[k, a, z] = log f( K[pos_K(z) - S_k] - a )."""
    pos = np.empty(M, dtype=np.int64)
    pos[np.asarray(K)] = np.arange(M)
    S = np.asarray(running(offsets))
    Karr = np.asarray(K)
    z = np.arange(M)
    inner = Karr[(pos[z][None, :] - S[:, None]) % M]  # (5, M): K[pos(z) - S_k]
    plain = (inner[:, None, :] - np.arange(M)[None, :, None]) % M  # (5, M, M)
    return np.ascontiguousarray(logf[plain], dtype=np.float32)


def score_key(K, scheds, corpus: Corpus, logf, *, keep: int):
    """Best (score, schedule, inner dial) over every schedule and its 29 inner dials."""
    best: list[tuple[float, list[int], int]] = []
    for sched in scheds:
        offsets = [int(x) for x in sched]
        scores = corpus.score(log_table(K, offsets, logf))
        top = int(scores.argmax())
        item = (float(scores[top]), offsets, top)
        if len(best) < keep:
            heapq.heappush(best, item)
        elif item[0] > best[0][0]:
            heapq.heapreplace(best, item)
    return best


def _work(task):
    """Sweep one slice of keyed alphabets: generate its schedules, score them."""
    name, lo, step = task
    best: list[tuple[float, str, list[int], list[int], int]] = []
    tested = 0
    W = base._W  # filled by `_prepare` in the forking parent  # noqa: SLF001
    for kwname, K in W["keys"][lo::step]:
        scheds = surviving_schedules(K, W["tables"], W["bands"])
        if not len(scheds):
            continue
        tested += len(scheds) * M
        for score, offsets, dial in score_key(
            K, scheds, W["corpus"], W["logf"], keep=KEEP_PER_TASK
        ):
            item = (score, kwname, list(K), offsets, dial)
            if len(best) < KEEP_PER_TASK:
                heapq.heappush(best, item)
            elif score > best[0][0]:
                heapq.heapreplace(best, item)
    return name, tested, best


def selftest(sample: int = 2000) -> None:
    from pure_quagmire_restart import matched_register, schedule  # noqa: PLC0415
    from quagmire_runner import (  # noqa: PLC0415
        PROSE_CACHE,
        build_register,
        build_setup,
        load_register,
    )
    from quagmire_schedule_census import (  # noqa: PLC0415
        lp_words,
        observed_rates,
        wilson,
    )
    from zero_offset_census import diluted_band  # noqa: PLC0415

    rng = random.Random(3301)
    lens = _lens()
    _words, _vocab, T1, lo1, hi1, _s = build_setup(PROSE_CACHE, lens, vocab=["the"])
    _T1, T4, T6, _cross = build_register(PROSE_CACHE, lens)
    obs = observed_rates(lp_words())
    bands = (
        (lo1, hi1),
        diluted_band(*wilson(*obs[4]), 4),
        diluted_band(*wilson(*obs[6]), 6),
    )
    pools, _t, _f = load_register(PROSE_CACHE)
    logf = log_frequencies()

    K = rng.sample(range(M), M)
    offsets = schedule(rng)
    dials = (rng.randrange(M), rng.randrange(M))
    plain = matched_register(rng, lens, pools)
    phases: list[int] = []
    cipher = encipher(plain, K, offsets, dials, phases)
    print(f"planted: schedule {offsets}, dials {dials}")

    # 1. the table is the cipher's inverse: at the phase each rune was emitted at, the
    # implied plaintext is the plaintext, and the table holds its log frequency
    tab = log_table(K, offsets, logf)
    assert np.isfinite(tab).all()
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    a, b, i, dodged = dials[0], dials[1], 0, 0
    for pw, cw in zip(plain, cipher):
        for p, c in zip(pw, cw):
            z = (c - b) % M
            implied = (K[(pos[z] - S[phases[i]]) % M] - a) % M
            assert implied == p, "the table does not invert the cipher"
            assert tab[phases[i], a, z] == np.float32(logf[p])
            i += 1
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    dodged = sum(
        1 for j in range(1, len(phases)) if phases[j] != (phases[j - 1] + 1) % 5
    )
    print(f"table inverts the cipher at every rune; {dodged} dodges in {i} runes")

    # 2. coverage
    scheds = surviving_schedules(K, (T1, T4, T6), bands)
    hit = [i for i, s in enumerate(scheds) if list(s) == offsets]
    print(
        f"{len(scheds):,} schedules in the generator; planted {'IN' if hit else 'NOT IN'}"
    )
    assert hit, "the generator does not emit the planted schedule"

    # 3. sensitivity
    corpus = Corpus(cipher)
    if sample and sample < len(scheds):
        pick = np.random.default_rng(3301).choice(len(scheds), sample, replace=False)
        scheds = np.concatenate([scheds[np.sort(pick)], scheds[hit[:1]]])
    start = time.time()
    best = score_key(K, scheds, corpus, logf, keep=len(scheds))
    dt = time.time() - start
    ranked = sorted(best, reverse=True)
    rank = next(i for i, (_s, o, _d) in enumerate(ranked) if o == offsets)
    truth = ranked[rank]
    others = np.array([s for s, o, _d in ranked if o != offsets])
    z = (truth[0] - others.mean()) / others.std()
    print(
        f"SENSITIVITY: planted key ranks {rank + 1} of {len(ranked)}, score "
        f"{truth[0]:+.4f} vs wrong mean {others.mean():+.4f} max {others.max():+.4f}"
        f" (z = {z:+.1f}); recovered inner dial {truth[2]}, planted {dials[0]}"
    )
    rate = len(scheds) * M / dt
    print(
        f"{rate:,.0f} keys/s/core on {len(scheds):,} schedules x {M} dials in {dt:.1f}s"
    )
    assert rank == 0, "the planted key does not rank first"
    assert truth[2] == dials[0], "the inner dial is not recovered"
    print("self-test passed")


def run(nproc: int) -> None:
    _words, keys = _prepare(_lens())
    print(f"{len(keys):,} keyed alphabets from 3301's vocabulary, {nproc} workers")
    tasks = [(f"pdial-{i}", i, TASKS) for i in range(TASKS)]
    progress = Path(tempfile.gettempdir()) / "plaintext_dial_progress.jsonl"
    tested, best, finished = 0, [], set()
    if progress.exists():
        for line in progress.read_text().splitlines():
            rec = json.loads(line)
            finished.add(rec["task"])
            tested += rec["tested"]
            best += rec["best"]
        print(f"resuming: {len(finished)} tasks already in {progress}", flush=True)
    todo = [t for t in tasks if t[0] not in finished]
    start = time.time()
    with progress.open("a") as log, get_context("fork").Pool(nproc) as pool:
        for done, (name, count, top) in enumerate(pool.imap_unordered(_work, todo), 1):
            tested += count
            best = heapq.nlargest(
                KEEP, best + [list(t) for t in top], key=lambda t: t[0]
            )
            log.write(json.dumps({"task": name, "tested": count, "best": top}) + "\n")
            log.flush()
            if done % 5 == 0 or done == len(todo):
                rate = tested / max(1e-9, time.time() - start)
                print(
                    f"  {done}/{len(todo)} tasks, {tested:,} keys, best {best[0][0]:+.4f},"
                    f" {rate:,.0f} keys/s, {(time.time() - start) / 60:.1f} min",
                    flush=True,
                )
    print(f"\nDONE: {tested:,} keys in {(time.time() - start) / 60:.1f} min")
    with OUT.open("w") as fout:
        for score, kwname, K, sched, dial in best:
            print(f"  {score:+.4f}  {kwname:<28} sched {sched} dial {dial}")
            fout.write(
                json.dumps(
                    {
                        "score": score,
                        "keyword": kwname,
                        "K": K,
                        "sched": sched,
                        "dial": dial,
                    }
                )
                + "\n"
            )
    print(f"written to {OUT}; a true key scores near +1.0, wrong keys below +0.65")


def decrypt(cipher_words, K, offsets, a0, *, window: int = 18):
    """Read the body under a key, fitting the outer dial and each window's phase.

    The preventer moves the clock, so inside each window the phase is unknown; every
    window is read at all five phases and the one scoring best on runeglish quadgrams
    is kept. The outer dial b0 is chosen the same way over the whole text. Returns
    (plaintext words, nats per rune above a shuffled baseline, b0).
    """
    from aldegonde import c3301  # noqa: PLC0415

    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    runes = [c for w in cipher_words for c in w]
    owner = [w for w, cw in enumerate(cipher_words) for _ in cw]
    dial_a = []
    a, b_shift = a0, 0
    for _ in cipher_words:
        dial_a.append(a)
        a = (a + 1) % M
        if a == 0:
            b_shift += 1
    carries = [0] * len(cipher_words)
    a, k = a0, 0
    for w in range(len(cipher_words)):
        carries[w] = k
        a = (a + 1) % M
        if a == 0:
            k += 1

    def read(b0):
        out = []
        for lo in range(0, len(runes), window):
            best, best_text = -1e30, None
            for ph in range(5):
                text = []
                for i in range(lo, min(lo + window, len(runes))):
                    w = owner[i]
                    z = (runes[i] - b0 - carries[w]) % M
                    p = (K[(pos[z] - S[(ph + i - lo) % 5]) % M] - dial_a[w]) % M
                    text.append(p)
                score = c3301.quadgramscore(
                    "".join(c3301.CICADA_ALPHABET[x] for x in text)
                )
                if score > best:
                    best, best_text = score, text
            out.extend(best_text)
        return out

    best_b, best_score, best_text = 0, -1e30, None
    for b0 in range(M):
        text = read(b0)
        score = c3301.quadgramscore("".join(c3301.CICADA_ALPHABET[x] for x in text))
        if score > best_score:
            best_b, best_score, best_text = b0, score, text
    rng = random.Random(1)
    shuffled = best_text[:]
    rng.shuffle(shuffled)
    baseline = c3301.quadgramscore("".join(c3301.CICADA_ALPHABET[x] for x in shuffled))
    words, i = [], 0
    for cw in cipher_words:
        words.append(best_text[i : i + len(cw)])
        i += len(cw)
    return words, (best_score - baseline) / len(runes), best_b


def decrypt_selftest() -> None:
    from pure_quagmire_restart import matched_register, schedule  # noqa: PLC0415
    from quagmire_runner import PROSE_CACHE, load_register  # noqa: PLC0415

    rng = random.Random(11)
    lens = _lens()
    pools, _t, _f = load_register(PROSE_CACHE)
    K = rng.sample(range(M), M)
    offsets = schedule(rng)
    dials = (rng.randrange(M), rng.randrange(M))
    plain = matched_register(rng, lens, pools)
    cipher = encipher(plain, K, offsets, dials)
    words, gain, b0 = decrypt(cipher, K, offsets, dials[0])
    right = sum(p == q for pw, qw in zip(plain, words) for p, q in zip(pw, qw))
    total = sum(len(w) for w in plain)
    print(
        f"planted key read back: {right} of {total} runes, b0 {b0} (planted {dials[1]}), {gain:+.2f} nats/rune over shuffled"
    )
    # the window phases are fitted, so a few runes around each dodge read wrong
    assert b0 == dials[1] and right > 0.8 * total
    wrong = decrypt(cipher, rng.sample(range(M), M), schedule(rng), rng.randrange(M))
    print(f"a wrong key reads {wrong[1]:+.2f} nats/rune over shuffled")
    assert wrong[1] < gain / 3
    print("decrypt self-test passed")


def show(path: Path = OUT, top: int = 3) -> None:
    """Decrypt the best candidates in the sweep's output and print the opening."""
    from quagmire_schedule_census import lp_words  # noqa: PLC0415

    from aldegonde import c3301  # noqa: PLC0415

    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows.sort(key=lambda r: -r["score"])
    body = lp_words()
    for r in rows[:top]:
        words, gain, b0 = decrypt(body, r["K"], r["sched"], r["dial"])
        opening = " ".join(c3301.decode_english(w) for w in words[:40])
        print(
            f"{r['score']:+.4f} {r['keyword']} sched {r['sched']} dial {r['dial']} b0 {b0}"
        )
        print(f"   {gain:+.2f} nats/rune over shuffled: {opening}")


def main() -> None:
    if "--decrypt-selftest" in sys.argv:
        decrypt_selftest()
        return
    if "--show" in sys.argv:
        show()
        return
    if "--selftest" in sys.argv:
        sample = 2000
        for i, a in enumerate(sys.argv):
            if a == "--sample" and i + 1 < len(sys.argv):
                sample = int(sys.argv[i + 1])
        selftest(sample)
        return
    nproc = 4
    for i, a in enumerate(sys.argv):
        if a == "--nproc" and i + 1 < len(sys.argv):
            nproc = int(sys.argv[i + 1])
    run(nproc)


if __name__ == "__main__":
    main()
