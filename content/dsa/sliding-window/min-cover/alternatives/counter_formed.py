# expect: pass
# Counter tallies and a count of distinct items whose quota is met, instead of one outstanding total.
from collections import Counter


def solve(stream, needed):
    want = Counter(needed)
    have = Counter()
    formed = 0
    best = 0
    left = 0
    for right, item in enumerate(stream):
        have[item] += 1
        if have[item] == want[item]:
            formed += 1
        while formed == len(want):
            size = right - left + 1
            best = size if best == 0 else min(best, size)
            gone = stream[left]
            if have[gone] == want[gone]:
                formed -= 1
            have[gone] -= 1
            left += 1
    return best
