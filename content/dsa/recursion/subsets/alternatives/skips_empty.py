# expect: fail
# Only records non-empty subsets, dropping the empty one the statement asks for.
def solve(nums):
    result = []
    chosen = []

    def explore(i):
        if i == len(nums):
            if chosen:
                result.append(chosen[:])
            return
        chosen.append(nums[i])
        explore(i + 1)
        chosen.pop()
        explore(i + 1)

    explore(0)
    return result
