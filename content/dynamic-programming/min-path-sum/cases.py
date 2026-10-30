def visual():
    grid = [
        [3, 1, 4, 2],
        [1, 5, 1, 3],
        [4, 2, 6, 1],
        [2, 7, 1, 2],
    ]
    return (grid,)


def fixed():
    return [
        ([[7]],),
        ([[1, 2, 3]],),
        ([[1], [2], [3]],),
        ([[1, 9], [1, 1]],),
        ([[0, 0], [0, 0]],),
    ]


def cases(n, rng):
    rows = max(n, 1)
    cols = rng.randint(1, rows)
    if rng.random() < 0.5:
        rows, cols = cols, rows
    return [([[rng.randint(0, 9) for _ in range(cols)] for _ in range(rows)],)]


def bench(n, rng):
    return [([[rng.randint(0, 9) for _ in range(n)] for _ in range(n)],)]
