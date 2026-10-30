# expect: slow
# Plain recursion without memo: every route into a cell is recomputed, exponential in the grid size.
def solve(grid):
    def cheapest(r, c):
        if r == 0 and c == 0:
            return grid[0][0]
        if r == 0:
            return grid[r][c] + cheapest(r, c - 1)
        if c == 0:
            return grid[r][c] + cheapest(r - 1, c)
        return grid[r][c] + min(cheapest(r - 1, c), cheapest(r, c - 1))

    return cheapest(len(grid) - 1, len(grid[0]) - 1)
