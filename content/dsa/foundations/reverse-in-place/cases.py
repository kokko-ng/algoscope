def visual():
    return (["a", "b", "c", "d", "e", "f"],)


def fixed():
    return [([],), ([1],), ([1, 2],), ([1, 2, 3],)]


def cases(n, rng):
    return [([rng.randint(0, 99) for _ in range(n)],)]
