def _shape(n):
    rows = max(1, int(n**0.5))
    return rows, max(1, n // rows)


def _grid(rows, cols, rng, walls):
    return [[0 if rng.random() < walls else 1 for _ in range(cols)] for _ in range(rows)]


def visual():
    grid = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1],
        [0, 0, 1, 1, 1],
    ]
    return (grid, (2, 0), (3, 2))


def fixed():
    return [
        ([[1]], (0, 0), (0, 0)),
        ([[1, 0, 1]], (0, 0), (0, 2)),
        ([[1, 1], [1, 1]], (0, 0), (1, 1)),
        ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], (0, 0), (0, 2)),
        ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], (1, 1), (2, 0)),
        ([[1, 1, 1], [0, 0, 1], [1, 1, 1]], (2, 0), (0, 0)),
    ]


def cases(n, rng):
    rows, cols = _shape(n)
    grid = _grid(rows, cols, rng, rng.choice([0.0, 0.2, 0.35]))
    start = (rng.randrange(rows), rng.randrange(cols))
    target = (rng.randrange(rows), rng.randrange(cols))
    grid[start[0]][start[1]] = 1
    grid[target[0]][target[1]] = 1
    return [(grid, start, target)]


def bench(n, rng):
    side = max(1, int(n**0.5))
    grid = _grid(side, side, rng, 0.2)
    grid[0][0] = grid[-1][-1] = 1
    return [(grid, (0, 0), (side - 1, side - 1))]
