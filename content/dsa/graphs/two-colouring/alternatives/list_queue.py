# expect: slow
# Uses a plain list as the BFS queue: pop(0) shifts every waiting node.
def solve(graph):
    colour = {}
    for start in graph:
        if start in colour:
            continue
        colour[start] = 0
        queue = [start]
        while queue:
            node = queue.pop(0)
            for neighbour in graph[node]:
                if neighbour not in colour:
                    colour[neighbour] = 1 - colour[node]
                    queue.append(neighbour)
                elif colour[neighbour] == colour[node]:
                    return False
    return True
