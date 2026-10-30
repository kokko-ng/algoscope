def _inserts(values):
    return [("insert", v) for v in values]


def visual():
    return [*_inserts([10, 20, 30, 25, 27]), ("height",), ("contains", 25), ("contains", 26), ("inorder",)]


def fixed():
    return [
        [("height",), ("contains", 1), ("inorder",)],
        [*_inserts([5]), ("height",), ("contains", 5), ("inorder",)],
        [*_inserts([1, 2, 3]), ("height",), ("inorder",)],
        [*_inserts([3, 2, 1]), ("height",), ("inorder",)],
        [*_inserts([3, 1, 2]), ("height",), ("inorder",)],
        [*_inserts([1, 3, 2]), ("height",), ("inorder",)],
        [*_inserts([5, 5, 5, 3, 3]), ("height",), ("inorder",)],
        [*_inserts(range(1, 16)), ("height",), ("contains", 8), ("contains", 16)],
        [*_inserts(range(31, 0, -1)), ("height",), ("inorder",)],
        [*_inserts([50, 20, 80, 10, 30, 25, 27, 26]), ("height",), ("inorder",)],
    ]


def cases(n, rng):
    span = 3 * n + 5
    values = rng.sample(range(span), n)
    style = rng.randrange(4)
    if style == 1:
        values.sort()
    elif style == 2:
        values.sort(reverse=True)
    elif style == 3:
        values.sort()
        values = [values[i // 2] if i % 2 == 0 else values[-1 - i // 2] for i in range(n)]
    ops = []
    for value in values:
        ops.append(("insert", value))
        r = rng.random()
        if r < 0.2:
            ops.append(("contains", rng.randrange(span)))
        elif r < 0.3:
            ops.append(("height",))
        elif r < 0.35:
            ops.append(("insert", value))
    ops += [("height",), ("inorder",)]
    return [ops]


def bench(n, rng):
    values = list(range(n))
    if rng.random() < 0.5:
        values.reverse()
    ops = _inserts(values)
    ops += [("contains", rng.randrange(2 * n)) for _ in range(n // 2)]
    ops += [("height",), ("inorder",)]
    return [ops]
