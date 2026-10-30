def visual():
    return [("push", v) for v in [9, 5, 7, 2, 8, 1, 4]]


def cases(n, rng):
    return [[("push", rng.randint(0, 99)) for _ in range(n)]]
