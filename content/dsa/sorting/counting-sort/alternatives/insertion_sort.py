# expect: slow
# Insertion sort into a copy: correct, but O(n^2) comparisons.
def solve(values, max_value):
    result = list(values)
    for i in range(1, len(result)):
        current = result[i]
        j = i - 1
        while j >= 0 and result[j] > current:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result
