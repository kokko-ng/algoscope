# expect: pass
# Returns (balanced, height) pairs instead of a sentinel.
def solve(root):
    def walk(node):
        if node is None:
            return True, 0
        left_ok, left = walk(node.left)
        right_ok, right = walk(node.right)
        ok = left_ok and right_ok and abs(left - right) <= 1
        return ok, 1 + max(left, right)

    return walk(root)[0]
