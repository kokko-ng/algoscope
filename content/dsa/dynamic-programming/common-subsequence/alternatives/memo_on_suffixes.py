# expect: slow
# Memoised recursion keyed on the suffix strings themselves: every call copies both suffixes.
def solve(a, b):
    memo = {}

    def lcs(x, y):
        if not x or not y:
            return 0
        key = (x, y)
        if key in memo:
            return memo[key]
        if x[0] == y[0]:
            out = 1 + lcs(x[1:], y[1:])
        else:
            out = max(lcs(x[1:], y), lcs(x, y[1:]))
        memo[key] = out
        return out

    return lcs(a, b)
