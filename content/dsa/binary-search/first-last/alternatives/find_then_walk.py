# expect: slow
# Binary search for one copy, then walk outwards: correct, but the walk costs the length of the run.
def solve(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            first = last = mid
            while first > 0 and nums[first - 1] == target:
                first -= 1
            while last < len(nums) - 1 and nums[last + 1] == target:
                last += 1
            return [first, last]
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return [-1, -1]
