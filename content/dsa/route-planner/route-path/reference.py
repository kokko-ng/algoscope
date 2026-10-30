import heapq


def solve(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    dist = [[float("inf")] * cols for _ in range(rows)]
    came_from = [[None] * cols for _ in range(rows)]
    sr, sc = start
    dist[sr][sc] = grid[sr][sc]
    heap = [(dist[sr][sc], sr, sc)]
    while heap:
        d, r, c = heapq.heappop(heap)
        if (r, c) == target:
            break
        if d > dist[r][c]:
            continue
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] > 0:
                if d + grid[nr][nc] < dist[nr][nc]:
                    dist[nr][nc] = d + grid[nr][nc]
                    came_from[nr][nc] = (r, c)
                    heapq.heappush(heap, (dist[nr][nc], nr, nc))
    tr, tc = target
    if dist[tr][tc] == float("inf"):
        return []
    path = [target]
    while path[-1] != start:
        r, c = path[-1]
        path.append(came_from[r][c])
    path.reverse()
    return path
