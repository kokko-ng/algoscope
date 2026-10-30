def visual():
    return ([[1, 4], [3, 5], [0, 6], [5, 7], [3, 9], [5, 9], [6, 10], [8, 11]],)


def fixed():
    return [
        ([],),
        ([[1, 2]],),
        ([[1, 2], [2, 3]],),
        ([[1, 10], [2, 3], [4, 5]],),
        ([[1, 3], [1, 3], [1, 3]],),
        ([[5, 6], [1, 2], [3, 4]],),
        ([[0, 5], [1, 2], [2, 3], [3, 4], [4, 8]],),
    ]


def cases(n, rng):
    out = []
    for _ in range(n):
        start = rng.randint(0, 3 * n)
        out.append([start, start + rng.randint(1, 8)])
    return [(out,)]
