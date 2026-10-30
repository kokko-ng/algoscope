def visual():
    return (list("{[()()]}(]"),)


def cases(n, rng):
    return [([rng.choice("()[]{}") for _ in range(n)],)]
