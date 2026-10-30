# expect: slow
# Remembers visited nodes in a plain list, so every membership test scans it.
def solve(graph, source, target):
    seen = []
    stack = [source]
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if node in seen:
            continue
        seen.append(node)
        for neighbour in graph[node]:
            stack.append(neighbour)
    return False
