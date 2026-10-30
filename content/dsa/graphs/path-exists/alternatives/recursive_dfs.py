# expect: pass
# Recursive depth-first search with a seen set.
def solve(graph, source, target):
    seen = set()

    def reach(node):
        if node == target:
            return True
        seen.add(node)
        for neighbour in graph[node]:
            if neighbour not in seen and reach(neighbour):
                return True
        return False

    return reach(source)
