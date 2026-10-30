def random_graph(count, edges, rng, connected=False):
    graph = {i: [] for i in range(count)}
    if connected:
        for i in range(1, count):
            j = rng.randrange(i)
            graph[i].append(j)
            graph[j].append(i)
    for _ in range(edges):
        a, b = rng.randrange(count), rng.randrange(count)
        if a != b and b not in graph[a]:
            graph[a].append(b)
            graph[b].append(a)
    return graph


def visual():
    graph = {
        0: [1, 2],
        1: [0, 3],
        2: [0, 3, 4],
        3: [1, 2, 5],
        4: [2, 5],
        5: [3, 4],
        6: [7],
        7: [6],
    }
    return (graph, 0)


def fixed():
    return [
        ({0: []}, 0),
        ({0: [1], 1: [0], 2: []}, 2),
        ({0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}, 3),
    ]


def cases(n, rng):
    count = max(n, 1)
    graph = random_graph(count, count, rng)
    return [(graph, rng.randrange(count))]


def bench(n, rng):
    graph = random_graph(n, n, rng, connected=True)
    return [(graph, rng.randrange(n))]
