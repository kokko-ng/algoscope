def visual():
    graph = {
        "A": ["B", "C"],
        "B": ["A", "D", "E"],
        "C": ["A", "F"],
        "D": ["B", "G"],
        "E": ["B", "F"],
        "F": ["C", "E", "G"],
        "G": ["D", "F"],
    }
    return (graph, "A")


def cases(n, rng):
    count = max(n, 1)
    graph = {i: [] for i in range(count)}
    for _ in range(count):
        a, b = rng.randrange(count), rng.randrange(count)
        if a != b and b not in graph[a]:
            graph[a].append(b)
            graph[b].append(a)
    return [(graph, 0)]
