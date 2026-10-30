# expect: pass
# Depth-first colouring with recursion.
def solve(graph):
    colour = {}

    def paint(node, c):
        colour[node] = c
        for neighbour in graph[node]:
            if neighbour not in colour:
                if not paint(neighbour, 1 - c):
                    return False
            elif colour[neighbour] == c:
                return False
        return True

    for start in graph:
        if start not in colour and not paint(start, 0):
            return False
    return True
