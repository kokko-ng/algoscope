def visual():
    return ([[0, 30], [5, 10], [15, 20], [10, 25], [25, 35], [31, 40]],)


def fixed():
    return [
        ([],),
        ([[1, 5]],),
        ([[1, 5], [5, 9]],),
        ([[1, 5], [2, 6], [3, 7]],),
        ([[7, 10], [2, 4]],),
        ([[1, 10], [2, 3], [3, 4], [4, 5]],),
    ]


def cases(n, rng):
    out = []
    for _ in range(n):
        start = rng.randint(0, 3 * n)
        out.append([start, start + rng.randint(1, 10)])
    return [(out,)]
