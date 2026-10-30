# expect: pass
# Iterative: an explicit stack of cells instead of the call stack.
def solve(grid, row, col, color):
    old = grid[row][col]
    if old == color:
        return
    stack = [(row, col)]
    while stack:
        r, c = stack.pop()
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]) and grid[r][c] == old:
            grid[r][c] = color
            stack.append((r + 1, c))
            stack.append((r - 1, c))
            stack.append((r, c + 1))
            stack.append((r, c - 1))
    return grid
