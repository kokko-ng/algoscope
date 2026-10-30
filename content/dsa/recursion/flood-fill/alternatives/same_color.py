# expect: fail
# Skips the old == color guard: recoloring no longer marks cells, so the recursion never ends.
def solve(grid, row, col, color):
    old = grid[row][col]

    def fill(r, c):
        if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]):
            return
        if grid[r][c] != old:
            return
        grid[r][c] = color
        fill(r + 1, c)
        fill(r - 1, c)
        fill(r, c + 1)
        fill(r, c - 1)

    fill(row, col)
