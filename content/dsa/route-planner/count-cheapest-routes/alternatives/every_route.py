# expect: slow
# Walks every route recursively: exponential in the grid size.
def solve(grid):
    rows, cols = len(grid), len(grid[0])
    best = [float("inf"), 0]

    def walk(r, c, spent):
        if r >= rows or c >= cols or grid[r][c] == 0:
            return
        spent += grid[r][c]
        if (r, c) == (rows - 1, cols - 1):
            if spent < best[0]:
                best[0], best[1] = spent, 1
            elif spent == best[0]:
                best[1] += 1
            return
        walk(r + 1, c, spent)
        walk(r, c + 1, spent)

    walk(0, 0, 0)
    return (-1, 0) if best[1] == 0 else (best[0], best[1])
