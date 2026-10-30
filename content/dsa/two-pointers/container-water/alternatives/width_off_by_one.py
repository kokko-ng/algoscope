# expect: fail
# Counts the width as j - i + 1, the number of walls, instead of the distance j - i.
def solve(heights):
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        best = max(best, min(heights[left], heights[right]) * (right - left + 1))
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    return best
