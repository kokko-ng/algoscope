def visual():
    return ([5, 12, 9, 5, 12],)


def fixed():
    return [([7],), ([1, 1, 2],), ([2, 1, 1],), ([0, 3, 3],), ([4, 0, 4],), ([6, 1, 6, 2, 1],)]


def cases(n, rng):
    pairs = n // 2
    values = rng.sample(range(10 * n + 10), pairs + 1)
    nums = values[:pairs] * 2 + [values[pairs]]
    rng.shuffle(nums)
    return [(nums,)]
