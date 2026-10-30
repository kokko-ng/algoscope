def visual():
    grid = [
        [1, 1, 0, 0, 1],
        [1, 0, 0, 1, 1],
        [0, 0, 1, 0, 0],
        [1, 0, 1, 1, 0],
        [1, 1, 0, 0, 0],
    ]
    return (grid,)


def fixed():
    return [
        ([],),
        ([[0]],),
        ([[1]],),
        ([[1, 0, 1, 0, 1]],),
        ([[1], [1], [0], [1]],),
        ([[1, 1, 1], [1, 0, 1], [1, 1, 1]],),
    ]


def cases(n, rng):
    if n == 0:
        return [([],)]
    cols = rng.randint(1, n)
    density = rng.choice([0.3, 0.5, 0.7])
    grid = [[1 if rng.random() < density else 0 for _ in range(cols)] for _ in range(n)]
    return [(grid,)]


def bench(n, rng):
    grid = [[1 if rng.random() < 0.55 else 0 for _ in range(n)] for _ in range(n)]
    return [(grid,)]
