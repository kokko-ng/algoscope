def visual():
    return ([4, 2, 7, 1, 3, 6, 5, 2], 3)


def fixed():
    return [([], 2), ([5], 1), ([1, 2], 3)]


def cases(n, rng):
    k = rng.randint(1, max(1, n))
    return [([rng.randint(0, 50) for _ in range(n)], k)]
