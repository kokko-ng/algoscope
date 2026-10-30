def solve(values):
    quicksort(values, 0, len(values) - 1)


def quicksort(values, low, high):
    if low >= high:
        return
    split = partition(values, low, high)
    quicksort(values, low, split - 1)
    quicksort(values, split + 1, high)


def partition(values, low, high):
    middle = (low + high) // 2
    values[middle], values[high] = values[high], values[middle]
    pivot = values[high]
    boundary = low
    for scan in range(low, high):
        if values[scan] < pivot:
            values[boundary], values[scan] = values[scan], values[boundary]
            boundary += 1
    values[boundary], values[high] = values[high], values[boundary]
    return boundary
