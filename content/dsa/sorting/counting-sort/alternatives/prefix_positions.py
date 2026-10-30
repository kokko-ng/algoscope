# expect: pass
# Stable counting sort: prefix sums give each value's start position in a preallocated output.
def solve(values, max_value):
    counts = [0] * (max_value + 1)
    for value in values:
        counts[value] += 1
    start = 0
    for v in range(max_value + 1):
        counts[v], start = start, start + counts[v]
    result = [0] * len(values)
    for value in values:
        result[counts[value]] = value
        counts[value] += 1
    return result
