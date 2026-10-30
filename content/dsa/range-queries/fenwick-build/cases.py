def _ops(n, count, rng, updates):
    ops = [("__init__", n)]
    for _ in range(count):
        r = rng.random()
        if r < updates:
            ops.append(("update", rng.randrange(n), rng.randint(-50, 50)))
        elif r < (1 + updates) / 2:
            ops.append(("prefix", rng.randint(0, n)))
        else:
            l = rng.randrange(n)
            ops.append(("range_sum", l, rng.randint(l, n - 1)))
    return ops


def visual():
    return [
        ("__init__", 8),
        ("update", 2, 5),
        ("update", 5, 3),
        ("update", 0, 4),
        ("prefix", 6),
        ("update", 7, -2),
        ("range_sum", 1, 7),
    ]


def fixed():
    return [
        [("__init__", 0), ("prefix", 0)],
        [("__init__", 1), ("prefix", 1), ("update", 0, 7), ("prefix", 0), ("prefix", 1), ("range_sum", 0, 0)],
        [("__init__", 4), ("update", 3, 2), ("update", 3, 2), ("prefix", 3), ("prefix", 4), ("range_sum", 3, 3)],
        [
            ("__init__", 5),
            ("update", 0, 1),
            ("update", 4, 10),
            ("range_sum", 0, 4),
            ("range_sum", 1, 3),
            ("update", 2, -3),
            ("range_sum", 2, 2),
        ],
    ]


def cases(n, rng):
    if n == 0:
        return [[("__init__", 0), ("prefix", 0)]]
    return [_ops(n, 2 * n, rng, 0.4)]


def bench(n, rng):
    return [_ops(n, n, rng, 0.5)]
