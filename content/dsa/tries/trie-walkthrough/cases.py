def visual():
    return [("insert", w) for w in ["car", "cat", "cart", "dog", "do"]]


def cases(n, rng):
    return [[("insert", "".join(rng.choice("abc") for _ in range(rng.randint(1, 5)))) for _ in range(n)]]
