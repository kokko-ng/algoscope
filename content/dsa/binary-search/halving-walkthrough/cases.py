def visual():
    return ([2, 5, 8, 12, 16, 23, 38, 41, 56, 72], 38)


def cases(n, rng):
    nums = sorted(rng.sample(range(10 * n + 10), n))
    target = rng.choice(nums) if nums and rng.random() < 0.7 else -1
    return [(nums, target)]
