# expect: fail
# A stack instead of a queue: the first route found is not the shortest.
def solve(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    steps = {start: 0}
    stack = [start]
    while stack:
        r, c = stack.pop()
        if (r, c) == target:
            return steps[(r, c)]
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] and (nr, nc) not in steps:
                steps[(nr, nc)] = steps[(r, c)] + 1
                stack.append((nr, nc))
    return -1
