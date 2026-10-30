def solve(bits, k):
    zeros = 0
    left = 0
    best = 0
    for right in range(len(bits)):
        if bits[right] == 0:
            zeros += 1
        while zeros > k:
            if bits[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
