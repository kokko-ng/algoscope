# expect: fail
# Follows the links back from the target but forgets to reverse, so the route runs target to start.
import heapq


def solve(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    dist = {start: grid[start[0]][start[1]]}
    came_from = {}
    heap = [(dist[start], start)]
    while heap:
        d, cell = heapq.heappop(heap)
        if cell == target:
            break
        if d > dist[cell]:
            continue
        r, c = cell
        for nxt in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            nr, nc = nxt
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and grid[nr][nc] > 0
                and d + grid[nr][nc] < dist.get(nxt, float("inf"))
            ):
                dist[nxt] = d + grid[nr][nc]
                came_from[nxt] = cell
                heapq.heappush(heap, (dist[nxt], nxt))
    if target not in dist:
        return []
    path = [target]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    return path
