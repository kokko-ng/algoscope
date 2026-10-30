from algoscope import build_list


def visual():
    return (build_list([1, 2, 3, 4, 5, 6]),)


def cases(n, rng):
    return [(build_list([rng.randint(0, 99) for _ in range(n)]),)]
