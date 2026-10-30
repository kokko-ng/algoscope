def visual():
    return [
        ("__init__", 8),
        ("update", 2, 5),
        ("update", 4, 3),
        ("update", 0, 4),
        ("prefix", 7),
        ("update", 6, 2),
        ("prefix", 8),
    ]


def cases(n, rng):
    ops = [("__init__", max(n, 1))]
    for _ in range(n):
        ops.append(("update", rng.randrange(max(n, 1)), rng.randint(-9, 9)))
        ops.append(("prefix", rng.randint(0, max(n, 1))))
    return [ops]
