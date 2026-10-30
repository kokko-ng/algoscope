def visual():
    ops = [("push", v) for v in [6, 3, 8, 1, 5, 9, 2]]
    return [*ops, ("peek",), ("pop",), ("pop",), ("push", 4), ("pop",), ("__len__",)]


def fixed():
    return [
        [("__len__",)],
        [("push", 5), ("peek",), ("pop",), ("__len__",)],
        [("push", 2), ("push", 2), ("push", 1), ("pop",), ("pop",), ("pop",)],
        [("push", v) for v in [5, 4, 3, 2, 1]] + [("pop",)] * 5,
        [("push", v) for v in [1, 2, 3, 4, 5]] + [("pop",)] * 5,
        [("push", -3), ("push", 7), ("pop",), ("push", -9), ("peek",), ("__len__",)],
    ]


def cases(n, rng):
    ops = []
    size = 0
    for _ in range(n):
        r = rng.random()
        if size > 0 and r < 0.3:
            ops.append(("pop",))
            size -= 1
        elif size > 0 and r < 0.4:
            ops.append(("peek",))
        elif r < 0.45:
            ops.append(("__len__",))
        else:
            ops.append(("push", rng.randint(-50, 50)))
            size += 1
    ops += [("pop",)] * size
    return [ops]


def bench(n, rng):
    ops = [("push", n - i) for i in range(n)]
    ops += [("pop",)] * n
    return [ops]
