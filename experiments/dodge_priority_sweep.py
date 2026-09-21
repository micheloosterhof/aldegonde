# ABOUTME: The zero-offset Quagmire-dodge sweep over 3301's own vocabulary, using the
# ABOUTME: dodge-aware compiled scorer; enumerates the schedules every old sweep masked out.
"""The search `quagmire-dodge.md` has pointed at for three revisions.

Every keyword sweep in this project required all five schedule offsets to be
non-zero. The dodge model needs exactly one of them to BE zero -- that is where the
doublet preventer fails, and it is what derives the 1/5 in the observed doublet rate.
So none of those sweeps could have found this family, whatever they scored.

Two prerequisites are now met and are re-checked here by `--selftest`:

  coverage    the generator below must contain a planted key's schedule. Counting
              agrees with `zero_offset_census.dodge_filter_full`, which is the
              reviewed counter, so the enumeration is the same set.
  sensitivity the scorer must rank a planted key first. `dodge_score_kernel` shows
              this for the dials; here it is shown for the whole key, against the
              schedules the generator actually emits.

Both are needed and neither implies the other: a sweep can cover a key it cannot
score, and score a key it never generates.

    python dodge_priority_sweep.py --selftest     coverage + recovery
    python dodge_priority_sweep.py --selftest --sample 0    against every schedule
    python dodge_priority_sweep.py --nproc 8      the sweep
"""

from __future__ import annotations

import ctypes
import heapq
import json
import sys
import tempfile
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import log_frequencies  # noqa: E402
from dodge_aware_scorer import PASSES, WINDOW, letter_maps  # noqa: E402
from dodge_score_kernel import _library, log_table, score_dials  # noqa: E402
from quagmire_runner import build_register, build_setup, load_register  # noqa: E402
from quagmire_schedule_census import (  # noqa: E402
    delta_vectors,
    lp_words,
    observed_rates,
    wilson,
)
from zero_offset_census import PROSE_CACHE, diluted_band  # noqa: E402

M = 29
SCORE_WORDS = 400  # what dodge_aware_scorer showed is enough to separate a planted key
BANDS: frozenset[int] = frozenset()  # band_retention.py: every band is cost-neutral
KEEP = 40
KEEP_PER_TASK = 5
TASKS = 240
OUT = ROOT / "experiments" / "dodge_priority_candidates.jsonl"

_W: dict = {}


def fast_log_table(K, offsets, logf) -> np.ndarray:
    """`dodge_score_kernel.log_table`, without the 4,205-iteration Python loop.

    The table is rebuilt for every (alphabet, schedule) pair in the sweep, so the
    loop there would cost about a fifth of the run. Indexing gives the same array;
    `--selftest` asserts they are equal.
    """
    _fwd, inv = letter_maps(K, offsets)
    Karr = np.asarray(K, dtype=np.int64)
    pos_of = np.empty(M, dtype=np.int64)
    pos_of[Karr] = np.arange(M)
    inner = (pos_of[None, :] - np.arange(M)[:, None]) % M  # [t][z]
    runes = Karr[inner]  # [t][z]
    logf = np.asarray(logf, dtype=np.float32)
    tab = np.empty((5, M, M), dtype=np.float32)
    for k in range(5):
        tab[k] = logf[np.asarray(inv[k], dtype=np.int64)[runes]]
    return tab


def surviving_schedules(K, tables, bands, use=BANDS) -> np.ndarray:
    """Every schedule the dodge model admits for this alphabet, as (n, 5) offsets.

    The counting version is `zero_offset_census.dodge_filter_full`; this returns the
    schedules themselves. Exactly one offset is zero (at position z), the offset at
    z-1 is pinned by the observed distance-1 rate, and the other three are free
    non-zero residues completing the sum to zero mod 29.

    `use` selects which rate bands are applied. `band_retention.py` measures that all
    three together keep a true key only 9% of the time while cutting the work by the
    same factor they cut retention, so the default applies none of them.
    """
    T1, T4, T6 = tables
    (lo1, hi1), (lo4, hi4), (lo6, hi6) = bands
    pooled = delta_vectors(K, T1, -1).sum(axis=0)
    inband = np.ones(M, dtype=bool)
    inband[0] = False  # a second zero would give the schedule two, not one
    if 1 in use:
        for d in range(1, M):
            inband[d] = lo1 <= pooled[d] / 5 <= hi1
    if not inband.any():
        return np.empty((0, 5), dtype=np.int8)

    v4 = delta_vectors(K, T4, 1)
    v6 = delta_vectors(K, T6, -1)
    r = np.arange(M, dtype=np.int64)
    a, b, c = r[:, None, None], r[None, :, None], r[None, None, :]
    out = []
    for z in range(5):
        slots = [(z + 1) % 5, (z + 2) % 5, (z + 3) % 5, (z + 4) % 5]
        pinned = (-(a + b + c)) % M
        offs = {z: np.zeros_like(pinned), slots[0]: a, slots[1]: b, slots[2]: c}
        offs[slots[3]] = pinned
        keep = (a != 0) & (b != 0) & (c != 0) & inband[pinned]
        if 4 in use:
            rate4 = sum(v4[k][offs[k]] for k in range(5))
            keep = keep & (rate4 >= lo4) & (rate4 <= hi4)
        if 6 in use:
            rate6 = sum(v6[k][offs[(k + 1) % 5]] for k in range(5))
            keep = keep & (rate6 >= lo6) & (rate6 <= hi6)
        if not keep.any():
            continue
        idx = np.nonzero(np.broadcast_to(keep, pinned.shape))
        block = np.empty((idx[0].size, 5), dtype=np.int8)
        for phase in range(5):
            block[:, phase] = np.broadcast_to(offs[phase], pinned.shape)[idx]
        out.append(block)
    return np.concatenate(out) if out else np.empty((0, 5), dtype=np.int8)


class Corpus:
    """The ciphertext in the layout the kernel wants, converted once.

    `dodge_score_kernel.score_dials` rebuilds these arrays on every call, which is
    free when a call covers 841 dials and is most of the cost when it covers 29 --
    the sweep's shape. Converting once per worker and reusing the buffers is what
    makes the measured rate match the projected one.
    """

    def __init__(
        self, cipher_words, window: int = WINDOW, passes: int = PASSES
    ) -> None:
        self.runes = np.array([c for w in cipher_words for c in w], dtype=np.int8)
        self.lens = np.array([len(w) for w in cipher_words], dtype=np.int32)
        self.dials = np.ascontiguousarray([(t, 0) for t in range(M)], dtype=np.int8)
        self.out = np.empty(M, dtype=np.float32)
        self.window = window
        self.passes = passes
        self.lib = _library()

    def score(self, logtab: np.ndarray) -> np.ndarray:
        """Nats per rune above flat for each of the 29 inner dials."""
        ptr = lambda a: a.ctypes.data_as(ctypes.c_void_p)  # noqa: E731
        self.lib.score_dials(
            ptr(logtab),
            ptr(self.dials),
            ctypes.c_int(M),
            ptr(self.runes),
            ptr(self.lens),
            ctypes.c_int(len(self.lens)),
            ctypes.c_int(self.window),
            ctypes.c_int(self.passes),
            ptr(self.out),
        )
        return self.out


def score_key(K, scheds, corpus: Corpus, logf, *, keep: int):
    """Best (score, schedule, inner dial) over every schedule and its 29 inner dials.

    The outer dial is a uniform ciphertext shift, which the scorer's free bijection
    absorbs exactly (`dodge_score_kernel` asserts this), so it is held at zero and
    the sweep enumerates 29 dials per pair, not 841.
    """
    best: list[tuple[float, list[int], int]] = []
    for sched in scheds:
        offsets = [int(x) for x in sched]
        scores = corpus.score(fast_log_table(K, offsets, logf))
        top = int(scores.argmax())
        item = (float(scores[top]), offsets, top)
        if len(best) < keep:
            heapq.heappush(best, item)
        elif item[0] > best[0][0]:
            heapq.heapreplace(best, item)
    return best


def _prepare(lens):
    """Fill the tables the workers read. The pool forks, so they are shared, not copied."""
    from keyword_exhaustion import alphabets, kw_runes  # noqa: PLC0415
    from quagmire_ungated_sweep import priority_vocabulary  # noqa: PLC0415

    words, _vocab, T1, lo1, hi1, _sigmas = build_setup(PROSE_CACHE, lens, vocab=["the"])
    _T1, T4, T6, _cross = build_register(PROSE_CACHE, lens)
    obs = observed_rates(lp_words())
    raw4, raw6 = wilson(*obs[4]), wilson(*obs[6])
    _W["tables"] = (T1, T4, T6)
    _W["bands"] = ((lo1, hi1), diluted_band(*raw4, 4), diluted_band(*raw6, 6))
    _W["logf"] = log_frequencies()
    _W["corpus"] = Corpus(lp_words()[:SCORE_WORDS])

    keys = []
    for word in priority_vocabulary():
        seq = kw_runes(word)
        if seq:
            keys.extend((name, K) for name, K in alphabets(seq))
    _W["keys"] = keys
    return words, keys


def _work(task):
    """Sweep one slice of keyed alphabets: generate its schedules, score them."""
    name, lo, step = task
    best: list[tuple[float, str, list[int], list[int], int]] = []
    tested = 0
    for kwname, K in _W["keys"][lo::step]:
        scheds = surviving_schedules(K, _W["tables"], _W["bands"])
        if not len(scheds):
            continue
        tested += len(scheds) * M
        for score, offsets, dial in score_key(
            K, scheds, _W["corpus"], _W["logf"], keep=KEEP_PER_TASK
        ):
            item = (score, kwname, list(K), offsets, dial)
            if len(best) < KEEP_PER_TASK:
                heapq.heappush(best, item)
            elif score > best[0][0]:
                heapq.heapreplace(best, item)
    return name, tested, best


def selftest(sample: int = 0) -> None:
    """Coverage then sensitivity, on a planted key of exactly this family."""
    import random  # noqa: PLC0415

    from doublet_phase_test import encipher  # noqa: PLC0415
    from lp_corpus import load_clean  # noqa: PLC0415
    from pure_quagmire_restart import matched_register, schedule  # noqa: PLC0415
    from zero_offset_census import dodge_filter_full  # noqa: PLC0415

    rng = random.Random(3301)
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)][:SCORE_WORDS]

    words, _vocab, T1, lo1, hi1, _s = build_setup(PROSE_CACHE, lens, vocab=["the"])
    _T1, T4, T6, _cross = build_register(PROSE_CACHE, lens)
    obs = observed_rates(lp_words())
    bands = (
        (lo1, hi1),
        diluted_band(*wilson(*obs[4]), 4),
        diluted_band(*wilson(*obs[6]), 6),
    )
    tables = (T1, T4, T6)
    pools, _t, _f = load_register(PROSE_CACHE)
    logf = log_frequencies()

    K = rng.sample(range(M), M)
    offsets = schedule(rng)
    true_dials = (rng.randrange(M), rng.randrange(M))
    plain = matched_register(rng, lens, pools)
    cipher = encipher(plain, K, offsets, true_dials, 0, "advance")
    print(f"planted: schedule {offsets}, dials {true_dials}")

    probe = fast_log_table(K, offsets, logf)
    assert np.array_equal(probe, log_table(K, offsets, logf)), (
        "the vectorised table must equal the reference the kernel test pins"
    )
    print("vectorised log table equals the reference exactly")

    banded = surviving_schedules(K, tables, bands, use={1, 4, 6})
    counted = dodge_filter_full(K, tables, bands)
    print(f"\nwith all three bands: generator {len(banded):,}, counter {counted:,}")
    assert len(banded) == counted, "the enumeration must be the counter's set"

    scheds = surviving_schedules(K, tables, bands)
    print(f"bands in use {sorted(BANDS) or 'none'}: {len(scheds):,} schedules")
    assert all(
        int(np.count_nonzero(s == 0)) == 1 and int(s.sum()) % M == 0 for s in scheds
    ), "every emitted schedule needs exactly one zero and must sum to zero"

    in_banded = any(list(s) == offsets for s in banded)
    hit = [i for i, s in enumerate(scheds) if list(s) == offsets]
    print(
        f"COVERAGE: planted schedule {'IN' if hit else 'NOT IN'} the swept set; "
        f"{'IN' if in_banded else 'NOT IN'} the fully banded set"
    )
    if not hit:
        print("  the sweep cannot find this key; stop here and fix the generator")
        return

    corpus = Corpus(cipher)
    assert np.allclose(
        corpus.score(probe), score_dials(probe, [(t, 0) for t in range(M)], cipher)
    ), "the reused buffers must give the reference's scores"

    if sample and sample < len(scheds):
        pick = np.random.default_rng(3301).choice(len(scheds), sample, replace=False)
        scheds = np.concatenate([scheds[np.sort(pick)], scheds[hit[:1]]])
        print(f"scoring a random {sample:,} of them, plus the planted one")

    start = time.time()
    best = score_key(K, scheds, corpus, logf, keep=len(scheds))
    dt = time.time() - start
    ranked = sorted(best, reverse=True)
    pos = next(i for i, (_s, o, _d) in enumerate(ranked) if o == offsets)
    truth = ranked[pos]
    others = np.array([s for s, _o, _d in ranked if _o != offsets])
    z = (truth[0] - others.mean()) / others.std()
    print(
        f"SENSITIVITY: planted key ranks {pos + 1} of {len(ranked)}, "
        f"score {truth[0]:+.4f} vs wrong mean {others.mean():+.4f} (z = {z:+.1f})"
    )
    rate = len(scheds) * M / dt
    print(
        f"\nmeasured {rate:,.0f} keys/s/core on the sweep's own shape "
        f"({len(scheds):,} schedules x {M} dials in {dt:.1f}s)"
    )
    print(
        f"so the unbanded priority sweep is "
        f"{105_980 * 1264 * M / rate / 3600:,.0f} core-hours"
    )
    print(f"  recovered inner dial {truth[2]}, planted {true_dials[0]}")
    del words


def run(nproc: int) -> None:
    _words, keys = _prepare(_lens())
    print(f"{len(keys):,} keyed alphabets from 3301's vocabulary, {nproc} workers")
    tasks = [(f"dodge-{i}", i, TASKS) for i in range(TASKS)]
    progress = Path(tempfile.gettempdir()) / "dodge_priority_progress.jsonl"
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
                    f"  {done}/{len(todo)} tasks, {tested:,} keys, "
                    f"best {best[0][0]:+.4f}, {rate:,.0f} keys/s, "
                    f"{(time.time() - start) / 60:.1f} min",
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
    print(f"written to {OUT}")


def _lens() -> list[int]:
    from lp_corpus import load_clean  # noqa: PLC0415

    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    return [counts[k] for k in sorted(counts)][:SCORE_WORDS]


def main() -> None:
    if "--selftest" in sys.argv:
        sample = 4000
        for i, a in enumerate(sys.argv):
            if a == "--sample" and i + 1 < len(sys.argv):
                sample = int(sys.argv[i + 1])
        selftest(sample)
        return
    nproc = 6
    for i, a in enumerate(sys.argv):
        if a == "--nproc" and i + 1 < len(sys.argv):
            nproc = int(sys.argv[i + 1])
    run(nproc)


if __name__ == "__main__":
    main()
