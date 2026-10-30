def visual():
    return ([[8, 10], [1, 3], [15, 18], [2, 6], [9, 12], [17, 20], [4, 5]],)


def cases(n, rng):
    out = []
    for _ in range(n):
        start = rng.randint(0, 5 * n)
        out.append([start, start + rng.randint(0, 6)])
    return [(out,)]
