# expect: fail
# Ignores cycles: without a seen set the search can loop forever.
def solve(graph, source, target):
    stack = [source]
    while stack:
        node = stack.pop()
        if node == target:
            return True
        for neighbour in graph[node]:
            stack.append(neighbour)
    return False
