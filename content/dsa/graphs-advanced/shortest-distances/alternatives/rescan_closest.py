# expect: slow
# Dijkstra without a heap: rescan every node for the closest unsettled one, O(V^2).
def solve(graph, source):
    inf = float("inf")
    dist = {node: inf for node in graph}
    dist[source] = 0
    done = set()
    while True:
        best = None
        for node in graph:
            if node not in done and dist[node] < inf and (best is None or dist[node] < dist[best]):
                best = node
        if best is None:
            break
        done.add(best)
        for neighbour, weight in graph[best]:
            if dist[best] + weight < dist[neighbour]:
                dist[neighbour] = dist[best] + weight
    return {node: (d if d != inf else -1) for node, d in dist.items()}
