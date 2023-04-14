def print_modchecker(runes: list[int], *, trace: bool = False) -> None:
    """For a list of integers, find the highest number where remainder of the modulus is constant."""
    if len(runes) < 2:
        return
    runes = sorted(runes)
    lowest = runes[0]
    runes[-1]

    for i in range(lowest, 0, -1):
        rests = []
        for j in runes:
            rests.append(j % i)
        if trace is True:
            print(f"mod {i}: {rests}")

        result = all(element == rests[0] for element in rests)
        if result:
            print(f"FOUND mod {i}: {rests}")
            break
