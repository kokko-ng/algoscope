def visual():
    return [
        ("append", 4),
        ("append", 7),
        ("append", 1),
        ("get", 1),
        ("append", 9),
        ("set", 0, 3),
        ("pop",),
        ("__len__",),
    ]


def cases(n, rng):
    ops = []
    size = 0
    for _ in range(n):
        r = rng.random()
        if size > 0 and r < 0.15:
            ops.append(("pop",))
            size -= 1
        elif size > 0 and r < 0.3:
            ops.append(("get", rng.randrange(size)))
        elif size > 0 and r < 0.4:
            ops.append(("set", rng.randrange(size), rng.randint(0, 999)))
        else:
            ops.append(("append", rng.randint(0, 999)))
            size += 1
    ops.append(("__len__",))
    return [ops]


def bench(n, rng):
    return [[("append", i) for i in range(n)] + [("get", n // 2), ("__len__",)]]
