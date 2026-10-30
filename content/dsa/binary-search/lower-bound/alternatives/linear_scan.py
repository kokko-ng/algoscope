# expect: slow
# Scan from the left for the first element >= target: correct, but O(n).
def lower_bound(nums, target):
    for i in range(len(nums)):
        if nums[i] >= target:
            return i
    return len(nums)
