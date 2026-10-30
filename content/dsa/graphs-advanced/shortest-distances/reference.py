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
            if d + weight < dist.get(neighbour, float("inf")):
                dist[neighbour] = d + weight
                heapq.heappush(heap, (d + weight, neighbour))
    return {node: dist.get(node, -1) for node in graph}
