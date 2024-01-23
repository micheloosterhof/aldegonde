from aldegonde.maths import factor
from aldegonde.pasc import T
from aldegonde.stats import ioc


def create_table(
    sequence: list[T],
    height: int,
    width: int,
) -> tuple[list[list[T]], list[list[T]]]:
    assert len(sequence) == height * width

    rows = [sequence[i * width : (i + 1) * width] for i in range(height)]

    columns = []
    for i in range(width):
        col = []
        for j in range(height):
            col.append(sequence[j * width + i])
        columns.append(col)

    return rows, columns


def print_tables(sequence: list[T]) -> None:
    allsizes = factor.factor_pairs(len(sequence))[1:-1]
    for size in allsizes:
        rows, columns = create_table(sequence, size[0], size[1])
        print(f"height: {size[0]} width: {size[1]}")
        for i, row in enumerate(rows):
            print(f"row {i}/{size[0]}: ioc: {29*ioc.ioc(row)}")
        for i, column in enumerate(columns):
            print(f"col {i}/{size[1]}: ioc: {29*ioc.ioc(column)}")
