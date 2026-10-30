def visual():
    return ([1, 3, 3, 5, 5, 5, 8, 9], 5)


def fixed():
    return [([], 4), ([2], 1), ([2], 2), ([2], 3), ([1, 1, 1], 1), ([1, 1, 1], 2), ([1, 2, 3], 0), ([1, 2, 3], 4)]


def cases(n, rng):
    nums = sorted(rng.randint(0, 3 * n + 3) for _ in range(n))
    return [(nums, rng.randint(-2, 3 * n + 5))]


def bench(n, rng):
    # one large sorted list per case, with the answer near the end so a scan from the left pays in full
    nums = sorted(rng.randint(0, 4 * n) for _ in range(n))
    return [(nums, nums[-1] - rng.randint(0, 3))]
