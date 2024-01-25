"""Friedman test to detect use of the same alphabet at regular intervals."""

from collections.abc import Sequence
from statistics import mean, median
from typing import TypeVar

from aldegonde.analysis.split import split_by_slice_interrupted
from aldegonde.stats.ioc import ioc
from aldegonde.stats.kappa import kappa

T = TypeVar("T")


def friedman_test(
    ciphertext: Sequence[T],
    minperiod: int = 1,
    maxperiod: int = 20,
    *,
    trace: bool = False,
) -> None:
    """Print the friedman test
    https://crypto.stackexchange.com/questions/40066/finding-length-of-a-key-for-a-given-vigenere-cipher-using-index-of-coincidence.
    """
    # avgioc contains the key length as key. as value it's the avgioc
    # delta is the difference between the avgioc and the max of avgioc of all lower values
    avgioc: dict[int, float] = {}
    medioc: dict[int, float] = {}
    avgdelta: dict[int, float] = {}
    meddelta: dict[int, float] = {}

    if trace is True:
        print("Testing for periodicity using friedman test")

    if maxperiod > len(ciphertext):
        maxperiod = len(ciphertext) - 1

    for period in range(minperiod, maxperiod + 1):
        kscore = kappa(ciphertext, period)
        iocs: list[float] = []
        for k in range(period):
            v = ciphertext[slice(k, len(ciphertext), period)]
            ic: float = ioc(v)  # note, perviously was normalized
            iocs.append(ic)
            if trace is True:
                print(f"ioc of slice {k}/{period} = {ic:.3f}")
        medioc[period] = median(iocs)
        avgioc[period] = mean(iocs)
        avgdelta[period] = avgioc[period] - max(avgioc.values())
        meddelta[period] = medioc[period] - max(medioc.values())
        print(
            f"friedman: period {period:02d} ",
            end="",
        )
        print(
            f"kappa={kscore:0.4f}  ",
            end="",
        )
        print(
            f"avgioc: {avgioc[period]:.3f} delta: {avgdelta[period]:+.4f}",
            end="",
        )
        if abs(avgdelta[period]) < 0.001:
            print("* ", end="")
        else:
            print("  ", end="")

        print(
            f"  medioc: {medioc[period]:.3f} delta: {meddelta[period]:+.4f}",
            end="",
        )
        if abs(meddelta[period]) < 0.001:
            print("* ")
        else:
            print("  ")


def friedman_test_with_interrupter(
    ciphertext: Sequence[T],
    alphabet: Sequence[T],
    minperiod: int = 1,
    maxperiod: int = 20,
    *,
    trace: bool = False,
) -> None:
    """Print the friedman test
    https://crypto.stackexchange.com/questions/40066/finding-length-of-a-key-for-a-given-vigenere-cipher-using-index-of-coincidence.

    this version assumes it is a periodic polyalphabetic cipher with a single ciphertext interrupter
    restart the sequence to first symbol of the alpahbet at the occurence of a particular symbol
    """
    # avgioc contains the key length as key. as value it's the avgioc
    # delta is the difference between the avgioc and the max of avgioc of all lower values

    for i, interrupter in enumerate(alphabet):
        avgioc: dict[int, float] = {}
        medioc: dict[int, float] = {}
        avgdelta: dict[int, float] = {}
        meddelta: dict[int, float] = {}

        if trace is True:
            print(
                "Testing for periodicity with ciphertext interrupters using friedman test:",
            )

        for period in range(minperiod, maxperiod + 1):
            kscore = kappa(ciphertext, period) * len(alphabet)
            iocs: list[float] = []
            kv = split_by_slice_interrupted(
                ciphertext,
                step=period,
                interrupter=interrupter,
            )
            # print(kv)
            for k, v in kv.items():
                ic: float = ioc(v) * len(alphabet)
                iocs.append(ic)
                if trace is True:
                    print(f"ioc of slice {k}/{period} = {ic:.3f}")
            medioc[period] = median(iocs)
            avgioc[period] = mean(iocs)
            avgdelta[period] = avgioc[period] - max(avgioc.values())
            meddelta[period] = medioc[period] - max(medioc.values())
            print(
                f"friedman interrupter {interrupter}({i:02d}): period {period:02d} ",
                end="",
            )
            print(
                f"kappa={kscore:0.4f}  ",
                end="",
            )
            print(
                f"avgioc: {avgioc[period]:.3f} delta: {avgdelta[period]:+.4f}",
                end="",
            )
            if abs(avgdelta[period]) < 0.001:
                print("* ", end="")
            else:
                print("  ", end="")

            print(
                f"  medioc: {medioc[period]:.3f} delta: {meddelta[period]:+.4f}",
                end="",
            )
            if abs(meddelta[period]) < 0.001:
                print("* ")
            else:
                print("  ")
