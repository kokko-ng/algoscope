# expect: pass
# Different tie rule: on equal heights both walls are spent, so both pointers move.
def solve(heights):
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        h = min(heights[left], heights[right])
        best = max(best, h * (right - left))
        if heights[left] == heights[right]:
            left += 1
            right -= 1
        elif heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    return best
