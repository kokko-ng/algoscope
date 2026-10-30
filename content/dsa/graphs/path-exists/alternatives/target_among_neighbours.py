# expect: fail
# Only checks for target among neighbours, so a node never reaches itself.
def solve(graph, source, target):
    seen = {source}
    stack = [source]
    while stack:
        node = stack.pop()
        for neighbour in graph[node]:
            if neighbour == target:
                return True
            if neighbour not in seen:
                seen.add(neighbour)
                stack.append(neighbour)
    return False
