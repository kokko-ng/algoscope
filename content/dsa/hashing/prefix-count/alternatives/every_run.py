# expect: slow
# Sum every run from every start: correct, but O(n^2).
def solve(nums, k):
    total = 0
    for a in range(len(nums)):
        s = 0
        for b in range(a, len(nums)):
            s += nums[b]
            if s == k:
                total += 1
    return total
