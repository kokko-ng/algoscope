def visual():
    return ([7, 2, 5, 1, 6, 4, 3],)


def fixed():
    return [([],), ([5],), ([5, 4, 3],), ([1, 2],), ([3, 3, 3],)]


def cases(n, rng):
    return [([rng.randint(0, 1000) for _ in range(n)],)]
