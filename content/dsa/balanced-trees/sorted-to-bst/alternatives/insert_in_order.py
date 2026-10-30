# expect: fail
# Hangs each value to the right of the last one: a valid search tree, but a chain, not balanced.
from algoscope import TreeNode


def solve(nums):
    root = None
    tail = None
    for value in nums:
        node = TreeNode(value)
        if root is None:
            root = node
        else:
            tail.right = node
        tail = node
    return root
