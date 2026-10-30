# expect: fail
# Sorts and walks two pointers, returning positions in the sorted copy instead of the original indices.
def solve(nums, target):
    order = sorted(nums)
    left, right = 0, len(order) - 1
    while left < right:
        total = order[left] + order[right]
        if total == target:
            return [left, right]
        if total < target:
            left += 1
        else:
            right -= 1
    return [-1, -1]
