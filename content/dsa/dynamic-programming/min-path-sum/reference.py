def solve(grid):
    rows, cols = len(grid), len(grid[0])
    dp = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0:
                best = 0
            elif r == 0:
                best = dp[r][c - 1]
            elif c == 0:
                best = dp[r - 1][c]
            else:
                best = min(dp[r - 1][c], dp[r][c - 1])
            dp[r][c] = best + grid[r][c]
    return dp[rows - 1][cols - 1]
