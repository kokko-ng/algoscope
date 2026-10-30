def solve(n):
    codes = []
    for i in range(1 << n):
        code = i ^ (i >> 1)
        codes.append(code)
    return codes
