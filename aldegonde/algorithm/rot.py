from ..structures import sequence


def rot(inp: sequence.Sequence, shift: int) -> sequence.Sequence:
    """
    shift contents of list by `shift` mod MAX
    e.g. rot13
    """
    MAX = len(inp.alphabet)
    output = sequence.Sequence(alphabet=inp.alphabet)
    for i in inp:
        output.append((i + shift + MAX) % MAX)
    return output
