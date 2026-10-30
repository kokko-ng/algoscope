def solve(nums):
    acc = 0
    for value in nums:
        acc ^= value
    return acc
