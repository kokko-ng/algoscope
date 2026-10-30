def solve(intervals):
    intervals.sort()
    merged = []
    for i in range(len(intervals)):
        start, end = intervals[i]
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
