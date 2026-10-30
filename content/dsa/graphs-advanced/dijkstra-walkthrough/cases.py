def visual():
    graph = {
        "A": [("B", 4), ("C", 1)],
        "B": [("A", 4), ("C", 2), ("D", 1)],
        "C": [("A", 1), ("B", 2), ("D", 5), ("E", 8)],
        "D": [("B", 1), ("C", 5), ("E", 3)],
        "E": [("C", 8), ("D", 3), ("F", 1)],
        "F": [("E", 1)],
    }
    return (graph, "A")


def cases(n, rng):
    count = max(n, 1)
    graph = {i: [] for i in range(count)}
    for _ in range(2 * count):
        a, b = rng.randrange(count), rng.randrange(count)
        if a != b:
            w = rng.randint(1, 9)
            graph[a].append((b, w))
            graph[b].append((a, w))
    return [(graph, 0)]
