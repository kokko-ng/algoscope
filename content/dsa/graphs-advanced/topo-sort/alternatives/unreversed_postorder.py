# expect: fail
# Returns the depth-first post-order without reversing it, so edges point backwards.
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
    return post
