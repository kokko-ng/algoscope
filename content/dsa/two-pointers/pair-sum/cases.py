def visual():
    return ([1, 3, 4, 6, 8, 11, 14], 17)


def fixed():
    return [([], 5), ([2], 4), ([1, 2], 3), ([1, 2], 4), ([-3, -1, 0, 2, 5], -4)]


def cases(n, rng):
    nums = sorted(rng.sample(range(-5 * n - 10, 5 * n + 10), n))
    if n >= 2 and rng.random() < 0.8:
        i, j = sorted(rng.sample(range(n), 2))
        target = nums[i] + nums[j]
    else:
        target = 10 * n + 99
    return [(nums, target)]


def check(case, got, expected):
    nums, target = case
    if expected == [-1, -1]:
        return got == [-1, -1]
    i, j = got
    return 0 <= i < j < len(nums) and nums[i] + nums[j] == target


def bench(n, rng):
    nums = sorted(rng.sample(range(-5 * n - 10, 5 * n + 10), n))
    return [(nums, 10 * n + 99)]
