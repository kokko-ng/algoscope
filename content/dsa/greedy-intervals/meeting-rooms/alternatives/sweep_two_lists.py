# expect: pass
# Sweep line: sorted starts and sorted ends walked with two pointers, no heap.
def solve(meetings):
    starts = sorted(m[0] for m in meetings)
    ends = sorted(m[1] for m in meetings)
    rooms = most = 0
    j = 0
    for s in starts:
        while j < len(ends) and ends[j] <= s:
            rooms -= 1
            j += 1
        rooms += 1
        most = max(most, rooms)
    return most
