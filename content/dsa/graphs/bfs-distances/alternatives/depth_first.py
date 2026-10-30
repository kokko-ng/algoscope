# expect: fail
# Uses a stack instead of a queue: the first distance found is not always the shortest.
def solve(graph, start):
    dist = {start: 0}
    stack = [start]
    while stack:
        node = stack.pop()
        for neighbour in graph[node]:
            if neighbour not in dist:
                dist[neighbour] = dist[node] + 1
                stack.append(neighbour)
    return {node: dist.get(node, -1) for node in graph}
