# expect: fail
# Compares only the root's two subtrees, so a lopsided node further down goes unnoticed.
def solve(root):
    def height(node):
        if node is None:
            return 0
        return 1 + max(height(node.left), height(node.right))

    if root is None:
        return True
    return abs(height(root.left) - height(root.right)) <= 1
