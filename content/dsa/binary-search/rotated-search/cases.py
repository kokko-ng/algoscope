def rotated(values, shift):
    return values[shift:] + values[:shift]


def visual():
    return ([15, 18, 22, 27, 3, 6, 9, 11], 6)


def fixed():
    return [([], 1), ([4], 4), ([4], 5), ([2, 1], 1), ([2, 1], 2), ([1, 2], 2), ([3, 1, 2], 3), ([3, 1, 2], 4)]


def cases(n, rng):
    values = sorted(rng.sample(range(5 * n + 5), n))
    nums = rotated(values, rng.randrange(n)) if n else values
    target = rng.choice(nums) if nums and rng.random() < 0.7 else 5 * n + 9
    return [(nums, target)]


def bench(n, rng):
    # even values only, so an odd target falls in a gap and every scan runs to the end
    values = [2 * i for i in range(n)]
    nums = rotated(values, rng.randrange(n))
    return [(nums, 2 * rng.randrange(n) + 1)]
