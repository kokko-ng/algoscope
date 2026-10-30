# expect: fail
# Pads the table with a zero border instead of handling the first row and column, so min() takes a free 0.
def solve(grid):
    rows, cols = len(grid), len(grid[0])
    dp = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            dp[r][c] = grid[r - 1][c - 1] + min(dp[r - 1][c], dp[r][c - 1])
    return dp[rows][cols]
