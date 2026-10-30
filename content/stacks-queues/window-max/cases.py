def visual():
    return ([1, 3, -1, -3, 5, 3, 6, 7], 3)


def fixed():
    return [([], 1), ([4], 1), ([2, 1], 2), ([1, 2], 1), ([5, 5, 5], 2), ([9, 8, 7, 6], 4)]


def cases(n, rng):
    nums = [rng.randint(-10, 10) for _ in range(n)]
    return [(nums, rng.randint(1, max(n, 1)))]


def bench(n, rng):
    # wide windows: taking max over each window costs k per position
    return [([rng.randint(0, 1000) for _ in range(n)], n // 2)]
