# expect: pass
# A*: order the heap by cost so far plus the Manhattan distance left. Every cell costs at least 1, so the estimate never overshoots.
import heapq


def solve(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    tr, tc = target
    best = {start: grid[start[0]][start[1]]}
    heap = [(best[start] + abs(start[0] - tr) + abs(start[1] - tc), best[start], start)]
    while heap:
        _, d, cell = heapq.heappop(heap)
        if cell == target:
            return d
        if d > best[cell]:
            continue
        r, c = cell
        for nxt in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            nr, nc = nxt
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] > 0:
                nd = d + grid[nr][nc]
                if nd < best.get(nxt, float("inf")):
                    best[nxt] = nd
                    heapq.heappush(heap, (nd + abs(nr - tr) + abs(nc - tc), nd, nxt))
    return -1
