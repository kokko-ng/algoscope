# expect: slow
# General-tree LCA that ignores the ordering and searches every node.
def solve(root, p, q):
    def find(node):
        if node is None:
            return None
        left = find(node.left)
        right = find(node.right)
        if node.val in (p, q) or (left is not None and right is not None):
            return node
        return left if left is not None else right

    found = find(root)
    return found.val if found else None
