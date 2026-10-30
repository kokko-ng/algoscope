def visual():
    return ([1, 2, 3],)


def fixed():
    return [([],), ([5],), ([2, 9],)]


def cases(n, rng):
    return [(rng.sample(range(-20, 21), n),)]


def check(case, got, expected):
    try:
        mine = sorted(list(p) for p in got)
    except TypeError:
        return False
    return mine == sorted(list(p) for p in expected)
