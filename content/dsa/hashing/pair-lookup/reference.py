def solve(nums, target):
    seen = {}
    for j in range(len(nums)):
        want = target - nums[j]
        if want in seen:
            return [seen[want], j]
        seen[nums[j]] = j
    return [-1, -1]
