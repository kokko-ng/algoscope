# expect: slow
# Scan every node for one with nothing left before it, again and again: O(V^2).
def solve(graph):
    indegree = dict.fromkeys(graph, 0)
    for node in graph:
        for after in graph[node]:
            indegree[after] += 1
    placed = set()
    order = []
    while len(order) < len(graph):
        found = None
        for node in graph:
            if node not in placed and indegree[node] == 0:
                found = node
                break
        if found is None:
            return None
        placed.add(found)
        order.append(found)
        for after in graph[found]:
            indegree[after] -= 1
    return order
