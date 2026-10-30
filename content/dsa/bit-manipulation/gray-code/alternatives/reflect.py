# expect: pass
# Reflect and prefix: the codes for width k + 1 are the width-k codes, then the same codes reversed with bit k set.
def solve(n):
    codes = [0]
    for bit in range(n):
        codes += [code | (1 << bit) for code in reversed(codes)]
    return codes
