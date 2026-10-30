# expect: slow
# Scan every list head for each output value: O(nk).
def solve(lists):
    pos = [0] * len(lists)
    merged = []
    while True:
        best = -1
        for r in range(len(lists)):
            if pos[r] < len(lists[r]) and (best < 0 or lists[r][pos[r]] < lists[best][pos[best]]):
                best = r
        if best < 0:
            return merged
        merged.append(lists[best][pos[best]])
        pos[best] += 1
