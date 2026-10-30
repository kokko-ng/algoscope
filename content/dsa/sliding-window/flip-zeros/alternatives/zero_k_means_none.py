# expect: fail
# Shrinks while zeros >= k, so the window holds fewer than k zeros and k = 0 never sees a run of 1s.
def solve(bits, k):
    zeros = 0
    left = 0
    best = 0
    for right in range(len(bits)):
        if bits[right] == 0:
            zeros += 1
        while zeros >= k and left <= right:
            if bits[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
