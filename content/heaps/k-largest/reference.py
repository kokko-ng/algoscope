import heapq


def solve(nums, k):
    kept = []
    if k == 0:
        return kept
    for i in range(len(nums)):
        if len(kept) < k:
            heapq.heappush(kept, nums[i])
        elif nums[i] > kept[0]:
            heapq.heapreplace(kept, nums[i])
    return kept
