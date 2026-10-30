def visual():
    return [("append", v) for v in [5, 8, 2, 9, 4, 7]]


def cases(n, rng):
    return [[("append", rng.randint(0, 99)) for _ in range(n)]]
