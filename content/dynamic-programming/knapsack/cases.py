def visual():
    return ([1, 3, 4, 5], [1, 4, 5, 7], 7)


def fixed():
    return [
        ([], [], 10),
        ([5], [10], 4),
        ([5], [10], 5),
        ([1, 1, 1], [2, 3, 4], 0),
        ([2, 2, 3], [3, 3, 5], 4),
        ([4, 3, 2], [10, 7, 6], 5),
    ]


def cases(n, rng):
    weights = [rng.randint(1, n + 2) for _ in range(n)]
    values = [rng.randint(1, 30) for _ in range(n)]
    capacity = rng.randint(0, sum(weights) // 2 + 1)
    return [(weights, values, capacity)]


def bench(n, rng):
    weights = [rng.randint(1, n) for _ in range(n)]
    values = [rng.randint(1, 100) for _ in range(n)]
    return [(weights, values, 2 * n)]
