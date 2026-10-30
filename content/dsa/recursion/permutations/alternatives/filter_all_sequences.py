# expect: slow
# Brute force: build all n^n sequences of values and keep those that use every value once.
def solve(nums):
    n = len(nums)
    result = []
    seq = []

    def fill():
        if len(seq) == n:
            if len(set(seq)) == n:
                result.append([nums[i] for i in seq])
            return
        for i in range(n):
            seq.append(i)
            fill()
            seq.pop()

    fill()
    return result
