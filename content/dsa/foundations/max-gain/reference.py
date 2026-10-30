def solve(readings):
    best = 0
    if not readings:
        return best
    low = readings[0]
    for j in range(1, len(readings)):
        best = max(best, readings[j] - low)
        low = min(low, readings[j])
    return best
