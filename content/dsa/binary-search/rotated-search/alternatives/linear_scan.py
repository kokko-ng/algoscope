# expect: slow
# Scan every element: correct, but O(n).
def solve(nums, target):
    for i in range(len(nums)):
        if nums[i] == target:
            return i
    return -1
