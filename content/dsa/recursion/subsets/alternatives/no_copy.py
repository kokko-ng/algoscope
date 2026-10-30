# expect: fail
# Records `chosen` itself instead of a copy, so every saved subset ends up empty.
def solve(nums):
    result = []
    chosen = []

    def explore(i):
        if i == len(nums):
            result.append(chosen)
            return
        chosen.append(nums[i])
        explore(i + 1)
        chosen.pop()
        explore(i + 1)

    explore(0)
    return result
