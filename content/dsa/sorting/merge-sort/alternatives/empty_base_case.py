# expect: fail
# Base case only stops at the empty list, so a single element splits into [] and itself forever.
def solve(values):
    if len(values) == 0:
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
    return merged + left[i:] + right[j:]
