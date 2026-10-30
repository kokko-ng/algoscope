from collections import deque


def solve(nums, k):
    candidates = deque()
    result = []
    for i in range(len(nums)):
        start = i - k + 1
        if candidates and candidates[0] < start:
            candidates.popleft()
        while candidates and nums[candidates[-1]] <= nums[i]:
            candidates.pop()
        candidates.append(i)
        if start >= 0:
            result.append(nums[candidates[0]])
    return result
