# expect: fail
# Replaces the top when the new value is smaller, keeping a mix rather than the k largest.
import heapq


def solve(nums, k):
    kept = []
    if k == 0:
        return kept
    for x in nums:
        if len(kept) < k:
            heapq.heappush(kept, x)
        elif x < kept[0]:
            heapq.heapreplace(kept, x)
    return kept
