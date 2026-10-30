# expect: slow
# From every start, grow until the tally covers needed, rechecking every needed item each time.
def solve(stream, needed):
    want = {}
    for item in needed:
        want[item] = want.get(item, 0) + 1
    best = 0
    for i in range(len(stream)):
        have = {}
        for j in range(i, len(stream)):
            have[stream[j]] = have.get(stream[j], 0) + 1
            if all(have.get(item, 0) >= count for item, count in want.items()):
                if best == 0 or j - i + 1 < best:
                    best = j - i + 1
                break
    return best
