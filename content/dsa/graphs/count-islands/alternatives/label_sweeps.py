# expect: slow
# Give every land cell a label, then sweep the grid copying the smallest neighbour label until stable.
def solve(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    label = [[r * cols + c if grid[r][c] == 1 else -1 for c in range(cols)] for r in range(rows)]
    changed = True
    while changed:
        changed = False
        for r in range(rows):
            for c in range(cols):
                if label[r][c] < 0:
                    continue
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and 0 <= label[nr][nc] < label[r][c]:
                        label[r][c] = label[nr][nc]
                        changed = True
    count = 0
    for r in range(rows):
        for c in range(cols):
            if label[r][c] == r * cols + c:
                count += 1
    return count
