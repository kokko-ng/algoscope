# expect: pass
# Iterative literal reading: each mask from 0 to 2^n - 1 picks one subset.
def solve(nums):
    n = len(nums)
    result = []
    for mask in range(1 << n):
        result.append([nums[i] for i in range(n) if mask >> i & 1])
    return result
