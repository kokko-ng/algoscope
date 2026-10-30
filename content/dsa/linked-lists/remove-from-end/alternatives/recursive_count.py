# expect: pass
# Recursion counts positions on the way back from the tail and unlinks the k-th node there.
def solve(head, k):
    def walk(node):
        if node is None:
            return None, 0
        rest, depth = walk(node.next)
        node.next = rest
        depth += 1
        if depth == k:
            return node.next, depth
        return node, depth

    return walk(head)[0]
