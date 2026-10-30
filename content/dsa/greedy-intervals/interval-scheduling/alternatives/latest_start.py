# expect: pass
# The mirror-image greedy: sort by start and keep the latest-starting interval first, scanning from the right.
def solve(intervals):
    order = sorted(intervals)
    count = 0
    next_start = float("inf")
    for i in range(len(order) - 1, -1, -1):
        start, end = order[i]
        if end <= next_start:
            count += 1
            next_start = start
    return count
