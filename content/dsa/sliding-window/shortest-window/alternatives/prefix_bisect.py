# expect: pass
# Prefix sums plus binary search for each end: a different valid technique, O(n log n).
import bisect


def solve(nums, target):
    prefix = [0]
    for x in nums:
        prefix.append(prefix[-1] + x)
    best = 0
    for end in range(1, len(prefix)):
        start = bisect.bisect_right(prefix, prefix[end] - target, 0, end) - 1
        if start >= 0:
            length = end - start
            if best == 0 or length < best:
                best = length
    return best
