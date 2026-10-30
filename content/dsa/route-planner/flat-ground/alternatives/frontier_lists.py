# expect: pass
# Level by level with two lists: the current frontier and the next one.
def solve(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    seen[start[0]][start[1]] = True
    frontier = [start]
    moves = 0
    while frontier:
        nxt = []
        for r, c in frontier:
            if (r, c) == target:
                return moves
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] and not seen[nr][nc]:
                    seen[nr][nc] = True
                    nxt.append((nr, nc))
        frontier = nxt
        moves += 1
    return -1
