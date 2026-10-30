# expect: slow
# Try every pair of walls: correct, but O(n^2).
def solve(heights):
    best = 0
    for i in range(len(heights)):
        for j in range(i + 1, len(heights)):
            best = max(best, min(heights[i], heights[j]) * (j - i))
    return best
