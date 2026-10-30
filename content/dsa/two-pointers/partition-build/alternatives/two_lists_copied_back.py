# expect: fail
# Copies into two new lists and writes them back: O(n) extra space, which the statement forbids.
def solve(nums, pivot):
    nums[:] = [v for v in nums if v < pivot] + [v for v in nums if v >= pivot]
