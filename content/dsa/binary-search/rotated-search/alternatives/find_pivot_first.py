# expect: pass
# Two searches: halve to find the rotation point, then binary search the sorted half that can hold target.
def solve(nums, target):
    if not nums:
        return -1
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    start = lo
    if start > 0 and target >= nums[0]:
        lo, hi = 0, start - 1
    else:
        lo, hi = start, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
