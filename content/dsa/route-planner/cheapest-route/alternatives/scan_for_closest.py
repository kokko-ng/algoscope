# expect: slow
# Dijkstra without a heap: scan the whole grid for the closest unsettled cell, O(V^2).
def solve(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    dist = [[float("inf")] * cols for _ in range(rows)]
    done = [[False] * cols for _ in range(rows)]
    sr, sc = start
    dist[sr][sc] = grid[sr][sc]
    while True:
        best, r, c = float("inf"), -1, -1
        for i in range(rows):
            for j in range(cols):
                if not done[i][j] and dist[i][j] < best:
                    best, r, c = dist[i][j], i, j
        if r < 0:
            return -1
        if (r, c) == target:
            return best
        done[r][c] = True
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] > 0:
                dist[nr][nc] = min(dist[nr][nc], best + grid[nr][nc])
