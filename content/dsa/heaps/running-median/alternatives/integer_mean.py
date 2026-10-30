# expect: fail
# Uses // for the even-count mean, so 2 and 3 give 2 instead of 2.5.
import heapq


def solve(stream):
    low, high, medians = [], [], []
    for value in stream:
        heapq.heappush(low, -value)
        heapq.heappush(high, -heapq.heappop(low))
        if len(high) > len(low):
            heapq.heappush(low, -heapq.heappop(high))
        if len(low) > len(high):
            medians.append(-low[0])
        else:
            medians.append((-low[0] + high[0]) // 2)
    return medians
