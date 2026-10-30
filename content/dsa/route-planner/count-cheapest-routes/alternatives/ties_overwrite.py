# expect: fail
# Uses <= when comparing totals, so a tie replaces the count instead of adding to it.
def solve(grid):
    rows, cols = len(grid), len(grid[0])
    cost = [[float("inf")] * cols for _ in range(rows)]
    ways = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                continue
            if r == 0 and c == 0:
                cost[r][c], ways[r][c] = grid[r][c], 1
                continue
            for pr, pc in ((r - 1, c), (r, c - 1)):
                if pr >= 0 and pc >= 0 and ways[pr][pc] > 0:
                    total = cost[pr][pc] + grid[r][c]
                    if total <= cost[r][c]:
                        cost[r][c], ways[r][c] = total, ways[pr][pc]
    if ways[-1][-1] == 0:
        return (-1, 0)
    return (cost[-1][-1], ways[-1][-1])
