# expect: pass
# Literal reading: index the last position of every value first, then scan; returns a tuple.
def solve(nums, target):
    last = {}
    for i, x in enumerate(nums):
        last[x] = i
    for i, x in enumerate(nums):
        j = last.get(target - x, -1)
        if j > i:
            return (i, j)
    return (-1, -1)
