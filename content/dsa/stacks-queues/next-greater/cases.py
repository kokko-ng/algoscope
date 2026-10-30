def visual():
    return ([4, 2, 1, 5, 3, 3, 6, 2],)


def fixed():
    return [([],), ([7],), ([1, 2],), ([2, 1],), ([3, 3, 3],), ([5, 4, 3, 2, 1],)]


def cases(n, rng):
    return [([rng.randint(0, 20) for _ in range(n)],)]


def bench(n, rng):
    # mostly descending: a scan to the right from every index finds nothing larger for a long time
    return [([n - i + rng.randint(0, 1) for i in range(n)] + [n + 5],)]
