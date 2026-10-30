def visual():
    return [
        ("__init__", 8),
        ("union", 0, 1),
        ("union", 2, 3),
        ("union", 1, 3),
        ("union", 4, 5),
        ("connected", 0, 2),
        ("union", 5, 3),
        ("connected", 6, 4),
        ("union", 0, 4),
        ("count",),
    ]


def fixed():
    return [
        [("__init__", 0), ("count",)],
        [("__init__", 1), ("union", 0, 0), ("connected", 0, 0), ("count",)],
        [("__init__", 3), ("union", 0, 1), ("union", 1, 0), ("connected", 0, 2), ("count",)],
    ]


def cases(n, rng):
    ops = [("__init__", n)]
    if n == 0:
        return [ops + [("count",)]]
    for _ in range(2 * n):
        r = rng.random()
        a, b = rng.randrange(n), rng.randrange(n)
        if r < 0.5:
            ops.append(("union", a, b))
        elif r < 0.9:
            ops.append(("connected", a, b))
        else:
            ops.append(("count",))
    ops.append(("count",))
    return [ops]


def bench(n, rng):
    # long chains in both directions, then queries from the far end
    forward = [("__init__", n)] + [("union", i, i + 1) for i in range(n - 1)]
    forward += [("connected", 0, rng.randrange(n)) for _ in range(n)]
    backward = [("__init__", n)] + [("union", i + 1, i) for i in range(n - 1)]
    backward += [("connected", n - 1, rng.randrange(n)) for _ in range(n)]
    return [forward, backward]
