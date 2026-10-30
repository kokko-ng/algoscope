# expect: pass
# BFS one ring at a time with plain lists instead of a deque.
def solve(graph, start):
    dist = {node: -1 for node in graph}
    dist[start] = 0
    frontier = [start]
    level = 0
    while frontier:
        level += 1
        nxt = []
        for node in frontier:
            for neighbour in graph[node]:
                if dist[neighbour] == -1:
                    dist[neighbour] = level
                    nxt.append(neighbour)
        frontier = nxt
    return dist
