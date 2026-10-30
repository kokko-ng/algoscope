# expect: pass
# Scan from the right, moving the goal left whenever a square can jump onto it.
def solve(jumps):
    goal = len(jumps) - 1
    for i in range(len(jumps) - 2, -1, -1):
        if i + jumps[i] >= goal:
            goal = i
    return goal == 0
