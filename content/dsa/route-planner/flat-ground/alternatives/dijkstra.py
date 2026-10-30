# expect: slow
# Correct, but a heap ordered by cost does extra O(log n) work that a FIFO queue gets for free.
import heapq


def solve(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, cell = heapq.heappop(heap)
        if cell == target:
            return d
        if d > dist[cell]:
            continue
        r, c = cell
        for nxt in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            nr, nc = nxt
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc]:
                if d + 1 < dist.get(nxt, float("inf")):
                    dist[nxt] = d + 1
                    heapq.heappush(heap, (d + 1, nxt))
    return -1
