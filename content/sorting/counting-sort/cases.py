def visual():
    return ([3, 1, 4, 1, 5, 2, 0, 4], 5)


def fixed():
    return [([], 0), ([], 3), ([0], 0), ([2, 2, 2], 2), ([0, 3], 9)]


def cases(n, rng):
    k = rng.randint(0, max(1, n))
    return [([rng.randint(0, k) for _ in range(n)], k)]


def bench(n, rng):
    return [([rng.randint(0, n) for _ in range(n)], n)]
