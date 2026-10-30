def visual():
    return ([3, 0, 2, 0, 2, 0, 2, 1],)


def fixed():
    return [([0],), ([5],), ([0, 1],), ([1, 0],), ([2, 0, 0],), ([1, 0, 1],), ([1, 1, 0, 1],), ([4, 0, 0, 0, 0],)]


def cases(n, rng):
    n = max(n, 1)
    return [([rng.choice([0, 1, 1, 2, 2, 3]) for _ in range(n)],)]


def bench(n, rng):
    return [([rng.randint(1, n) for _ in range(n)],)]
