def _ops(n, count, rng):
    width = max(n, 1)
    ops = []
    for _ in range(count):
        r = rng.random()
        if r < 0.35:
            ops.append(("add", rng.randrange(width)))
        elif r < 0.5:
            ops.append(("remove", rng.randrange(width)))
        elif r < 0.7:
            ops.append(("contains", rng.randrange(width)))
        elif r < 0.75:
            ops.append(("union", rng.getrandbits(width)))
        elif r < 0.8:
            ops.append(("intersect", rng.getrandbits(width)))
        elif r < 0.9:
            ops.append(("count",))
        else:
            ops.append(("mask",))
    return ops


def visual():
    return [
        ("add", 1),
        ("add", 4),
        ("add", 6),
        ("contains", 4),
        ("remove", 4),
        ("remove", 5),
        ("union", 0b10100001),
        ("intersect", 0b11000011),
        ("contains", 7),
        ("count",),
        ("mask",),
    ]


def fixed():
    return [
        [("count",), ("mask",), ("contains", 0)],
        [("remove", 3), ("mask",), ("count",)],
        [("add", 0), ("add", 0), ("count",), ("remove", 0), ("remove", 0), ("count",), ("mask",)],
        [("add", 70), ("contains", 70), ("contains", 69), ("count",), ("mask",)],
        [("union", 0b1011), ("intersect", 0b0110), ("mask",), ("count",), ("contains", 1), ("contains", 3)],
    ]


def cases(n, rng):
    return [[*_ops(n, 2 * n + 1, rng), ("count",), ("mask",)]]


def bench(n, rng):
    positions = list(range(n))
    rng.shuffle(positions)
    ops = [("add", i) for i in positions[: n // 2]]
    ops += [("contains", rng.randrange(n)) for _ in range(n // 4)]
    ops += [("remove", i) for i in positions[: n // 4]]
    ops += [("union", rng.getrandbits(n)), ("intersect", rng.getrandbits(n) | rng.getrandbits(n))]
    return [[*ops, ("count",), ("mask",)]]
