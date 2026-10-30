import itertools


def _shape(n):
    rows = max(1, int(n**0.5))
    return rows, max(1, n // rows)


def _grid(rows, cols, rng, walls, top):
    return [[0 if rng.random() < walls else rng.randint(1, top) for _ in range(cols)] for _ in range(rows)]


def _open(grid, cell, rng, top):
    r, c = cell
    if grid[r][c] == 0:
        grid[r][c] = rng.randint(1, top)
    return cell


def _random_cell(rows, cols, rng):
    return (rng.randrange(rows), rng.randrange(cols))


def visual():
    grid = [
        [1, 1, 5, 1],
        [3, 0, 5, 1],
        [1, 1, 9, 1],
        [4, 1, 1, 2],
    ]
    return (grid, (0, 0), (3, 3))


def fixed():
    return [
        ([[5]], (0, 0), (0, 0)),
        ([[1, 0, 1]], (0, 0), (0, 2)),
        ([[2, 3], [4, 1]], (0, 0), (1, 1)),
        ([[1, 9, 1], [1, 1, 1]], (0, 0), (0, 2)),
        ([[1, 1, 1], [0, 0, 1], [7, 1, 1]], (2, 0), (0, 0)),
        ([[3, 1], [1, 3]], (1, 1), (1, 1)),
        ([[1, 1, 0, 1], [1, 1, 0, 1]], (1, 3), (0, 0)),
    ]


def cases(n, rng):
    rows, cols = _shape(n)
    grid = _grid(rows, cols, rng, 0.15, 9)
    start = _open(grid, _random_cell(rows, cols, rng), rng, 9)
    target = _open(grid, _random_cell(rows, cols, rng), rng, 9)
    return [(grid, start, target)]


def bench(n, rng):
    side = max(1, int(n**0.5))
    grid = _grid(side, side, rng, 0.1, 9)
    start = _open(grid, (0, 0), rng, 9)
    target = _open(grid, (side - 1, side - 1), rng, 9)
    return [(grid, start, target)]


def check(case, got, expected):
    grid, start, target = case
    path = [tuple(cell) for cell in got]
    if not expected:
        return path == []
    if path[0] != tuple(start) or path[-1] != tuple(target):
        return False
    for (r1, c1), (r2, c2) in itertools.pairwise(path):
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return False
    for r, c in path:
        if not (0 <= r < len(grid) and 0 <= c < len(grid[0])) or grid[r][c] == 0:
            return False
    return sum(grid[r][c] for r, c in path) == sum(grid[r][c] for r, c in expected)
