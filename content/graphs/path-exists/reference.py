def solve(graph, source, target):
    seen = set()
    stack = [source]
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if node in seen:
            continue
        seen.add(node)
        for neighbour in graph[node]:
            if neighbour not in seen:
                stack.append(neighbour)
    return False
