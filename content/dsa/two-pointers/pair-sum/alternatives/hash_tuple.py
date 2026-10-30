# expect: pass
# Literal reading: a hash map of seen values, returning a tuple and possibly a different valid pair.
def solve(nums, target):
    seen = {}
    for j, x in enumerate(nums):
        if target - x in seen:
            return (seen[target - x], j)
        seen[x] = j
    return (-1, -1)
