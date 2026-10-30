def visual():
    return ([1, 1, 2, 3, 3, 3, 5, 8, 8],)


def fixed():
    return [([],), ([4],), ([2, 2, 2],)]


def cases(n, rng):
    return [(sorted(rng.randint(0, n) for _ in range(n)),)]
