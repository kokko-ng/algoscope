# expect: fail
# Breadth-first search adding weights along the first route found, ignoring that a longer route can be shorter.
from collections import deque


def solve(graph, source):
    dist = {source: 0}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        for neighbour, weight in graph[node]:
            if neighbour not in dist:
                dist[neighbour] = dist[node] + weight
                queue.append(neighbour)
    return {node: dist.get(node, -1) for node in graph}
