def visual():
    return ([3, 1, 4, 1, 5, 9, 2, 6],)


def fixed():
    return [([],), ([5],), ([5, 5, 5],), ([5, 4, 3, 2],), ([1, 2, 3, 4],), ([2, 9, 3, 4, 1, 5],)]


def cases(n, rng):
    return [([rng.randint(0, max(3, n)) for _ in range(n)],)]


def bench(n, rng):
    return [([rng.randint(0, 10 * n) for _ in range(n)],)]
