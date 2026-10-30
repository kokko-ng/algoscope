def _sorted_disjoint(n, rng):
    out = []
    pos = rng.randint(0, 3)
    for _ in range(n):
        start = pos + rng.randint(1, 4)
        end = start + rng.randint(0, 4)
        out.append([start, end])
        pos = end
    return out


def visual():
    return ([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8])


def fixed():
    return [
        ([], [2, 5]),
        ([[1, 3]], [5, 7]),
        ([[5, 7]], [1, 3]),
        ([[1, 3]], [3, 4]),
        ([[1, 5]], [2, 3]),
        ([[1, 2], [4, 5]], [0, 9]),
        ([[1, 2], [6, 7]], [3, 4]),
    ]


def cases(n, rng):
    intervals = _sorted_disjoint(n, rng)
    hi = intervals[-1][1] + 5 if intervals else 10
    start = rng.randint(0, hi)
    return [(intervals, [start, start + rng.randint(0, max(1, hi // 4))])]


def bench(n, rng):
    intervals = _sorted_disjoint(n, rng)
    hi = intervals[-1][1]
    start = rng.randint(hi // 3, hi // 2)
    return [(intervals, [start, start + hi // 4])]
