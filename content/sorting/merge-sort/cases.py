def visual():
    return ([6, 3, 8, 1, 7, 2, 5, 4],)


def fixed():
    return [([],), ([1],), ([2, 1],), ([3, 3, 3],), ([5, 4, 3, 2, 1],), ([-1, 0, -1, 2],)]


def cases(n, rng):
    return [([rng.randint(-n, n) for _ in range(n)],)]


def bench(n, rng):
    return [([rng.randint(0, 10 * n) for _ in range(n)],)]
