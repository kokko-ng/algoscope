# expect: pass
# Top-down recursion on indices with a memo table instead of a bottom-up fill.
def solve(a, b):
    memo = [[-1] * (len(b) + 1) for _ in range(len(a) + 1)]

    def lcs(i, j):
        if i == len(a) or j == len(b):
            return 0
        if memo[i][j] < 0:
            if a[i] == b[j]:
                memo[i][j] = 1 + lcs(i + 1, j + 1)
            else:
                memo[i][j] = max(lcs(i + 1, j), lcs(i, j + 1))
        return memo[i][j]

    return lcs(0, 0)
