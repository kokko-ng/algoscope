# expect: fail
# Sorts and checks pairs, but never looks at the last element, so a largest single value is missed.
def solve(nums):
    ordered = sorted(nums)
    for i in range(0, len(ordered) - 1, 2):
        if ordered[i] != ordered[i + 1]:
            return ordered[i]
    return None
