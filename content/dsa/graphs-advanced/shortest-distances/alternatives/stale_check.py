# expect: pass
# Lazy deletion by comparing the popped distance with the best known one, instead of a done set.
import heapq


def solve(graph, source):
    dist = {node: -1 for node in graph}
    best = {source: 0}
    heap = [(0, source)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > best[node]:
            continue
        dist[node] = d
        for neighbour, weight in graph[node]:
            candidate = d + weight
            if neighbour not in best or candidate < best[neighbour]:
                best[neighbour] = candidate
                heapq.heappush(heap, (candidate, neighbour))
    return dist
