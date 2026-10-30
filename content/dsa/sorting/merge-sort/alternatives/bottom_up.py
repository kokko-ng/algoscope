# expect: pass
# Bottom-up merge sort: iterative passes merging runs of width 1, 2, 4, ... into a new list.
def solve(values):
    src = list(values)
    width = 1
    while width < len(src):
        dst = []
        for lo in range(0, len(src), 2 * width):
            mid = lo + width
            hi = lo + 2 * width
            if mid > len(src):
                mid = len(src)
            if hi > len(src):
                hi = len(src)
            i, j = lo, mid
            while i < mid and j < hi:
                if src[i] <= src[j]:
                    dst.append(src[i])
                    i += 1
                else:
                    dst.append(src[j])
                    j += 1
            while i < mid:
                dst.append(src[i])
                i += 1
            while j < hi:
                dst.append(src[j])
                j += 1
        src = dst
        width *= 2
    return src
