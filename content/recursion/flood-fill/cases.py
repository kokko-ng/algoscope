def visual():
    grid = [
        [1, 1, 0, 0, 2],
        [1, 0, 0, 1, 2],
        [0, 0, 1, 1, 2],
        [2, 0, 0, 0, 1],
    ]
    return (grid, 1, 2, 7)


def fixed():
    return [
        ([[5]], 0, 0, 5),
        ([[5]], 0, 0, 1),
        ([[1, 1], [1, 1]], 1, 1, 1),
        ([[1, 2], [2, 1]], 0, 0, 3),
        ([[0, 0, 0]], 0, 1, 4),
    ]


def cases(n, rng):
    rows, cols = max(n, 1), max(n // 2, 1)
    grid = [[rng.randint(0, 1) for _ in range(cols)] for _ in range(rows)]
    return [(grid, rng.randrange(rows), rng.randrange(cols), rng.randint(0, 2))]


def bench(n, rng):
    # a winding corridor of 0s between walls of 1s: half the cells, all connected in one long path
    grid = []
    for r in range(n):
        if r % 2 == 0:
            grid.append([0] * n)
        else:
            row = [1] * n
            row[n - 1 if r % 4 == 1 else 0] = 0
            grid.append(row)
    return [(grid, 0, 0, 2)]
