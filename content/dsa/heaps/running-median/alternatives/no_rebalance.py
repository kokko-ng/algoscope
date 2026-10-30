# expect: fail
# Routes each value to a half but never rebalances, so the halves drift apart in size.
import heapq


def solve(stream):
    low, high, medians = [], [], []
    for value in stream:
        if not low or value <= -low[0]:
            heapq.heappush(low, -value)
        else:
            heapq.heappush(high, value)
        if len(low) > len(high):
            medians.append(-low[0])
        elif len(high) > len(low):
            medians.append(high[0])
        else:
            medians.append((-low[0] + high[0]) / 2)
    return medians
