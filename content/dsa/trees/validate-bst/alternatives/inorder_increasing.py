# expect: pass
# Iterative in-order walk: a search tree reads strictly increasing.
def solve(root):
    stack = []
    node = root
    prev = None
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        if prev is not None and node.val <= prev:
            return False
        prev = node.val
        node = node.right
    return True
