# expect: fail
# Checks each node only against its two children, missing deeper violations.
def solve(root):
    if root is None:
        return True
    if root.left is not None and root.left.val >= root.val:
        return False
    if root.right is not None and root.right.val <= root.val:
        return False
    return solve(root.left) and solve(root.right)
