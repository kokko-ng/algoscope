# expect: fail
# Off-by-one: produces len(nums) - k windows, dropping the last one.
def solve(nums, k):
    result = []
    for i in range(len(nums) - k):
        best = nums[i]
        for j in range(i + 1, i + k):
            if nums[j] > best:
                best = nums[j]
        result.append(best)
    return result
