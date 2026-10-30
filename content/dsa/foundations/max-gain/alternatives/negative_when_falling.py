# expect: fail
# Starts best at -infinity, so falling readings return a negative rise instead of 0.
def solve(readings):
    if len(readings) < 2:
        return 0
    best = float("-inf")
    low = readings[0]
    for j in range(1, len(readings)):
        best = max(best, readings[j] - low)
        low = min(low, readings[j])
    return best
