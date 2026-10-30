def solve(colours):
    low, mid, high = 0, 0, len(colours) - 1
    while mid <= high:
        if colours[mid] == 0:
            colours[low], colours[mid] = colours[mid], colours[low]
            low += 1
            mid += 1
        elif colours[mid] == 1:
            mid += 1
        else:
            colours[mid], colours[high] = colours[high], colours[mid]
            high -= 1
