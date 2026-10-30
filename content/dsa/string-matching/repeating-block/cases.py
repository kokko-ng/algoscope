def visual():
    return (list("abaababaab"),)


def fixed():
    return [
        (["a"],),
        (list("aa"),),
        (list("ab"),),
        (list("abcab"),),
        (list("abab"),),
        (list("aabaab"),),
        (list("abaaba"),),
        (list("ababa"),),
    ]


def cases(n, rng):
    if n == 0:
        return []
    alphabet = rng.choice(["ab", "abc"])
    style = rng.randrange(3)
    if style == 0:
        sizes = [d for d in range(1, n + 1) if n % d == 0]
        size = rng.choice(sizes)
    elif style == 1:
        size = rng.randint(1, n)
    else:
        size = n
    block = [rng.choice(alphabet) for _ in range(size)]
    return [([block[i % size] for i in range(n)],)]


def bench(n, rng):
    return [(["a"] * (n - 1) + ["b"],)]
