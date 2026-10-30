# expect: pass
# Recursive version of the same walk down from the root.
def solve(root, p, q):
    if root is None:
        return None
    if p < root.val and q < root.val:
        return solve(root.left, p, q)
    if p > root.val and q > root.val:
        return solve(root.right, p, q)
    return root.val
