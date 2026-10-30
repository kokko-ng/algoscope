def visual():
    return ([3, 2, 2, 4, 1, 4], 3)


def fixed():
    return [([7], 1), ([7], 3), ([1, 1, 1], 1), ([1, 1, 1], 3), ([5, 1, 1, 5], 2), ([10, 1, 1, 1], 4)]


def cases(n, rng):
    weights = [rng.randint(1, 50) for _ in range(n)]
    return [(weights, rng.randint(1, n))]


def bench(n, rng):
    # few days: the answer sits far above the heaviest package, so counting up from it is slow
    weights = [rng.randint(1, 100) for _ in range(n)]
    return [(weights, rng.randint(3, 6))]
