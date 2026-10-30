# expect: fail
# Off-by-one: checks c + 1 <= len instead of <, so it reads past the end of a list.
import heapq


def solve(lists):
    merged = []
    frontier = [(row[0], r, 0) for r, row in enumerate(lists) if row]
    heapq.heapify(frontier)
    while frontier:
        value, r, c = heapq.heappop(frontier)
        merged.append(value)
        if c + 1 <= len(lists[r]):
            heapq.heappush(frontier, (lists[r][c + 1], r, c + 1))
    return merged
