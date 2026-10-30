import heapq


def solve(graph, source):
    dist = {source: 0}
    done = set()
    heap = [(0, source)]
    while heap:
        d, node = heapq.heappop(heap)
        if node in done:
            continue
        done.add(node)
        for neighbour, weight in graph[node]:
            candidate = d + weight
            if candidate < dist.get(neighbour, float("inf")):
                dist[neighbour] = candidate
                heapq.heappush(heap, (candidate, neighbour))
    return dist
