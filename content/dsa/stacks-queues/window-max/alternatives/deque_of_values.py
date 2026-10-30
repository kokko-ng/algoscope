# expect: pass
# Stores values rather than indices, keeping equal values, and expires the front by value.
from collections import deque


def solve(nums, k):
    dq = deque()
    out = []
    for i, x in enumerate(nums):
        while dq and dq[-1] < x:
            dq.pop()
        dq.append(x)
        if i >= k and dq[0] == nums[i - k]:
            dq.popleft()
        if i >= k - 1:
            out.append(dq[0])
    return out
