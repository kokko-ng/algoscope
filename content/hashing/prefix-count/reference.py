def solve(nums, k):
    counts = {0: 1}
    prefix = 0
    total = 0
    for i in range(len(nums)):
        prefix += nums[i]
        total += counts.get(prefix - k, 0)
        counts[prefix] = counts.get(prefix, 0) + 1
    return total
