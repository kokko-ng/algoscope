# expect: pass
# Non-shrinking window: slide the left edge by one instead of looping, so the size only ever grows.
def solve(bits, k):
    zeros = 0
    left = 0
    for right in range(len(bits)):
        if bits[right] == 0:
            zeros += 1
        if zeros > k:
            if bits[left] == 0:
                zeros -= 1
            left += 1
    return len(bits) - left
