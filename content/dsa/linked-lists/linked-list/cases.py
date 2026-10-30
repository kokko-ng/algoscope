def visual():
    return [
        ("push_back", 4),
        ("push_back", 7),
        ("push_front", 2),
        ("push_back", 9),
        ("find", 7),
        ("remove", 9),
        ("push_back", 5),
        ("pop_front",),
        ("__len__",),
    ]


def fixed():
    return [
        [("pop_front",), ("find", 1), ("remove", 1), ("__len__",)],
        [("push_back", 1), ("remove", 1), ("push_back", 2), ("pop_front",), ("pop_front",), ("__len__",)],
        [("push_front", 1), ("pop_front",), ("push_back", 3), ("push_front", 2), ("find", 3), ("__len__",)],
        [
            ("push_back", 1),
            ("push_back", 2),
            ("remove", 2),
            ("push_back", 3),
            ("find", 3),
            ("pop_front",),
            ("pop_front",),
        ],
        [("push_back", 5), ("push_back", 5), ("remove", 5), ("find", 5), ("__len__",)],
    ]


def cases(n, rng):
    ops = []
    for _ in range(n):
        r = rng.random()
        v = rng.randint(0, 9)
        if r < 0.3:
            ops.append(("push_back", v))
        elif r < 0.55:
            ops.append(("push_front", v))
        elif r < 0.7:
            ops.append(("pop_front",))
        elif r < 0.82:
            ops.append(("find", v))
        elif r < 0.94:
            ops.append(("remove", v))
        else:
            ops.append(("__len__",))
    # a final push_back exposes a stale tail after removals
    ops += [("push_back", 99), ("find", 99), ("__len__",)]
    return [ops]


def bench(n, rng):
    ops = []
    for i in range(n):
        ops.append(("push_back", i))
        ops.append(("push_front", -i))
    ops += [("pop_front",)] * (n // 2)
    ops += [("find", n - 1), ("remove", n // 2), ("push_back", n), ("__len__",)]
    return [ops]
