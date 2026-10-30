from algoscope import build_list


def visual():
    return (build_list([1, 4, 6, 9]), build_list([2, 3, 7, 10, 12]))


def fixed():
    return [
        (None, None),
        (build_list([1]), None),
        (None, build_list([1, 2])),
        (build_list([2, 2]), build_list([2])),
        (build_list([5, 6]), build_list([1, 2])),
    ]


def cases(n, rng):
    m = rng.randint(0, n)
    a = sorted(rng.randint(0, 3 * n + 3) for _ in range(n))
    b = sorted(rng.randint(0, 3 * n + 3) for _ in range(m))
    return [(build_list(a), build_list(b))]


def bench(n, rng):
    return [(build_list(range(0, 2 * n, 2)), build_list(range(1, 2 * n, 2)))]
