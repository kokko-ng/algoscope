def visual():
    return ([8, 3, 11, 6, 2, 9, 5], 7)


def fixed():
    return [([], 5), ([2], 4), ([2, 2], 4), ([3, 1], 5), ([-4, 7, 0, 4], 0), ([5, 5, 5], 10)]


def cases(n, rng):
    nums = [rng.randint(-5 * n - 10, 5 * n + 10) for _ in range(n)]
    if n >= 2 and rng.random() < 0.8:
        i, j = rng.sample(range(n), 2)
        target = nums[i] + nums[j]
    else:
        target = 100 * n + 999
    return [(nums, target)]


def bench(n, rng):
    return [([rng.randint(0, 10 * n) for _ in range(n)], 100 * n + 999)]


def check(case, got, expected):
    nums, target = case
    try:
        if expected == [-1, -1]:
            return list(got) == [-1, -1]
        i, j = got
        return 0 <= i < j < len(nums) and nums[i] + nums[j] == target
    except (TypeError, ValueError):
        return False
