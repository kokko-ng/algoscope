# expect: fail
# Off-by-one: returns the first index past the run as the last index.
def solve(nums, target):
    def first_at_least(value):
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < value:
                lo = mid + 1
            else:
                hi = mid
        return lo

    start = first_at_least(target)
    if start == len(nums) or nums[start] != target:
        return [-1, -1]
    return [start, first_at_least(target + 1)]
