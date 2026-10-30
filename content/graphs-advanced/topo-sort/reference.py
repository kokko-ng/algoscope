from collections import deque


def solve(graph):
    indegree = dict.fromkeys(graph, 0)
    for node in graph:
        for after in graph[node]:
            indegree[after] += 1
    queue = deque(node for node in graph if indegree[node] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for after in graph[node]:
            indegree[after] -= 1
            if indegree[after] == 0:
                queue.append(after)
    if len(order) < len(graph):
        return None
    return order
