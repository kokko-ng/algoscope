def visual():
    return ([1, 3, 4], 6)


def fixed():
    return [
        ([1], 0),
        ([2], 3),
        ([2], 4),
        ([5, 3], 7),
        ([1, 5, 6, 9], 11),
        ([7, 4], 1),
    ]


def cases(n, rng):
    k = rng.randint(1, max(1, min(5, n)))
    coins = rng.sample(range(1, n + 8), k)
    return [(coins, rng.randint(0, 3 * n + 5))]


def bench(n, rng):
    # small coprime coins make every total reachable, so top-down and bottom-up visit the same states
    coins = [2, 3, *rng.sample(range(4, 2 * n), max(2, n // 5) - 2)]
    return [(coins, 3 * n)]
