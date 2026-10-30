# expect: fail
# Never checks that target is present, so an absent target returns an empty range instead of [-1, -1].
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

    return [first_at_least(target), first_at_least(target + 1) - 1]
