# expect: fail
# Also floods diagonally, joining islands that only touch at a corner.
def solve(grid):
    islands = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 1:
                islands += 1
                sink(grid, r, c)
    return islands


def sink(grid, r, c):
    if r < 0 or c < 0 or r >= len(grid) or c >= len(grid[0]) or grid[r][c] != 1:
        return
    grid[r][c] = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                sink(grid, r + dr, c + dc)
