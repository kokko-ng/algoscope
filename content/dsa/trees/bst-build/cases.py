def visual():
    ops = [("insert", v) for v in [50, 30, 70, 20, 40, 60, 80, 35]]
    return [*ops, ("contains", 35), ("contains", 65), ("delete", 20), ("delete", 40), ("delete", 50), ("inorder",)]


def fixed():
    def build(values):
        return [("insert", v) for v in values]

    return [
        [("contains", 1), ("delete", 1), ("inorder",)],
        [*build([5]), ("delete", 5), ("contains", 5), ("inorder",)],
        [*build([5, 3, 8]), ("delete", 3), ("inorder",), ("contains", 3)],
        [*build([5, 3, 8, 7]), ("delete", 8), ("inorder",), ("contains", 7)],
        [*build([5, 3, 8, 1]), ("delete", 3), ("inorder",)],
        [*build([5, 3, 8, 6, 9]), ("delete", 5), ("inorder",), ("contains", 5), ("contains", 6)],
        [*build([10, 5, 20, 15, 30, 17, 16]), ("delete", 10), ("inorder",), ("delete", 15), ("inorder",)],
        [*build([4, 2, 6, 4, 2]), ("inorder",), ("delete", 9), ("inorder",)],
        [*build([1, 2, 3, 4, 5]), ("delete", 1), ("delete", 3), ("inorder",), ("contains", 4)],
    ]


def cases(n, rng):
    span = 4 * n + 10
    ops = []
    present = []
    for value in rng.sample(range(span), n):
        ops.append(("insert", value))
        present.append(value)
        r = rng.random()
        if r < 0.25:
            ops.append(("contains", rng.choice(present) if rng.random() < 0.5 else rng.randrange(span)))
        elif r < 0.45:
            victim = present.pop(rng.randrange(len(present)))
            ops.append(("delete", victim))
        elif r < 0.5:
            ops.append(("insert", rng.choice(present)))
        elif r < 0.55:
            ops.append(("delete", rng.randrange(span)))
        if rng.random() < 2 / (n + 1):
            ops.append(("inorder",))
    ops.append(("inorder",))
    return [ops]


def bench(n, rng):
    values = rng.sample(range(4 * n), n)
    ops = [("insert", v) for v in values]
    ops += [("contains", rng.randrange(4 * n)) for _ in range(n // 2)]
    ops += [("delete", v) for v in rng.sample(values, n // 4)]
    ops.append(("inorder",))
    return [ops]
