# expect: pass
# Divide and conquer: merge lists in pairs, halving their number each round.
def solve(lists):
    def merge_two(a, b):
        out = []
        i = j = 0
        while i < len(a) and j < len(b):
            if a[i] <= b[j]:
                out.append(a[i])
                i += 1
            else:
                out.append(b[j])
                j += 1
        while i < len(a):
            out.append(a[i])
            i += 1
        while j < len(b):
            out.append(b[j])
            j += 1
        return out

    rows = list(lists)
    if not rows:
        return []
    while len(rows) > 1:
        nxt = []
        for i in range(0, len(rows) - 1, 2):
            nxt.append(merge_two(rows[i], rows[i + 1]))
        if len(rows) % 2:
            nxt.append(rows[-1])
        rows = nxt
    return rows[0]
