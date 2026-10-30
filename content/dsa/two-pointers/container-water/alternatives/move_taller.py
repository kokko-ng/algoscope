# expect: fail
# Moves the pointer at the taller wall, discarding walls that could still be part of the best pair.
def solve(heights):
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        best = max(best, min(heights[left], heights[right]) * (right - left))
        if heights[left] > heights[right]:
            left += 1
        else:
            right -= 1
    return best
