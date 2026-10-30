# expect: slow
# Repeatedly rescan from the front for any interval touching new, absorb it and start over: O(n^2).
def solve(intervals, new):
    rest = [list(x) for x in intervals]
    start, end = new
    merged = True
    while merged:
        merged = False
        for i in range(len(rest)):
            if rest[i][0] <= end and rest[i][1] >= start:
                start = min(start, rest[i][0])
                end = max(end, rest[i][1])
                rest.pop(i)
                merged = True
                break
    pos = 0
    while pos < len(rest) and rest[pos][0] < start:
        pos += 1
    rest.insert(pos, [start, end])
    return rest
