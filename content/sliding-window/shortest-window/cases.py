def visual():
    return ([2, 3, 1, 2, 4, 3, 1, 5], 9)


def fixed():
    return [([], 5), ([5], 5), ([4], 5), ([1, 1, 1], 4), ([1, 1, 1], 3), ([10, 1, 1], 7), ([1, 2, 3, 4, 5], 15)]


def cases(n, rng):
    nums = [rng.randint(1, 20) for _ in range(n)]
    total = sum(nums)
    target = rng.randint(1, max(1, total // 3 + 1)) if rng.random() < 0.85 else total + 1
    return [(nums, target)]


def bench(n, rng):
    nums = [rng.randint(1, 20) for _ in range(n)]
    return [(nums, sum(nums) // 2)]
