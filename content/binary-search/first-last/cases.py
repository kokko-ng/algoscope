def visual():
    return ([1, 2, 4, 4, 4, 4, 7, 9], 4)


def fixed():
    return [([], 3), ([3], 3), ([3], 2), ([3, 3, 3], 3), ([1, 3, 3], 3), ([3, 3, 5], 3), ([1, 2, 3], 4), ([1, 2, 3], 0)]


def cases(n, rng):
    nums = sorted(rng.randint(0, n // 2 + 2) for _ in range(n))
    target = rng.choice(nums) if nums and rng.random() < 0.75 else rng.choice([-1, n // 2 + 3])
    return [(nums, target)]


def bench(n, rng):
    # a long run of the target: finding one copy and walking outwards costs the length of the run
    run = n // 2
    left = (n - run) // 2
    nums = list(range(left)) + [left] * run + list(range(left + 1, left + 1 + n - run - left))
    return [(nums, left)]
