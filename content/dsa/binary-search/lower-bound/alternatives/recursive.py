# expect: pass
# Recursive halving of the window instead of a loop.
def lower_bound(nums, target, lo=0, hi=None):
    if hi is None:
        hi = len(nums)
    if lo >= hi:
        return lo
    mid = (lo + hi) // 2
    if nums[mid] < target:
        return lower_bound(nums, target, mid + 1, hi)
    return lower_bound(nums, target, lo, mid)
