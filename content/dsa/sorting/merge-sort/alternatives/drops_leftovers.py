# expect: fail
# The merge stops when either half runs out and forgets to copy what is left of the other.
def solve(values):
    if len(values) <= 1:
        return values
    middle = len(values) // 2
    left = solve(values[:middle])
    right = solve(values[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    return merged
