def visual():
    return ([1, 1, 0, 1, 0, 0, 1, 1, 1, 0], 2)


def fixed():
    return [([], 1), ([0], 0), ([1], 0), ([0, 0, 0], 0), ([0, 0, 0], 2), ([1, 1, 1], 0), ([0, 1, 0], 5)]


def cases(n, rng):
    p = rng.random()
    return [([1 if rng.random() < p else 0 for _ in range(n)], rng.randint(0, max(0, n // 4)))]
