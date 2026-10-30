# expect: slow
# From every start, add values until the sum reaches target: correct, but O(n^2).
def solve(nums, target):
    best = 0
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            if total >= target:
                if best == 0 or j - i + 1 < best:
                    best = j - i + 1
                break
    return best
