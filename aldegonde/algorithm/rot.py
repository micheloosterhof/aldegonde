def rot(inp: list[int], shift: int) -> list[int]:
    """
    shift contents of list by `shift` mod MAX
    e.g. rot13
    """
    output = []
    for i in inp:
        output.append((i + shift + MAX) % MAX)
    return output
