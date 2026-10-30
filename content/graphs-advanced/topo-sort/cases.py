def random_dag(count, edges, rng):
    rank = list(range(count))
    rng.shuffle(rank)
    graph = {i: [] for i in range(count)}
    for _ in range(edges):
        a, b = rng.randrange(count), rng.randrange(count)
        if rank[a] < rank[b] and b not in graph[a]:
            graph[a].append(b)
        elif rank[b] < rank[a] and a not in graph[b]:
            graph[b].append(a)
    return graph


def visual():
    graph = {
        "A": ["C", "D"],
        "B": ["D", "E"],
        "C": ["F"],
        "D": ["F", "G"],
        "E": ["G"],
        "F": [],
        "G": [],
    }
    return (graph,)


def fixed():
    return [
        ({},),
        ({0: []},),
        ({0: [0]},),
        ({0: [1], 1: [0]},),
        ({0: [], 1: [], 2: []},),
        ({0: [1], 1: [2], 2: [3], 3: [1], 4: []},),
        ({3: [2], 2: [1], 1: [0], 0: []},),
    ]


def cases(n, rng):
    graph = random_dag(n, int(1.5 * n), rng)
    has_edge = [node for node in graph if graph[node]]
    if has_edge and rng.random() < 0.35:
        # reverse-link one existing edge: a guaranteed cycle
        a = rng.choice(has_edge)
        b = rng.choice(graph[a])
        graph[b].append(a)
    return [(graph,)]


def bench(n, rng):
    return [(random_dag(n, 3 * n, rng),)]


def check(case, got, expected):
    graph = case[0]
    if expected is None:
        return got is None
    if not isinstance(got, (list, tuple)) or len(got) != len(graph):
        return False
    position = {}
    for i, node in enumerate(got):
        if node not in graph or node in position:
            return False
        position[node] = i
    return all(position[a] < position[b] for a in graph for b in graph[a])
