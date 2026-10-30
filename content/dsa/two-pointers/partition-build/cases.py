def visual():
    return ([7, 2, 9, 4, 1, 8, 3, 6], 5)


def fixed():
    return [
        ([], 3),
        ([4], 3),
        ([2], 3),
        ([1, 2, 3], 10),
        ([7, 8, 9], 0),
        ([5, 5, 1, 5, 2], 5),
        ([9, 1], 5),
    ]


def cases(n, rng):
    nums = [rng.randint(-n - 5, n + 5) for _ in range(n)]
    pivot = rng.choice(nums) if nums and rng.random() < 0.7 else rng.randint(-n - 5, n + 5)
    return [(nums, pivot)]


def bench(n, rng):
    nums = [rng.randint(0, 10 * n) for _ in range(n)]
    return [(nums, 5 * n)]


def check(case, got, expected):
    nums, pivot = case
    try:
        if sorted(got) != sorted(nums):
            return False
    except TypeError:
        return False
    split = sum(1 for v in nums if v < pivot)
    return all(v < pivot for v in got[:split]) and all(v >= pivot for v in got[split:])
