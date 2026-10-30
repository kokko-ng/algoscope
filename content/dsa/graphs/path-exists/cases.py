def visual():
    graph = {
        "A": ["C", "B"],
        "B": ["D"],
        "C": ["D", "E"],
        "D": ["B"],
        "E": ["F"],
        "F": [],
        "G": ["F"],
    }
    return (graph, "A", "F")


def fixed():
    return [
        ({0: []}, 0, 0),
        ({0: [1], 1: []}, 1, 0),
        ({0: [1], 1: [0], 2: []}, 0, 2),
        ({0: [1], 1: [2], 2: [0], 3: [0]}, 0, 3),
        ({0: [1], 1: [2], 2: [0], 3: [0]}, 3, 2),
    ]


def cases(n, rng):
    count = max(n, 1)
    graph = {i: [] for i in range(count)}
    for _ in range(int(count * rng.choice([0.6, 1.0, 1.5]))):
        a, b = rng.randrange(count), rng.randrange(count)
        if b not in graph[a]:
            graph[a].append(b)
    return [(graph, rng.randrange(count), rng.randrange(count))]


def bench(n, rng):
    # every node is reachable from 0 except the target, so the search must explore everything
    target = n - 1
    graph = {i: [] for i in range(n)}
    for i in range(1, n - 1):
        graph[rng.randrange(i)].append(i)
    for _ in range(2 * n):
        a, b = rng.randrange(n - 1), rng.randrange(n - 1)
        graph[a].append(b)
    graph[target] = [rng.randrange(n - 1) for _ in range(3)]
    return [(graph, 0, target)]
