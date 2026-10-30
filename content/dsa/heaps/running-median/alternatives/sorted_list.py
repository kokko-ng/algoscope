# expect: slow
# Keep a sorted list by shifting each new value into place: O(n) per value.
def solve(stream):
    values = []
    medians = []
    for value in stream:
        values.append(value)
        i = len(values) - 1
        while i > 0 and values[i - 1] > value:
            values[i] = values[i - 1]
            i -= 1
        values[i] = value
        m = len(values) // 2
        if len(values) % 2:
            medians.append(values[m])
        else:
            medians.append((values[m - 1] + values[m]) / 2)
    return medians
