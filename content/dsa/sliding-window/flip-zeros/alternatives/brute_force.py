# expect: slow
# Count zeros in every window: correct, but O(n^2).
def solve(bits, k):
    best = 0
    for i in range(len(bits)):
        zeros = 0
        for j in range(i, len(bits)):
            if bits[j] == 0:
                zeros += 1
            if zeros <= k:
                best = max(best, j - i + 1)
    return best
