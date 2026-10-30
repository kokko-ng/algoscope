# expect: slow
# Correct, but every level copies its halves with slices: O(n log n).
from algoscope import TreeNode


def solve(nums):
    if not nums:
        return None
    mid = len(nums) // 2
    return TreeNode(nums[mid], solve(nums[:mid]), solve(nums[mid + 1 :]))
