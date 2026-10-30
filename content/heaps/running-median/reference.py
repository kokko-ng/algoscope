import heapq


def solve(stream):
    low = []
    high = []
    medians = []
    for value in stream:
        heapq.heappush(low, -value)
        heapq.heappush(high, -heapq.heappop(low))
        if len(high) > len(low):
            heapq.heappush(low, -heapq.heappop(high))
        if len(low) > len(high):
            medians.append(-low[0])
        else:
            medians.append((-low[0] + high[0]) / 2)
    return medians
