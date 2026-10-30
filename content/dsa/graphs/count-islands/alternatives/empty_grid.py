# expect: fail
# Reads len(grid[0]) up front, which crashes on the empty grid.
def solve(grid):
    rows, cols = len(grid), len(grid[0])
    islands = 0

    def sink(r, c):
        if r < 0 or c < 0 or r >= rows or c >= cols or grid[r][c] != 1:
            return
        grid[r][c] = 0
        sink(r + 1, c)
        sink(r - 1, c)
        sink(r, c + 1)
        sink(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                islands += 1
                sink(r, c)
    return islands
