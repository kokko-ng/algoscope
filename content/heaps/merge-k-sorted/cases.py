def _split(values, k, rng):
    lists = [[] for _ in range(k)]
    for v in values:
        lists[rng.randrange(k)].append(v)
    return [sorted(row) for row in lists]


def visual():
    return ([[1, 4, 9], [2, 3, 8], [5, 7]],)


def fixed():
    return [([],), ([[]],), ([[], [1]],), ([[1, 1], [1]],), ([[3], [1], [2]],), ([[1, 2, 3]],)]


def cases(n, rng):
    k = rng.randint(1, max(1, n // 2))
    return [(_split([rng.randint(-50, 50) for _ in range(n)], k, rng),)]


def bench(n, rng):
    return [(_split([rng.randint(0, 10 * n) for _ in range(n)], max(2, n // 8), rng),)]
