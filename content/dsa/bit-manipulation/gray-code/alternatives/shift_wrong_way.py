# expect: fail
# Shifts left instead of right: codes grow too wide and the order is wrong.
def solve(n):
    return [i ^ (i << 1) for i in range(1 << n)]
