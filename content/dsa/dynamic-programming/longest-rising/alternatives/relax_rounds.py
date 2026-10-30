# expect: slow
# Relax every pair in rounds, ends visited right to left, until no length improves: one O(n^2) round per step of the answer.
def solve(nums):
    if not nums:
        return 0
    length = [1] * len(nums)
    changed = True
    while changed:
        changed = False
        for i in range(len(nums) - 1, -1, -1):
            for j in range(i):
                if nums[j] < nums[i] and length[j] + 1 > length[i]:
                    length[i] = length[j] + 1
                    changed = True
    return max(length)
