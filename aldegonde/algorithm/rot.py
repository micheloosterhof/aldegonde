from typing import List


def rot(inp: List[int], shift: int) -> List[int]:
    """
    shift contents of list by `shift` mod MAX
    e.g. rot13
    """
    output = []
    for i in inp:
        output.append((i + shift + MAX) % MAX)
    return output
