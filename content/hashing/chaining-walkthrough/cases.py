def visual():
    return [
        ("put", 12, "ant"),
        ("put", 3, "bee"),
        ("put", 7, "cat"),
        ("put", 22, "dog"),
        ("put", 9, "elk"),
        ("get", 7),
        ("put", 12, "fox"),
        ("get", 17),
    ]


def cases(n, rng):
    ops = []
    for _ in range(n):
        if rng.random() < 0.6:
            ops.append(("put", rng.randint(0, 2 * n), rng.randint(0, 99)))
        else:
            ops.append(("get", rng.randint(0, 2 * n)))
    return [ops]
