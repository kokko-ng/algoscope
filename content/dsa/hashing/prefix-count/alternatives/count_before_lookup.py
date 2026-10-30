# expect: fail
# Records the current prefix before looking it up, so with k = 0 every empty run is counted too.
def solve(nums, k):
    counts = {0: 1}
    prefix = 0
    total = 0
    for x in nums:
        prefix += x
        counts[prefix] = counts.get(prefix, 0) + 1
        total += counts.get(prefix - k, 0)
    return total
