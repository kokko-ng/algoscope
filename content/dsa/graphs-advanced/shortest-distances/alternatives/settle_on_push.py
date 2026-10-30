# expect: fail
# Fixes a node's distance the first time it is reached, as in BFS, so a cheaper later route is ignored.
import heapq


def solve(graph, source):
    dist = {source: 0}
    heap = [(0, source)]
    while heap:
        d, node = heapq.heappop(heap)
        for neighbour, weight in graph[node]:
            if neighbour not in dist:
                dist[neighbour] = d + weight
                heapq.heappush(heap, (d + weight, neighbour))
    return {node: dist.get(node, -1) for node in graph}
