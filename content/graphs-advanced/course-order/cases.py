def random_plan(n, m, rng):
    rank = list(range(n))
    rng.shuffle(rank)
    pairs = []
    for _ in range(m):
        a, b = rng.randrange(n), rng.randrange(n)
        if rank[a] > rank[b]:
            pairs.append([a, b])
        elif rank[b] > rank[a]:
            pairs.append([b, a])
    return pairs


def visual():
    return (6, [[1, 0], [2, 1], [3, 1], [4, 2], [4, 3], [5, 4], [2, 5]])


def fixed():
    return [
        (0, []),
        (1, []),
        (1, [[0, 0]]),
        (2, [[1, 0]]),
        (2, [[1, 0], [0, 1]]),
        (3, [[1, 0], [2, 1], [1, 0]]),
        (4, [[1, 0], [2, 1], [3, 2], [1, 3]]),
    ]


def cases(n, rng):
    if n == 0:
        return [(0, [])]
    pairs = random_plan(n, int(1.5 * n), rng)
    if pairs and rng.random() < 0.4:
        course, required = rng.choice(pairs)
        pairs.append([required, course])
    rng.shuffle(pairs)
    return [(n, pairs)]


def bench(n, rng):
    return [(n, random_plan(n, 3 * n, rng))]
