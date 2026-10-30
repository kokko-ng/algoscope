# expect: fail
# Returns the last entry of length instead of the largest one.
def solve(nums):
    if not nums:
        return 0
    length = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i] and length[j] + 1 > length[i]:
                length[i] = length[j] + 1
    return length[-1]
