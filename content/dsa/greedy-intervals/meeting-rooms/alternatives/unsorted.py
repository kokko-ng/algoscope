# expect: fail
# Forgets to sort by start, so meetings arrive out of order and rooms are not reused.
import heapq


def solve(meetings):
    ends = []
    for start, end in meetings:
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)
