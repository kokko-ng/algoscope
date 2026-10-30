# expect: fail
# Places new only when a later interval appears, so it is lost when it belongs at the end.
def solve(intervals, new):
    out = []
    start, end = new
    placed = False
    for s, e in intervals:
        if e < start:
            out.append([s, e])
        elif s > end:
            if not placed:
                out.append([start, end])
                placed = True
            out.append([s, e])
        else:
            start, end = min(start, s), max(end, e)
    return out
