# expect: slow
# Sweep the whole grid until no cell changes; a winding region needs one sweep per bend.
def solve(grid, row, col, color):
    old = grid[row][col]
    if old == color:
        return
    rows, cols = len(grid), len(grid[0])
    filled = [[False] * cols for _ in range(rows)]
    filled[row][col] = True
    changed = True
    while changed:
        changed = False
        for r in range(rows):
            for c in range(cols):
                if filled[r][c] or grid[r][c] != old:
                    continue
                if (
                    (r > 0 and filled[r - 1][c])
                    or (r + 1 < rows and filled[r + 1][c])
                    or (c > 0 and filled[r][c - 1])
                    or (c + 1 < cols and filled[r][c + 1])
                ):
                    filled[r][c] = True
                    changed = True
    for r in range(rows):
        for c in range(cols):
            if filled[r][c]:
                grid[r][c] = color
