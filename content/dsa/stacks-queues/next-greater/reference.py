def solve(nums):
    result = [-1] * len(nums)
    waiting = []
    for i in range(len(nums)):
        while waiting and nums[waiting[-1]] < nums[i]:
            result[waiting.pop()] = nums[i]
        waiting.append(i)
    return result
