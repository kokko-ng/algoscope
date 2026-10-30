def _shape(n):
    rows = max(1, int(n**0.5))
    return rows, max(1, n // rows)


def visual():
    grid = [
        [1, 3, 1, 2],
        [1, 1, 1, 1],
        [2, 0, 1, 1],
        [1, 1, 2, 1],
    ]
    return (grid,)


def fixed():
    return [
        ([[4]],),
        ([[0]],),
        ([[1, 1], [1, 1]],),
        ([[1, 0], [0, 1]],),
        ([[1, 1, 1], [1, 1, 1], [1, 1, 0]],),
        ([[2, 1, 1], [1, 1, 1], [1, 1, 1]],),
        ([[1, 5, 1], [1, 1, 1]],),
    ]


def cases(n, rng):
    if n == 0:
        return []
    rows, cols = _shape(n)
    top = rng.choice([1, 2, 3, 9])
    walls = rng.choice([0.0, 0.1, 0.25])
    grid = [[0 if rng.random() < walls else rng.randint(1, top) for _ in range(cols)] for _ in range(rows)]
    if rng.random() < 0.8:
        grid[0][0] = grid[0][0] or 1
        grid[-1][-1] = grid[-1][-1] or 1
    return [(grid,)]


def bench(n, rng):
    side = max(1, int(n**0.5))
    grid = [[rng.randint(1, 2) for _ in range(side)] for _ in range(side)]
    return [(grid,)]
