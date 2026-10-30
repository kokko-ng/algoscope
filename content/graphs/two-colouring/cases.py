def bipartite(count, edges, rng):
    side = [rng.randrange(2) for _ in range(count)]
    graph = {i: [] for i in range(count)}
    for _ in range(edges):
        a, b = rng.randrange(count), rng.randrange(count)
        if side[a] != side[b] and b not in graph[a]:
            graph[a].append(b)
            graph[b].append(a)
    return graph, side


def visual():
    graph = {
        "A": ["B", "D"],
        "B": ["A", "C", "E"],
        "C": ["B", "F"],
        "D": ["A", "E"],
        "E": ["B", "D", "F"],
        "F": ["C", "E"],
    }
    return (graph,)


def fixed():
    return [
        ({},),
        ({0: []},),
        ({0: [1], 1: [0]},),
        ({0: [1, 2], 1: [0, 2], 2: [0, 1]},),
        ({0: [1], 1: [0], 2: [3, 4], 3: [2, 4], 4: [2, 3]},),
        ({0: [1], 1: [0, 2], 2: [1, 3], 3: [2, 0], 4: [], 5: [6], 6: [5]},),
    ]


def cases(n, rng):
    count = max(n, 1)
    graph, side = bipartite(count, int(count * 1.5), rng)
    if count >= 3 and rng.random() < 0.5:
        # one edge inside a side may or may not close an odd cycle
        same = [i for i in range(count) if side[i] == side[0]]
        if len(same) >= 2:
            a, b = rng.sample(same, 2)
            if b not in graph[a]:
                graph[a].append(b)
                graph[b].append(a)
    return [(graph,)]


def bench(n, rng):
    graph, _ = bipartite(n, 3 * n, rng)
    return [(graph,)]
