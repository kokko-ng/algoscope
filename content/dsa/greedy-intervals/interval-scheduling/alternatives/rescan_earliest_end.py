# expect: slow
# The right greedy rule without a sort: rescan every interval for the earliest end that still fits, O(n^2).
def solve(intervals):
    count = 0
    last_end = float("-inf")
    while True:
        best = None
        for start, end in intervals:
            if start >= last_end and (best is None or end < best):
                best = end
        if best is None:
            return count
        count += 1
        last_end = best
