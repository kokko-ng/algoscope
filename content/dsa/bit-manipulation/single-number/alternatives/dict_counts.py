# expect: pass
# Counts in a dict: O(n) time, but O(n) memory.
def solve(nums):
    counts = {}
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
    for value, seen in counts.items():
        if seen == 1:
            return value
