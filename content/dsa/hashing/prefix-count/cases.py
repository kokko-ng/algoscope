def visual():
    return ([3, 4, -7, 1, 3, 3, 1, -4], 7)


def fixed():
    return [([], 0), ([0], 0), ([5], 5), ([5], 4), ([0, 0, 0], 0), ([1, -1, 1, -1], 0), ([2, 2, 2], 4)]


def cases(n, rng):
    nums = [rng.randint(-5, 5) for _ in range(n)]
    return [(nums, rng.randint(-6, 6))]
