# expect: fail
# Greedy by start time: an early, long interval blocks several short ones.
def solve(intervals):
    intervals.sort()
    count = 0
    last_end = float("-inf")
    for start, end in intervals:
        if start >= last_end:
            count += 1
            last_end = end
    return count
