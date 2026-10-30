# expect: fail
# Searches only from the first node, ignoring the other pieces of the graph.
from collections import deque


def solve(graph):
    if not graph:
        return True
    start = next(iter(graph))
    colour = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if neighbour not in colour:
                colour[neighbour] = 1 - colour[node]
                queue.append(neighbour)
            elif colour[neighbour] == colour[node]:
                return False
    return True
