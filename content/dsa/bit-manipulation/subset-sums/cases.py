def visual():
    return ([2, 3, 5, 7],)


def fixed():
    return [([],), ([4],), ([1, -1],), ([0, 0, 0],)]


def cases(n, rng):
    return [([rng.randint(-50, 50) for _ in range(n)],)]
