def solve(root):
    def fits(node, low, high):
        if node is None:
            return True
        if not low < node.val < high:
            return False
        return fits(node.left, low, node.val) and fits(node.right, node.val, high)

    return fits(root, float("-inf"), float("inf"))
