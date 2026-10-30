# expect: fail
# Off-by-one: requires reach to cover len(jumps), one square past the last index.
def solve(jumps):
    reach = 0
    for i in range(len(jumps)):
        if i > reach:
            return False
        reach = max(reach, i + jumps[i])
    return reach >= len(jumps)
