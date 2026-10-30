# expect: fail
# Treats needed as a set, so a window with one "a" covers needed = ["a", "a"].
def solve(stream, needed):
    want = set(needed)
    count = {}
    covered = 0
    best = 0
    left = 0
    for right in range(len(stream)):
        item = stream[right]
        count[item] = count.get(item, 0) + 1
        if item in want and count[item] == 1:
            covered += 1
        while covered == len(want):
            if best == 0 or right - left + 1 < best:
                best = right - left + 1
            gone = stream[left]
            count[gone] -= 1
            if gone in want and count[gone] == 0:
                covered -= 1
            left += 1
    return best
