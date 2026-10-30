# expect: pass
# Scan from the right with a stack of candidate values, returning a tuple.
def solve(nums):
    result = [-1] * len(nums)
    stack = []
    for i in range(len(nums) - 1, -1, -1):
        while stack and stack[-1] <= nums[i]:
            stack.pop()
        if stack:
            result[i] = stack[-1]
        stack.append(nums[i])
    return tuple(result)
