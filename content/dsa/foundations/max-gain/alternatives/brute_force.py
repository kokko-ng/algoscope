# expect: slow
# Compare every pair: correct, but O(n^2).
def solve(readings):
    best = 0
    for i in range(len(readings)):
        for j in range(i + 1, len(readings)):
            best = max(best, readings[j] - readings[i])
    return best
