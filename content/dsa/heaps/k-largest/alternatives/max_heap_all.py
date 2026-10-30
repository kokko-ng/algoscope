# expect: pass
# Heapify every value negated, then pop k times: a different heap technique.
import heapq


def solve(nums, k):
    heap = [-x for x in nums]
    heapq.heapify(heap)
    return [-heapq.heappop(heap) for _ in range(k)]
