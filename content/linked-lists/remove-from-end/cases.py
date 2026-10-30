from algoscope import build_list


def visual():
    return (build_list([10, 20, 30, 40, 50, 60, 70]), 3)


def fixed():
    return [
        (build_list([1]), 1),
        (build_list([1, 2]), 1),
        (build_list([1, 2]), 2),
        (build_list([1, 2, 3]), 3),
        (build_list([1, 2, 3]), 2),
    ]


def cases(n, rng):
    size = max(n, 1)
    return [(build_list([rng.randint(0, 99) for _ in range(size)]), rng.randint(1, size))]


def bench(n, rng):
    # removing near the tail: counting first and then walking again costs almost two passes
    return [(build_list(range(n)), rng.randint(1, 3))]
