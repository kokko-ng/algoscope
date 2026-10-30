# expect: slow
# Naive pivot: always the last element, which the statement warns degrades to O(n^2) on sorted input.
def solve(values):
    quicksort(values, 0, len(values) - 1)


def quicksort(values, low, high):
    if low >= high:
        return
    pivot = values[high]
    boundary = low
    for scan in range(low, high):
        if values[scan] < pivot:
            values[boundary], values[scan] = values[scan], values[boundary]
            boundary += 1
    values[boundary], values[high] = values[high], values[boundary]
    quicksort(values, low, boundary - 1)
    quicksort(values, boundary + 1, high)
