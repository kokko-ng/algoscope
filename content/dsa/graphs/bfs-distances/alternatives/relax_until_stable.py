# expect: slow
# Relax every edge in sweeps until no distance improves: one sweep per level in the worst case.
def solve(graph, start):
    inf = float("inf")
    dist = {node: inf for node in graph}
    dist[start] = 0
    changed = True
    while changed:
        changed = False
        for node in graph:
            if dist[node] == inf:
                continue
            for neighbour in graph[node]:
                if dist[node] + 1 < dist[neighbour]:
                    dist[neighbour] = dist[node] + 1
                    changed = True
    return {node: (d if d != inf else -1) for node, d in dist.items()}
