def solve(values, max_value):
    counts = [0] * (max_value + 1)
    for value in values:
        counts[value] += 1
    result = []
    for value in range(max_value + 1):
        for _ in range(counts[value]):
            result.append(value)
    return result
