# expect: pass
# Different technique: permute the rest, then insert the first value at every position.
def solve(nums):
    if not nums:
        return [[]]
    first = nums[0]
    result = []
    for rest in solve(nums[1:]):
        for pos in range(len(rest) + 1):
            result.append(rest[:pos] + [first] + rest[pos:])
    return result
