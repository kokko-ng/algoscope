# expect: fail
# Declares failure at the first 0 before the end, even when a longer jump clears it.
def solve(jumps):
    for i in range(len(jumps) - 1):
        if jumps[i] == 0:
            return False
    return True
