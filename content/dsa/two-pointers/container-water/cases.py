def visual():
    return ([1, 8, 6, 2, 5, 4, 8, 3, 7],)


def fixed():
    return [([],), ([5],), ([3, 4],), ([2, 2, 2, 2],), ([1, 2, 3, 4, 5],), ([5, 4, 3, 2, 1],)]


def cases(n, rng):
    return [([rng.randint(0, 3 * n + 3) for _ in range(n)],)]
