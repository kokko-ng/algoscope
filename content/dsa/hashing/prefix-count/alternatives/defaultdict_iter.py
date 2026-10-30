# expect: pass
# A defaultdict and direct iteration over values instead of indices and get().
from collections import defaultdict


def solve(nums, k):
    seen = defaultdict(int)
    seen[0] = 1
    prefix = 0
    runs = 0
    for x in nums:
        prefix += x
        runs += seen[prefix - k]
        seen[prefix] += 1
    return runs
