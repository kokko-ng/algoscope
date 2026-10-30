# expect: pass
# No parent links: after the search, step back to any neighbour whose cost plus this cell's cost equals this cell's cost.
import heapq


def solve(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    inf = float("inf")
    dist = [[inf] * cols for _ in range(rows)]
    dist[start[0]][start[1]] = grid[start[0]][start[1]]
    heap = [(dist[start[0]][start[1]], start[0], start[1])]
    while heap:
        d, r, c = heapq.heappop(heap)
        if d > dist[r][c]:
            continue
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] > 0 and d + grid[nr][nc] < dist[nr][nc]:
                dist[nr][nc] = d + grid[nr][nc]
                heapq.heappush(heap, (dist[nr][nc], nr, nc))
    r, c = target
    if dist[r][c] == inf:
        return []
    path = [(r, c)]
    while (r, c) != start:
        for pr, pc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= pr < rows and 0 <= pc < cols and dist[pr][pc] + grid[r][c] == dist[r][c]:
                r, c = pr, pc
                break
        path.append((r, c))
    path.reverse()
    return path
