# expect: fail
# Greedy: always step to the cheaper of right and down, which can walk into an expensive corner.
def solve(grid):
    rows, cols = len(grid), len(grid[0])
    r = c = 0
    total = grid[0][0]
    while r < rows - 1 or c < cols - 1:
        if r == rows - 1:
            c += 1
        elif c == cols - 1:
            r += 1
        elif grid[r + 1][c] <= grid[r][c + 1]:
            r += 1
        else:
            c += 1
        total += grid[r][c]
    return total
