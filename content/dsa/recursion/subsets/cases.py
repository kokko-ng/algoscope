def visual():
    return ([1, 2, 3],)


def fixed():
    return [([],), ([5],), ([-1, 4],)]


def cases(n, rng):
    return [(rng.sample(range(-20, 21), n),)]


def check(case, got, expected):
    try:
        mine = sorted(sorted(s) for s in got)
    except TypeError:
        return False
    return mine == sorted(sorted(s) for s in expected)
