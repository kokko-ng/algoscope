def solve(jumps):
    reach = 0
    for i in range(len(jumps)):
        if i > reach:
            return False
        reach = max(reach, i + jumps[i])
    return True
