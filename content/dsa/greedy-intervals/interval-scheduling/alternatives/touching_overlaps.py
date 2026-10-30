# expect: fail
# Off-by-one: requires start > last_end, so intervals that only touch are treated as overlapping.
def solve(intervals):
    intervals.sort(key=lambda pair: pair[1])
    count = 0
    last_end = float("-inf")
    for start, end in intervals:
        if start > last_end:
            count += 1
            last_end = end
    return count
