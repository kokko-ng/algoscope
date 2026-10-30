# expect: fail
# Writes each value that occurs once, losing repeats.
def solve(values, max_value):
    present = [False] * (max_value + 1)
    for value in values:
        present[value] = True
    return [value for value in range(max_value + 1) if present[value]]
