from collections import deque


def solve(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    steps = [[-1] * cols for _ in range(rows)]
    sr, sc = start
    steps[sr][sc] = 0
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        if (r, c) == target:
            return steps[r][c]
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] and steps[nr][nc] < 0:
                steps[nr][nc] = steps[r][c] + 1
                queue.append((nr, nc))
    return -1
