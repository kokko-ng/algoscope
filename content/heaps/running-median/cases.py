def visual():
    return ([5, 15, 1, 3, 8, 7, 9],)


def fixed():
    return [([],), ([4],), ([4, 2],), ([1, 1, 1],), ([3, 2, 1, 0],), ([-2, 6, -8, 4],)]


def cases(n, rng):
    return [([rng.randint(-100, 100) for _ in range(n)],)]


def bench(n, rng):
    return [([rng.randint(0, 10 * n) for _ in range(n)],)]
