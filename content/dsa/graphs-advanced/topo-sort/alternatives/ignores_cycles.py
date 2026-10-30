# expect: fail
# Depth-first post-order with only a visited set: it never notices a cycle and always returns an order.
def solve(graph):
    seen = set()
    post = []

    def visit(node):
        seen.add(node)
        for after in graph[node]:
            if after not in seen:
                visit(after)
        post.append(node)

    for node in graph:
        if node not in seen:
            visit(node)
    post.reverse()
    return post
