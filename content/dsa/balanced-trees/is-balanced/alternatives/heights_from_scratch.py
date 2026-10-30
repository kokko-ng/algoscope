# expect: slow
# Measures both subtrees from scratch at every node: O(n log n) on a balanced tree.
def solve(root):
    def height(node):
        if node is None:
            return 0
        return 1 + max(height(node.left), height(node.right))

    def balanced(node):
        if node is None:
            return True
        if abs(height(node.left) - height(node.right)) > 1:
            return False
        return balanced(node.left) and balanced(node.right)

    return balanced(root)
