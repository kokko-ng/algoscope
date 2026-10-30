# expect: pass
# Depth-first search: reverse post-order, with a grey state to detect cycles. A different valid order.
def solve(graph):
    state = {}
    post = []

    def visit(node):
        state[node] = 1
        for after in graph[node]:
            s = state.get(after, 0)
            if s == 1:
                return False
            if s == 0 and not visit(after):
                return False
        state[node] = 2
        post.append(node)
        return True

    for node in graph:
        if node not in state and not visit(node):
            return None
    post.reverse()
    return post
