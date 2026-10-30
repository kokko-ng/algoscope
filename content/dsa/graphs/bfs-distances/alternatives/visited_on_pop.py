# expect: fail
# Marks nodes visited when popped, not when queued, so a queued node's distance gets overwritten.
from collections import deque


def solve(graph, start):
    dist = {start: 0}
    visited = set()
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        for neighbour in graph[node]:
            if neighbour not in visited:
                dist[neighbour] = dist[node] + 1
                queue.append(neighbour)
    return {node: dist.get(node, -1) for node in graph}
