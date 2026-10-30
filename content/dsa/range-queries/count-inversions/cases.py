def visual():
    return ([3, 1, 4, 1, 5, 2],)


def fixed():
    return [([],), ([7],), ([1, 2, 3],), ([3, 2, 1],), ([2, 2, 2],), ([2, 1, 2, 1],), ([-1, -5, 10, 0],)]


def cases(n, rng):
    top = rng.choice([max(1, n // 3), 10 * n + 10])
    return [([rng.randint(-top, top) for _ in range(n)],)]


def bench(n, rng):
    nums = list(range(n))
    rng.shuffle(nums)
    return [(nums,)]
