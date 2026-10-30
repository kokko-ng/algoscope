# expect: fail
# No k == 0 guard: the scan reads kept[0] from an empty heap.
import heapq


def solve(nums, k):
    kept = []
    for x in nums:
        if len(kept) < k:
            heapq.heappush(kept, x)
        elif x > kept[0]:
            heapq.heapreplace(kept, x)
    return kept
