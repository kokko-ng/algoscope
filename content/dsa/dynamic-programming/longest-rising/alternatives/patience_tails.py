# expect: pass
# Patience sorting: tails[k] is the smallest tail of a rising run of length k + 1. O(n log n).
from bisect import bisect_left


def solve(nums):
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
