def visual():
    return [
        ("put", 5, "a"),
        ("put", 9, "b"),
        ("put", 2, "c"),
        ("put", 13, "d"),
        ("put", 6, "e"),
        ("get", 13),
        ("put", 9, "f"),
        ("remove", 2),
        ("get", 2),
        ("__len__",),
    ]


def fixed():
    return [
        [("get", 1), ("remove", 1), ("__len__",)],
        [("put", "x", 1), ("put", "x", 2), ("get", "x"), ("__len__",)],
        [("put", 0, 0), ("remove", 0), ("remove", 0), ("get", 0), ("__len__",)],
        [("put", i, i * i) for i in range(20)] + [("get", i) for i in range(20)] + [("__len__",)],
    ]


def cases(n, rng):
    ops = []
    for _ in range(n):
        key = rng.randint(0, n // 2 + 2) if rng.random() < 0.8 else f"k{rng.randint(0, 9)}"
        r = rng.random()
        if r < 0.5:
            ops.append(("put", key, rng.randint(0, 999)))
        elif r < 0.8:
            ops.append(("get", key))
        else:
            ops.append(("remove", key))
    ops.append(("__len__",))
    return [ops]


def bench(n, rng):
    keys = rng.sample(range(100 * n), n)
    ops = [("put", k, i) for i, k in enumerate(keys)]
    ops += [("get", k) for k in keys]
    ops += [("remove", k) for k in keys[: n // 2]]
    ops.append(("__len__",))
    return [ops]
