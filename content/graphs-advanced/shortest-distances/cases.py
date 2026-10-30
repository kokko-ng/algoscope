def random_weighted(count, edges, rng, reach_from=None):
    graph = {i: [] for i in range(count)}
    if reach_from is not None:
        order = list(range(count))
        order.remove(reach_from)
        rng.shuffle(order)
        order.insert(0, reach_from)
        for i in range(1, count):
            graph[order[rng.randrange(i)]].append((order[i], rng.randint(1, 50)))
    for _ in range(edges):
        a, b = rng.randrange(count), rng.randrange(count)
        if a != b:
            graph[a].append((b, rng.randint(0, 20)))
    return graph


def visual():
    graph = {
        "S": [("A", 7), ("B", 2)],
        "A": [("C", 1)],
        "B": [("A", 3), ("C", 8), ("D", 5)],
        "C": [("E", 2)],
        "D": [("C", 1), ("E", 6)],
        "E": [],
        "F": [("S", 1)],
    }
    return (graph, "S")


def fixed():
    return [
        ({0: []}, 0),
        ({0: [(1, 5)], 1: []}, 1),
        ({0: [(1, 0)], 1: [(2, 0)], 2: [(0, 0)]}, 0),
        ({0: [(1, 10), (2, 1)], 1: [], 2: [(1, 1)]}, 0),
    ]


def cases(n, rng):
    count = max(n, 1)
    graph = random_weighted(count, int(count * rng.choice([1.0, 2.0, 3.0])), rng)
    return [(graph, rng.randrange(count))]


def bench(n, rng):
    return [(random_weighted(n, 2 * n, rng, reach_from=0), 0)]
