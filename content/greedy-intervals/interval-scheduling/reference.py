def solve(intervals):
    intervals.sort(key=lambda pair: pair[1])
    count = 0
    last_end = float("-inf")
    for i in range(len(intervals)):
        start, end = intervals[i]
        if start >= last_end:
            count += 1
            last_end = end
    return count
