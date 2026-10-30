def visual():
    return ([5, 1, 9, 3, 7, 6, 2, 8], 3)


def fixed():
    return [([], 0), ([4], 0), ([4], 1), ([2, 2, 2], 2), ([3, 1, 2], 3), ([-5, -1, -3], 1)]


def cases(n, rng):
    nums = [rng.randint(-100, 100) for _ in range(n)]
    return [(nums, rng.randint(0, n))]


def bench(n, rng):
    nums = [rng.randint(0, 10 * n) for _ in range(n)]
    return [(nums, max(1, n // 10))]


def check(case, got, expected):
    try:
        return sorted(got) == sorted(expected)
    except TypeError:
        return False
