# expect: pass
# Breadth-first search with a seen set, leaving the grid unchanged.
from collections import deque


def solve(grid):
    seen = set()
    islands = 0
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] != 1 or (r, c) in seen:
                continue
            islands += 1
            seen.add((r, c))
            queue = deque([(r, c)])
            while queue:
                y, x = queue.popleft()
                for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] == 1 and (ny, nx) not in seen:
                        seen.add((ny, nx))
                        queue.append((ny, nx))
    return islands
