def visual():
    return ([5, 9, 2, 7, 4, 8, 1, 6],)


def fixed():
    return [([],), ([1],), ([2, 1],), ([3, 3, 3],), ([1, 2, 3, 4, 5],), ([5, 4, 3, 2, 1],), ([2, -1, 2, 0],)]


def cases(n, rng):
    return [([rng.randint(-n, n) for _ in range(n)],)]


def bench(n, rng):
    return [(rng.sample(range(10 * n), n),)]
