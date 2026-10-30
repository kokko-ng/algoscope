# expect: fail
# Breadth-first search finds the route with the fewest moves, not the cheapest one.
from collections import deque


def solve(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    cost = {start: grid[start[0]][start[1]]}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        if (r, c) == target:
            return cost[(r, c)]
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] > 0 and (nr, nc) not in cost:
                cost[(nr, nc)] = cost[(r, c)] + grid[nr][nc]
                queue.append((nr, nc))
    return -1
