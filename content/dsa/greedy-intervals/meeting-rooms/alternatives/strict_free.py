# expect: fail
# Off-by-one: a room is reused only when it ended strictly before the start, not at the same moment.
import heapq


def solve(meetings):
    meetings.sort()
    ends = []
    for start, end in meetings:
        if ends and ends[0] < start:
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)
