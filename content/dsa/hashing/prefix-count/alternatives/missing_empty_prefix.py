# expect: fail
# Forgets to seed the empty prefix, so runs that start at index 0 are never counted.
def solve(nums, k):
    counts = {}
    prefix = 0
    total = 0
    for x in nums:
        prefix += x
        total += counts.get(prefix - k, 0)
        counts[prefix] = counts.get(prefix, 0) + 1
    return total
