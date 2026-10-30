def visual():
    return ([5, 2, 8, 1, 9, 3, 7],)


def fixed():
    return [([],), ([1],), ([2, 1],)]


def cases(n, rng):
    return [([rng.randint(0, 99) for _ in range(n)],)]
