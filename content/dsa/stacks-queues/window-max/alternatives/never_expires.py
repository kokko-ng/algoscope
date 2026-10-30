# expect: fail
# Never drops the front candidate when it leaves the window, so an old maximum lingers.
from collections import deque


def solve(nums, k):
    candidates = deque()
    result = []
    for i in range(len(nums)):
        while candidates and nums[candidates[-1]] <= nums[i]:
            candidates.pop()
        candidates.append(i)
        if i - k + 1 >= 0:
            result.append(nums[candidates[0]])
    return result
