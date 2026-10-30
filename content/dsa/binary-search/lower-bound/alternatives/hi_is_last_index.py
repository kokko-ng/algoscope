# expect: fail
# Starts hi at len(nums) - 1, so it can never answer len(nums) when every element is smaller.
def lower_bound(nums, target):
    lo, hi = 0, len(nums) - 1
    if hi < 0:
        return 0
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
