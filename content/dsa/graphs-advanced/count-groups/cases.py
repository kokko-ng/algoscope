def visual():
    return (7, [(0, 1), (2, 3), (1, 2), (4, 5), (3, 0), (5, 6), (6, 0)])


def fixed():
    return [
        (0, []),
        (1, [(0, 0)]),
        (3, [(0, 1), (1, 0), (2, 2)]),
        (4, [(0, 1), (2, 3), (1, 3)]),
    ]


def cases(n, rng):
    if n == 0:
        return [(0, [])]
    pairs = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(1, 2 * n))]
    return [(n, pairs)]


def bench(n, rng):
    # chains in both directions, then repeated links from the far end
    forward = [(i, i + 1) for i in range(n - 1)] + [(0, rng.randrange(n)) for _ in range(n)]
    backward = [(i + 1, i) for i in range(n - 1)] + [(n - 1, rng.randrange(n)) for _ in range(n)]
    return [(n, forward), (n, backward)]
