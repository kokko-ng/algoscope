# expect: fail
# Records the element before looking up its partner, so a value can pair with itself.
def solve(nums, target):
    seen = {}
    for j in range(len(nums)):
        seen[nums[j]] = j
        want = target - nums[j]
        if want in seen:
            return [seen[want], j]
    return [-1, -1]
