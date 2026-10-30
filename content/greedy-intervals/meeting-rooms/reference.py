import heapq


def solve(meetings):
    meetings.sort()
    ends = []
    for i in range(len(meetings)):
        start, end = meetings[i]
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)
