# expect: slow
# Compare each node with the max of its left subtree and the min of its right subtree, recomputed every time.
def solve(root):
    def values(node):
        if node is None:
            return []
        return values(node.left) + [node.val] + values(node.right)

    def ok(node):
        if node is None:
            return True
        left, right = values(node.left), values(node.right)
        if left and max(left) >= node.val:
            return False
        if right and min(right) <= node.val:
            return False
        return ok(node.left) and ok(node.right)

    return ok(root)
