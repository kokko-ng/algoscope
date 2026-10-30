def visual():
    return (list("abacabab"),)


def cases(n, rng):
    return [([rng.choice("ab") for _ in range(n)],)]
