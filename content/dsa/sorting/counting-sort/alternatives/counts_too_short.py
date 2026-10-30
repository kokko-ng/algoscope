# expect: fail
# Off-by-one: max_value slots instead of max_value + 1, so the largest value has nowhere to go.
def solve(values, max_value):
    counts = [0] * max_value
    for value in values:
        counts[value] += 1
    result = []
    for value in range(max_value):
        for _ in range(counts[value]):
            result.append(value)
    return result
