def _ops(values, count, rng):
    n = len(values)
    ops = [("__init__", values)]
    for _ in range(count):
        if rng.random() < 0.5:
            ops.append(("update", rng.randrange(n), rng.randint(-1000, 1000)))
        else:
            l = rng.randrange(n)
            ops.append(("query", l, rng.randint(l, n - 1)))
    return ops


def visual():
    return [
        ("__init__", [5, 2, 7, 1, 9, 3, 8, 6]),
        ("query", 1, 5),
        ("update", 3, 10),
        ("query", 2, 6),
        ("query", 0, 0),
    ]


def fixed():
    return [
        [("__init__", [4]), ("query", 0, 0), ("update", 0, -1), ("query", 0, 0)],
        [("__init__", [3, 1]), ("query", 0, 1), ("query", 0, 0), ("update", 1, 5), ("query", 0, 1), ("query", 1, 1)],
        [
            ("__init__", [5, 4, 3, 2, 1]),
            ("query", 0, 3),
            ("query", 4, 4),
            ("update", 4, 9),
            ("query", 0, 4),
            ("query", 3, 4),
        ],
        [("__init__", [2, 2, 2]), ("update", 1, 2), ("query", 0, 2)],
    ]


def cases(n, rng):
    values = [rng.randint(-1000, 1000) for _ in range(max(n, 1))]
    return [_ops(values, 2 * n + 1, rng)]


def bench(n, rng):
    values = [rng.randint(-1000, 1000) for _ in range(n)]
    return [_ops(values, n, rng)]
