# expect: pass
# Top-down: best (cost, count) from each cell to the bottom-right corner, memoised.
def solve(grid):
    rows, cols = len(grid), len(grid[0])
    memo = {}

    def best(r, c):
        if r >= rows or c >= cols or grid[r][c] == 0:
            return (float("inf"), 0)
        if (r, c) == (rows - 1, cols - 1):
            return (grid[r][c], 1)
        if (r, c) not in memo:
            down, right = best(r + 1, c), best(r, c + 1)
            low = min(down[0], right[0])
            count = (down[1] if down[0] == low else 0) + (right[1] if right[0] == low else 0)
            memo[(r, c)] = (low + grid[r][c], count)
        return memo[(r, c)]

    cost, count = best(0, 0)
    return (-1, 0) if count == 0 else (cost, count)
