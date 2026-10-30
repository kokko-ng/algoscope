def visual():
    return ([2, 0, 1, 2, 1, 0, 0, 2, 1],)


def fixed():
    return [([],), ([1],), ([2, 0],), ([2, 2, 2],), ([0, 0, 1],), ([1, 2, 0],)]


def cases(n, rng):
    return [([rng.randint(0, 2) for _ in range(n)],)]
